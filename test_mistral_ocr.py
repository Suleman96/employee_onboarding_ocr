# test_mistral_ocr.py
#
# Tests the Mistral OCR engine in isolation, then runs the full pipeline
# (Mistral OCR -> local Ollama extractor) on a sample image.
#
# Usage:
#   python test_mistral_ocr.py
#   python test_mistral_ocr.py path/to/your/image.jpg

import io
import json
import sys
from pathlib import Path

# Force UTF-8 output so non-ASCII characters from Mistral OCR print correctly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ── pick a test image ────────────────────────────────────────────────────────

DEFAULT_IMAGE = Path("uploads/upload_0001/originals/22f7f08f75ab46fcb3beccf029b9a33f.jpeg")

image_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_IMAGE

if not image_path.exists():
    print(f"[ERROR] Image not found: {image_path}")
    sys.exit(1)

print(f"[INFO] Test image: {image_path}")
print("=" * 60)

# ── Step 1: Mistral OCR ──────────────────────────────────────────────────────

print("\n[STEP 1] Running Mistral OCR engine...")

from ocr.mistral_ocr import MistralOCREngine

engine = MistralOCREngine()
raw_text = engine.extract_text(str(image_path))

print(f"\n--- Mistral OCR output ({len(raw_text)} chars) ---")
print(raw_text)
print("--- end of OCR output ---\n")

if not raw_text.strip():
    print("[WARN] Mistral OCR returned empty text. Check the image or API key.")
    sys.exit(1)

# ── Step 2: Local Ollama extractor ───────────────────────────────────────────

print("[STEP 2] Running local Ollama extractor on OCR text...")

from ai.extractor import LocalOllamaExtractor

extractor = LocalOllamaExtractor()
extracted = extractor.extract_from_text(raw_text, source_description="Mistral OCR test")

print("\n--- Extracted fields ---")
print(json.dumps(extracted, indent=2, ensure_ascii=False))
print("--- end of extraction ---")

# ── Summary ──────────────────────────────────────────────────────────────────

non_null = {k: v for k, v in extracted.items() if v and k not in ("confidence", "warnings", "extraction_notes")}
print(f"\n[DONE] {len(non_null)} non-null fields extracted: {list(non_null.keys())}")
if extracted.get("warnings"):
    print(f"[WARN] Extraction warnings: {extracted['warnings']}")
