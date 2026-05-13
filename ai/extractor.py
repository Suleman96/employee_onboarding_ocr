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
  "passport_expiry": string or null,
  "working_permit_number": string or null,
  "working_permit_expiry": string or null,
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
  Ablaufdatum / Gueltig bis (for passport)  -> passport_expiry
  Aufenthaltstitel / Aufenthaltserlaubnis / Dokumentennummer (when document type is a residence permit)  -> working_permit_number
  Gueltig bis / Karte gueltig bis / Ablaufdatum (for residence permit)  -> working_permit_expiry
  Strasse / Anschrift / Anschnift           -> street_and_number
  PLZ / Postleitzahl                         -> zip_code
  Ort / Wohnort / Ortsgemeinde              -> city
  Land                                       -> country

OCR error tolerance:
  The text may contain OCR mistakes. Common patterns:
  - "rn" rendered as "m"  (Vorname -> Vomame, Geburtsname -> Gebutrsname)
  - Umlauts replaced with ? or removed (ae/oe/ue are valid substitutes)
  - Numbers mixed with letters (0/O, 1/l)
  Match field labels by approximate spelling and position, not exact match.

MRZ / Machine Readable Zone (bottom lines on passports and ID cards):
  MRZ lines look like: P<DEUAGAMAI<<ASIF<<<< or 9907032M2712169AFG or PU808695<1UKR7506121F...
  NEVER use MRZ encoded strings as field values for any field.
  MRZ lines encode DOB as YYMMDD, nationality codes (AFG, DEU, UKR), check digits, and filler characters (<).
  Only extract data from the human-readable printed part of the document, not the MRZ.

CRITICAL rules:
- Familienname (last_name) and Geburtsname (birth_name) are DIFFERENT fields.
  Put Familienname in last_name and Geburtsname in birth_name.
  Never put Geburtsname into last_name unless Familienname is absent.
- Geburtsort (place_of_birth) = city/town where the person was BORN.
  Geburtsname = the SURNAME the person was born with (maiden name). Completely different.
- place_of_birth is NOT the current city. city is the current residential city.
- place_of_birth must be a real city or town name (e.g. "Kharkiv", "Wien", "Warszawa").
  NEVER put a 2-3 letter country code (like "UKR", "DEU", "POL", "AFG") in place_of_birth.
  If you only see a country code and no city name, use null for place_of_birth.
  On Ukrainian passports, the place of birth may appear as "M.XAPKIB/UKR" or "M.KHARKIV/UKR" —
  "M." is the Ukrainian abbreviation for city. Extract only the city name (e.g. "Kharkiv"), drop
  the country code and "M." prefix. NEVER invent a city name. If uncertain, use null.
- city: extract ONLY the city name. Ignore any codes in brackets such as "(GKZ 30604)" or "(BKZ 12345)" — these are municipal reference codes, not part of the city name.
- zip_code: must be a 4-5 digit numeric postal code only. NEVER use a date (like 02.01.2025), a registration code, or any other non-postal number as zip_code.
- phone: only extract if a phone number is explicitly labelled as the person's own contact (Telefon, Tel., Mobil, Handy, Telefonnummer). NEVER use service hotlines, bank 24h numbers, or numbers labelled "Service", "Hotline", "24h Service", "Notruf". If uncertain, use null.
- gender: use the exact word from the document (e.g. "maennlich", "weiblich", "divers", "M", "F").
- marital_status: use the exact word from the document (e.g. "Verheiratet", "ledig").
- date_of_birth: DD.MM.YYYY format. Convert if necessary. If the document shows YYYYMMDD (e.g. "19861228"), convert to DD.MM.YYYY (e.g. "28.12.1986").
- passport_expiry: the expiry date of the passport. DD.MM.YYYY format.
- IBAN: uppercase, no spaces. Only extract if the value is explicitly labelled as IBAN or Kontonummer in IBAN format.
- bic: only extract if explicitly labelled BIC or SWIFT. Never guess.
- steuer_id: copy exactly as shown — must be 11 digits. If the value is not exactly 11 digits, use null.
- working_permit_number: extract the alphanumeric permit/document number from an Aufenthaltstitel or Aufenthaltserlaubnis card (e.g. "A43635334", "YYZ1JL8M7"). Usually starts with a letter (A, N, Y) followed by digits.
- working_permit_expiry: the expiry date of the residence permit card. DD.MM.YYYY format. ONLY extract this from "Gueltig bis" or "Ablaufdatum" on the Aufenthaltstitel/Aufenthaltserlaubnis card itself. NEVER use the Meldedatum, "gemeldet seit", passport issue/expiry, or any other date as working_permit_expiry. If no clear expiry date is visible on a residence permit, use null.
- country: the country of residence (where the person currently lives), NOT their nationality. For an address in Wien, use "Oesterreich". Do not copy nationality into country.
- Never invent values. If a field is empty or missing, use null.
- Return valid JSON only, no explanations, no markdown.
"""


_IBAN_LENGTHS = {
    "DE": 22, "AT": 20, "CH": 21, "PL": 28,
    "GB": 22, "FR": 27, "NL": 18, "BE": 16,
}


_YYYYMMDD_RE = re.compile(r"^\d{8}$")
_COUNTRY_CODES = {
    "AFG","ALB","DZA","AND","AGO","ATG","ARG","ARM","AUS","AUT","AZE","BHS","BHR",
    "BGD","BRB","BLR","BEL","BLZ","BEN","BTN","BOL","BIH","BWA","BRA","BRN","BGR",
    "BFA","BDI","CPV","KHM","CMR","CAN","CAF","TCD","CHL","CHN","COL","COM","COD",
    "COG","CRI","CIV","HRV","CUB","CYP","CZE","DNK","DJI","DOM","ECU","EGY","SLV",
    "GNQ","ERI","EST","SWZ","ETH","FJI","FIN","FRA","GAB","GMB","GEO","DEU","GHA",
    "GRC","GRD","GTM","GIN","GNB","GUY","HTI","HND","HUN","ISL","IND","IDN","IRN",
    "IRQ","IRL","ISR","ITA","JAM","JPN","JOR","KAZ","KEN","KIR","PRK","KOR","KWT",
    "KGZ","LAO","LVA","LBN","LSO","LBR","LBY","LIE","LTU","LUX","MDG","MWI","MYS",
    "MDV","MLI","MLT","MHL","MRT","MUS","MEX","FSM","MDA","MCO","MNG","MNE","MAR",
    "MOZ","MMR","NAM","NRU","NPL","NLD","NZL","NIC","NER","NGA","MKD","NOR","OMN",
    "PAK","PLW","PAN","PNG","PRY","PER","PHL","POL","PRT","QAT","ROU","RUS","RWA",
    "KNA","LCA","VCT","WSM","SMR","STP","SAU","SEN","SRB","SYC","SLE","SGP","SVK",
    "SVN","SLB","SOM","ZAF","SSD","ESP","LKA","SDN","SUR","SWE","CHE","SYR","TWN",
    "TJK","TZA","THA","TLS","TGO","TON","TTO","TUN","TUR","TKM","TUV","UGA","UKR",
    "ARE","GBR","USA","URY","UZB","VUT","VEN","VNM","YEM","ZMB","ZWE",
}


def _parse_date(value: str) -> str | None:
    """Convert YYYYMMDD or YYYY-MM-DD to DD.MM.YYYY. Returns None if unrecognised."""
    v = value.strip()
    if _YYYYMMDD_RE.match(v):
        return f"{v[6:8]}.{v[4:6]}.{v[:4]}"
    if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
        parts = v.split("-")
        return f"{parts[2]}.{parts[1]}.{parts[0]}"
    return None


def _clean_string_fields(data: dict) -> dict:
    """Strip Unicode replacement characters from all string values."""
    for key, val in data.items():
        if isinstance(val, str):
            data[key] = val.replace("�", "").strip() or None
    return data


def _normalize_extracted(data: dict) -> dict:
    """Post-process extracted data: normalize formats, validate, and flag inconsistencies."""
    warnings = list(data.get("warnings") or [])

    # Strip Unicode replacement chars (U+FFFD) from all string fields first
    data = _clean_string_fields(data)

    # Date fields: normalize YYYYMMDD and YYYY-MM-DD to DD.MM.YYYY
    for date_field in ("date_of_birth", "working_permit_expiry", "passport_expiry"):
        if data.get(date_field):
            converted = _parse_date(data[date_field])
            if converted:
                warnings.append(
                    f"Converted {date_field} from '{data[date_field]}' to '{converted}'."
                )
                data[date_field] = converted

    # place_of_birth: reject bare 2-3 letter country codes (MRZ artefacts like "UKR", "DEU")
    if data.get("place_of_birth"):
        pob = data["place_of_birth"].strip()
        if pob.upper() in _COUNTRY_CODES or re.match(r"^[A-Z]{2,3}$", pob):
            warnings.append(
                f"place_of_birth '{pob}' looks like a country code, not a city -- cleared."
            )
            data["place_of_birth"] = None

    # IBAN: remove spaces, uppercase, validate length by country prefix
    if data.get("iban"):
        iban = re.sub(r"\s+", "", data["iban"]).upper()
        data["iban"] = iban
        country_prefix = iban[:2] if len(iban) >= 2 else ""
        expected_len = _IBAN_LENGTHS.get(country_prefix)
        if expected_len and len(iban) != expected_len:
            warnings.append(
                f"IBAN '{iban}' is {len(iban)} chars but {country_prefix} IBANs must be {expected_len}. "
                "Likely extraction error -- cleared."
            )
            data["iban"] = None
        elif not re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]+$", iban):
            warnings.append(f"IBAN '{iban}' does not match expected format -- cleared.")
            data["iban"] = None

    # BIC: remove spaces, uppercase, length check
    if data.get("bic"):
        bic = re.sub(r"\s+", "", data["bic"]).upper()
        data["bic"] = bic
        if len(bic) not in (8, 11):
            warnings.append(f"BIC '{bic}' is {len(bic)} chars -- expected 8 or 11. Cleared.")
            data["bic"] = None

    # steuer_id: strip spaces, must be exactly 11 digits -- nullify if invalid
    if data.get("steuer_id"):
        sid = re.sub(r"\s+", "", str(data["steuer_id"]))
        if sid.isdigit() and len(sid) == 11:
            data["steuer_id"] = sid
        else:
            warnings.append(
                f"steuer_id '{sid}' is not exactly 11 digits -- cleared. Please enter manually."
            )
            data["steuer_id"] = None

    # zip_code: must be 4-5 digits only (postal code, not a date or registration number)
    if data.get("zip_code"):
        zc = re.sub(r"\s+", "", str(data["zip_code"]))
        if not re.match(r"^\d{4,5}$", zc):
            warnings.append(
                f"zip_code '{zc}' does not look like a postal code (expected 4-5 digits) -- cleared."
            )
            data["zip_code"] = None
        else:
            data["zip_code"] = zc

    # city: strip Austrian/German municipal reference codes like "(GKZ 30604)" or "(BKZ 12345)"
    if data.get("city"):
        cleaned_city = re.sub(r"\s*\([A-Z]{2,3}\s*\d+\)", "", data["city"]).strip()
        if cleaned_city != data["city"]:
            warnings.append(f"Stripped municipal code from city: '{data['city']}' -> '{cleaned_city}'")
        data["city"] = cleaned_city or None

    # Flag when birth_name differs from last_name (maiden name / name change)
    birth_name = (data.get("birth_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    if birth_name and last_name and birth_name.lower() != last_name.lower():
        warnings.append(
            f"birth_name ('{birth_name}') differs from last_name ('{last_name}'). "
            "Person may have changed their surname (e.g. after marriage)."
        )

    # Flag if birth_name present but last_name is empty -- possible extraction error
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

        # Fix Windows-1252 mojibake: Tesseract on Windows writes UTF-8 but Python
        # sometimes reads its temp file as Latin-1, corrupting umlauts (ß->AŸ, ö->A¶, etc.).
        # Re-encode as Latin-1 bytes and decode as UTF-8 to recover the original characters.
        try:
            text = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

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
            ("Staatsangeh?ngkeit",  "Staatsangehoerigkeit"),
            ("Staatsangeh ngkeit",  "Staatsangehoerigkeit"),
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

Document context: {source_description}

Task:
Extract employee information from the document text below.
Follow the schema and field mapping rules exactly.
Only extract fields that are clearly visible in THIS document.
If a field is not clearly present in the text, use null -- never guess or invent values.

Document language may be German, Polish, English, Russian, Turkish, Hungarian or other.

{EXTRACTION_SCHEMA_DESCRIPTION}

Document text:
{raw_text[:4000]}
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
