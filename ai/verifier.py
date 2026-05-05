import json
from mistralai.client import Mistral

from config import MISTRAL_API_KEY


VERIFICATION_SCHEMA = {
    
    "type": "object",
    "properties": {
        "issues": {
            "type": "array",
            "items": {
                "type": "object"
                "properties":{
                    "field": {"type": "string"},
                    "problem": {"type": "string"},
                    "suggestion":  {"type": ["string", "null"]},
                    "severity": {"type": "string", "enum": ["error", "warning", "info"]}
                },
                "required": ["field", "problem", "severity"]
            }
        },
        "corrected_fields": {
            "type": "object",
            "additionalProperties": {"type": ["string", "null"]}
        },
        "overall_confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"]
        },
        "ready_for_review": {"type": "boolean"}
    },
    "required": ["issues", "overall_confidence", "ready_for_review"]
}

class MistralVerifier:
    def __init__(self):
        if not MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY is missing")
        self.client = Mistral(api_key=MISTRAL_API_KEY)

    def verify_extraction(self, original_text: str, extracted: dict) -> dict:
        prompt = f"""
            Prüfe die extrahierten Mitarbeiterdaten gegen den Originaltext.

            Prüfregeln:
            - Steuer-ID: genau 11 Ziffern
            - IBAN: Ländercode + plausible Länge
            - BIC: 8 oder 11 Zeichen
            - date_of_birth: DD.MM.YYYY
            - place_of_birth nicht mit aktueller Stadt verwechseln
            - nichts erfinden

            Originaltext:
            {original_text[:4000]}

            Extrahierte Daten:
            {json.dumps(extracted, ensure_ascii=False)}
            """

        response = self.client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "VerificationResult",
                    "schema": VERIFICATION_SCHEMA,
                    "strict": True
                }
            }
        )

        return json.loads(response.choices[0].message.content)