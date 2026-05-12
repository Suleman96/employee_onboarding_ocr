"""
Standalone pipeline test — creates a synthetic document image and runs
the full OCR + preprocessing stack without needing FastAPI or a database.

Run:  python test_pipeline.py
"""

import sys
import traceback
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ── helpers ──────────────────────────────────────────────────────────────────

SAMPLE_TEXT = """\
Personalfragebogen
Vorname:        Max
Familienname:   Mustermann
Geburtsdatum:   15.03.1990
Geburtsort:     Berlin
Nationalität:   Deutsch
Straße:         Musterstraße 12
PLZ / Ort:      10115 Berlin
Telefon:        +49 170 1234567
E-Mail:         max.mustermann@example.de
IBAN:           DE89370400440532013000
BIC:            COBADEFFXXX
Steuer-ID:      12345678901
"""


def create_test_image(out_path: Path) -> Path:
    """Draw sample employee-form text onto a white A4-ish image."""
    width, height = 900, 700
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except IOError:
        font = ImageFont.load_default()

    draw.multiline_text((60, 60), SAMPLE_TEXT, fill="black", font=font, spacing=8)
    img.save(str(out_path))
    print(f"[OK]  Test image saved: {out_path}")
    return out_path


def run_quality_check(image_path: str):
    from ocr.quality import analyse_image
    q = analyse_image(image_path)
    print(f"\n--- Quality analysis ---")
    print(f"  Size       : {q.width}x{q.height}")
    print(f"  Brightness : {q.brightness_score:.1f}")
    print(f"  Blur score : {q.blur_score:.1f}")
    print(f"  is_dark    : {q.is_dark}")
    print(f"  is_blurry  : {q.is_blurry}")
    print(f"  is_small   : {q.is_small}")
    print(f"  needs_prep : {q.needs_preprocessing}")
    return q


def run_preprocessor(image_path: str):
    from ocr.preprocessor import preprocess_image
    prep = preprocess_image(image_path)
    print(f"\n--- Preprocessor ---")
    print(f"  final_path : {prep['final_path']}")
    candidates = {k: v for k, v in prep["ocr_candidates"].items() if v}
    print(f"  candidates : {list(candidates.keys())}")
    assert Path(prep["final_path"]).exists(), "Final preprocessed image does not exist!"
    print(f"  [OK]  Final image exists on disk")
    return prep


def run_ocr(prep: dict):
    from ocr.engines import get_ocr_engine
    from pipeline import score_ocr_text

    ocr = get_ocr_engine("tesseract")
    if not ocr.is_available():
        print("\n[SKIP] Tesseract not found — skipping OCR step")
        return None

    candidates = {k: v for k, v in prep["ocr_candidates"].items() if v}
    best_text, best_score, best_name = "", -1, ""

    print(f"\n--- OCR trials ({len(candidates)} candidates) ---")
    for name, path in candidates.items():
        try:
            text = ocr.extract_text(path)
            score = score_ocr_text(text)
            short = text[:60].replace("\n", " ")
            print(f"  [{name:10s}]  score={score:5d}  preview: {short!r}")
            if score > best_score:
                best_text, best_score, best_name = text, score, name
        except Exception as exc:
            print(f"  [{name:10s}]  ERROR: {exc}")

    print(f"\n  Best candidate: {best_name!r} (score={best_score})")
    return best_text


def run_ai_extraction(raw_text: str):
    from ai.extractor import get_ai_extractor
    print(f"\n--- AI extraction (Ollama) ---")
    try:
        extractor = get_ai_extractor("local")
        extracted = extractor.extract_from_text(raw_text, source_description="test image")
        print(f"  first_name  : {extracted.get('first_name')}")
        print(f"  last_name   : {extracted.get('last_name')}")
        print(f"  date_of_birth: {extracted.get('date_of_birth')}")
        print(f"  iban        : {extracted.get('iban')}")
        print(f"  steuer_id   : {extracted.get('steuer_id')}")
        return extracted
    except Exception as exc:
        print(f"  [SKIP] Ollama unavailable or error: {exc}")
        return {}


def run_verifier(raw_text: str, extracted: dict):
    from ai.verifier import LocalOllamaVerifier
    print(f"\n--- AI verification (Ollama) ---")
    try:
        verifier = LocalOllamaVerifier()
        verification = verifier.verify_extraction(raw_text, extracted)
        print(f"  overall_confidence : {verification.get('overall_confidence')}")
        print(f"  ready_for_review   : {verification.get('ready_for_review')}")
        issues = verification.get("issues", [])
        if issues:
            for issue in issues:
                print(f"  ISSUE: {issue}")
        else:
            print(f"  No issues reported")
        return verification
    except Exception as exc:
        print(f"  [SKIP] Ollama unavailable or error: {exc}")
        return {}


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    test_image_path = Path("uploads/test_input.png")
    test_image_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("OCR Pipeline Test")
    print("=" * 60)

    create_test_image(test_image_path)

    try:
        q = run_quality_check(str(test_image_path))
    except Exception:
        print("[FAIL] Quality check failed:")
        traceback.print_exc()
        sys.exit(1)

    try:
        prep = run_preprocessor(str(test_image_path))
    except Exception:
        print("[FAIL] Preprocessor failed:")
        traceback.print_exc()
        sys.exit(1)

    raw_text = run_ocr(prep)

    if raw_text:
        extracted = run_ai_extraction(raw_text)
        if extracted:
            run_verifier(raw_text, extracted)
    else:
        print("\n[WARN] No OCR text produced — skipping AI steps")

    print("\n" + "=" * 60)
    print("Pipeline test complete")
    print("=" * 60)


if __name__ == "__main__":
    main()