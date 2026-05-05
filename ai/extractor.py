# ai/extractor.py

import json
import mistralai import MistralAI  # type: ignore[reportMissingImports]

from config import MISTRAL_API_KEY

EXTRACTION_SCHEMA = {
    
    "type": "object",
    "properties": {
        "first_name": {"type": ["string", "null"]},
        "last_name": {"type": ["string", "null"]},
        "date_of_birth": {"type": ["string", "null"]},
        "place_of_birth": {"type": ["string", "null"]},
        "country_of_birth": {"type": ["string", "null"]},
        "nationality": {"type": ["string", "null"]},
        "id_number": {"type": ["string", "null"]},
        "passport_number": {"type": ["string", "null"]},
        "street_and_number": {"type": ["string", "null"]},
        "zip_code": {"type": ["string", "null"]},
        "city": {"type": ["string", "null"]},
        "country": {"type": ["string", "null"]},
        "iban": {"type": ["string", "null"]},
        "bic": {"type": ["string", "null"]},
        "bank_name": {"type": ["string", "null"]},
        "account_owner": {"type": ["string", "null"]},
        "steuer_id": {"type": ["string", "null"]},
        "sozialversicherung": {"type": ["string", "null"]},
        "health_insurance_name": {"type": ["string", "null"]},
        "health_insurance_number": {"type": ["string", "null"]},
        "phone": {"type": ["string", "null"]},
        "email": {"type": ["string", "null"]},
        "confidence": {
            "type": "object",
            "additionalProperties": {
                "type": "string",
                "enum": ["high", "medium", "low", "not_found"]
            }
        },
        "extraction_notes": {"type": ["string", "null"]}
    },
    "required": ["first_name", "last_name", "date_of_birth", "confidence"]
}

class MistralExtractor:
    def __init__(self):
        if not MISTRAL_API_KEY:
            raise ValueError("Mistral API is missing")
        
        self.client = Mistral(api_key=MISTRAL_API_KEY)
    def extract_from_text(self, raw_text: str, source_description: str = "") -> dict:
        
        prompt = f"""
        
        Du bist ein Datenextraktions-Assistent für internationale Personaldokumente.

        Extrahiere Mitarbeiterdaten aus dem folgenden Text.

        WICHTIGE REGELN:
        - Erfinde nichts
        - Wenn ein Feld nicht vorhanden ist: null
        - date_of_birth immer in DD.MM.YYYY
        - IBAN ohne Leerzeichen, in Großbuchstaben
        - place_of_birth ist NICHT die aktuelle Stadt
        - city ist aktuelle Wohnstadt, nicht Geburtsort
        - confidence pro Feld: high / medium / low / not_found

        Quelle:
        {source_description}

        Text:
        {raw_text[:5000]}
        """
        
        response = self.client.chat.complete(
            model = "mistral-small-latest",
            messages = [{"role": "user", "content": prompt}],
            response_format= {
                "type": "json_schema",
                "json_schema": {
                    "name" : "EmployeeExtraction",
                    "schema" : EXTRACTION_SCHEMA,
                    "strict" : True
                }
            }
        )
        return json.loads(response.choices[0].message.content)

def get_ai_extractor(name: str = "mistral"):
    name = (name or "").lower()
    
    if name == "mistral":
        return MistralExtractor()
    
    raise ValueError(f"Unsupported AI extractor : {name}")
