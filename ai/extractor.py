# ai/extractor.py

import json
import re
import requests

from config import OLLAMA_BASE_URL, LOCAL_TEXT_MODEL


EXTRACTION_SCHEMA_DESCRIPTION = """
Return a JSON object with EXACTLY these fields:
{
  "first_name": string or null,
  "middle_name": string or null,
  "last_name": string or null,
  "birth_name": string or null,
  "gender": string or null,
  "marital_status": string or null,
  "date_of_birth": string or null,
  "place_of_birth": string or null,
  "country_of_birth": string or null,
  "nationality": string or null,
  "id_number": string or null,
  "passport_number": string or null,
  "street_and_number": string or null,
  "zip_code": string or null,
  "city": string or null,
  "country": string or null,
  "iban": string or null,
  "bic": string or null,
  "bank_name": string or null,
  "account_owner": string or null,
  "steuer_id": string or null,
  "sozialversicherung": string or null,
  "health_insurance_name": string or null,
  "health_insurance_number": string or null,
  "phone": string or null,
  "email": string or null,
  "confidence": {
    "first_name": "high|medium|low|not_found",
    "last_name": "high|medium|low|not_found",
    "date_of_birth": "high|medium|low|not_found",
    "iban": "high|medium|low|not_found",
    "steuer_id": "high|medium|low|not_found"
  },
  "warnings": [],
  "extraction_notes": string or null
}

German field name mappings:
  Familienname / Nachname / Familtenname      -> last_name
  Geburtsname / Geborene / Geburtsnam        -> birth_name   (maiden/birth surname, NOT place of birth, NOT last_name)
  Vorname / Vomame / Vornaine / Vomname      -> first_name   (OCR often misreads Vorname as Vomame)
  Zweiter Vorname / Mittelname               -> middle_name
  Geburtsdatum / Geb.datum                   -> date_of_birth
  Geburtsort / Gebunsort / Geburtsoit       -> place_of_birth  (city/town where born, NOT Geburtsname)
  Geburtsland / Land der Geburt             -> country_of_birth
  Staatsangehoerigkeit / Staatsangeh        -> nationality
  Familienstand                              -> marital_status
  Geschlecht                                 -> gender
  Personalausweisnummer / Ausweis-Nr.       -> id_number
  Reisepassnummer / Pass-Nr.                -> passport_number
  Strasse / Anschrift / Anschnift           -> street_and_number
  PLZ                                        -> zip_code
  Ort / Wohnort                             -> city
  Land                                       -> country

OCR error tolerance:
  The text may contain OCR mistakes. Common patterns:
  - "rn" rendered as "m"  (Vorname -> Vomame, Geburtsname -> Gebutrsname)
  - Umlauts replaced with ? or removed (ae/oe/ue are valid substitutes)
  - Numbers mixed with letters (0/O, 1/l)
  Match field labels by approximate spelling and position, not exact match.

CRITICAL rules:
- Familienname (last_name) and Geburtsname (birth_name) are DIFFERENT fields.
  Put Familienname in last_name and Geburtsname in birth_name.
  Never put Geburtsname into last_name unless Familienname is absent.
- Geburtsort (place_of_birth) = city/town where the person was BORN.
  Geburtsname = the SURNAME the person was born with (maiden name). Completely different.
- place_of_birth is NOT the current city. city is the current residential city.
- gender: use the exact word from the document (e.g. "maennlich", "weiblich", "divers").
- marital_status: use the exact word from the document (e.g. "Verheiratet", "ledig").
- date_of_birth: DD.MM.YYYY format. Convert if necessary.
- IBAN: uppercase, no spaces.
- steuer_id: copy exactly as shown — must be 11 digits.
- Never invent values. If a field is empty or missing, use null.
- Return valid JSON only, no explanations, no markdown.
"""


def _normalize_extracted(data: dict) -> dict:
    """Post-process extracted data: normalize formats and flag inconsistencies."""
    warnings = list(data.get("warnings") or [])

    # IBAN: remove spaces, uppercase
    if data.get("iban"):
        data["iban"] = re.sub(r"\s+", "", data["iban"]).upper()

    # BIC: remove spaces, uppercase, length check
    if data.get("bic"):
        bic = re.sub(r"\s+", "", data["bic"]).upper()
        data["bic"] = bic
        if len(bic) not in (8, 11):
            warnings.append(f"BIC '{bic}' is {len(bic)} characters - expected 8 or 11.")

    # steuer_id: strip spaces, must be exactly 11 digits
    if data.get("steuer_id"):
        sid = re.sub(r"\s+", "", str(data["steuer_id"]))
        data["steuer_id"] = sid
        if not sid.isdigit() or len(sid) != 11:
            warnings.append(f"steuer_id '{sid}' is not exactly 11 digits - please verify.")

    # Flag when birth_name differs from last_name (maiden name / name change)
    birth_name = (data.get("birth_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    if birth_name and last_name and birth_name.lower() != last_name.lower():
        warnings.append(
            f"birth_name ('{birth_name}') differs from last_name ('{last_name}'). "
            "Person may have changed their surname (e.g. after marriage)."
        )

    # Flag if birth_name present but last_name is empty - possible extraction error
    if birth_name and not last_name:
        warnings.append(
            "last_name is empty but birth_name is present. "
            "Verify whether Familienname was missed or only Geburtsname exists."
        )

    data["warnings"] = warnings
    return data


class LocalOllamaExtractor:
    def __init__(self, model_name: str = LOCAL_TEXT_MODEL):
        self.model_name = model_name

    @staticmethod
    def _fix_ocr_text(text: str) -> str:
        """Repair common OCR mistakes in German field labels before sending to the model."""
        # Fix garbled field names (rn->m is the most common Tesseract merge error)
        field_fixes = [
            ("Vomame",       "Vorname"),
            ("Vomname",      "Vorname"),
            ("Vornaine",     "Vorname"),
            ("Vornahe",      "Vorname"),
            ("Familtenname", "Familienname"),
            ("Famihenname",  "Familienname"),
            ("Famllienname", "Familienname"),
            ("Gebunsort",    "Geburtsort"),
            ("Geburtsoit",   "Geburtsort"),
            ("Anschnift",    "Anschrift"),
        ]
        for bad, good in field_fixes:
            text = text.replace(bad, good)

        # Fix garbled umlaut word forms (? and replacement chars from Tesseract)
        word_fixes = [
            ("Staatsangeh?ngkeit",  "Staatsangehörigkeit"),
            ("Staatsangeh ngkeit",  "Staatsangehörigkeit"),
            ("m?nnlich",            "maennlich"),
            ("m nnlich",            "maennlich"),
            ("gew?hnlichen",        "gewoehnlichen"),
            ("Fr?here",             "Fruehere"),
            ("Gegenw?rtige",        "Gegenwaertige"),
        ]
        for bad, good in word_fixes:
            text = text.replace(bad, good)

        # Strip any lone Unicode replacement character (U+FFFD)
        text = re.sub(r"�+", "", text)
        return text

    def extract_from_text(self, raw_text: str, source_description: str = "") -> dict:
        raw_text = self._fix_ocr_text(raw_text)
        prompt = f"""
You are a multilingual employee document extraction system.

Source: {source_description}

Task:
Extract employee information from the document text below.
Follow the schema and field mapping rules exactly.
If a field is not clearly present in the text, use null - never guess or invent values.

Document language may be German, Polish, English, Russian, Turkish, Hungarian or other.
Extract as much as possible even from non-German text.

{EXTRACTION_SCHEMA_DESCRIPTION}

Document text:
{raw_text[:8000]}
"""

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=180,
        )
        response.raise_for_status()

        result = response.json()
        text = result.get("response", "").strip()

        extracted = json.loads(text)
        extracted = _normalize_extracted(extracted)
        return extracted


def get_ai_extractor(name: str = "local"):
    if name in ("local", "ollama"):
        return LocalOllamaExtractor()
    raise ValueError(f"Unsupported AI extractor: {name}")
