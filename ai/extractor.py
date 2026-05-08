# ai/extractor.py

import json
import requests

from config import OLLAMA_BASE_URL, LOCAL_TEXT_MODEL


EXTRACTION_SCHEMA_DESCRIPTION = """
Return a JSON object with these fields only:
{
  "first_name": string or null,
  "last_name": string or null,
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
    "last_name": "high|medium|low|not_found"
  },
  "extraction_notes": string or null
}
Rules:
- never invent values
- if missing, use null
- date_of_birth must be DD.MM.YYYY if possible
- place_of_birth is NOT always the current city
- city is current residential city
- IBAN should be uppercase without spaces
"""


class LocalOllamaExtractor:
    def __init__self(self, model_name:str = LOCAL_TEXT_MODEL):
        self.model_name = model_name
        
    def extract_from_text(self, raw_text: str, source_description:str = "") -> dict:
        prompt = f"""
        
        You are a multilingual employee document extraction system 
        
        Source:
        {source_description}
        
        Task:
        Extract employee informaiton from the text below. Follow the schema and rules exactly. If information is missing, do not guess, just use null.
        
        Important:
        - The document amy be in german, polish, english, russian, turkish, hungarian or other languages. Always try to extract as much as possible, even from non-german text.
        - Follow the schema and rules exactly. Do no add any fields that are not in the schema. Do not return any explanations.
        - If the field is not clearly present, return null. Do no guess or infer values.
        - Never invent values
        - Keep place_of_birth separate from current address
        - Return valid JSON only
        
        Schema:
        {EXTRACTION_SCHEMA_DESCRIPTION}
        
        Text:
        {raw_text[:8000]}
       
        """
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=180,
        )
        response.raise_for_status()
        
        result =response.json()
        text = result.get("response",  "").strip()
        
        return json.loads(text)

def get_ai_extractor(name: str = "local"):
    if name in ("local", "ollama"):
        return LocalOllamaExtractor()
    raise ValueError(f"Unsupported AI extractor: {name}")
