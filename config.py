from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
PREPROCESSED_DIR = UPLOADS_DIR / "preprocessed"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# OCR
TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")


# AI
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


# Default providers for Phase 2 initial build
DEFAULT_OCR_ENGINE = "tesseract"
DEFAULT_AI_PROVIDER = "mistral"

