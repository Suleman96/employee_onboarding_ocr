from pathlib import Path
import shutil
import uuid

from docx import Document
from PyPDF2 import PdfReader
from pdf2image import convert_from_path

from config import UPLOADS_DIR, DEFAULT_OCR_ENGINE, DEFAULT_AI_PROVIDER
from ocr.quality import analyse_image
from ocr.preprocessor import preprocess_adaptive
from ocr.engines import get_ocr_engine
from ai.extractor import get_ai_extractor
from ai.verifier import MistralVerifier
from update_employee import merge_extraction_results, map_extracted_to_employee_fields, save_employee_draft


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
PDF_EXTENSIONS = {".pdf"}
DOCX_EXTENSIONS = {".docx"}


def save_uploaded_file(upload_file) -> str:
    suffix = Path(upload_file.filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    target = UPLOADS_DIR / safe_name

    with target.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return str(target)


def extract_text_from_docx(docx_path: str) -> str:
    doc = Document(docx_path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text_from_pdf_if_possible(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        texts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                texts.append(text)
        return "\n".join(texts).strip()
    except Exception:
        return ""


def convert_pdf_to_images(pdf_path: str) -> list[str]:
    pages = convert_from_path(pdf_path)
    image_paths = []

    for i, page in enumerate(pages, start=1):
        out_path = UPLOADS_DIR / f"{Path(pdf_path).stem}_page_{i}.png"
        page.save(out_path, "PNG")
        image_paths.append(str(out_path))

    return image_paths


def process_image_file(image_path: str, ocr_engine: str, ai_provider: str) -> dict:
    quality = analyse_image(image_path)

    if quality.route_to_vision:
        raise NotImplementedError("Vision-direct path can be added later. Start with OCR path first.")

    processed_path = preprocess_adaptive(image_path, quality, skip=False)
    ocr = get_ocr_engine(ocr_engine)
    raw_text = ocr.extract_text(processed_path)

    ai = get_ai_extractor(ai_provider)
    extracted = ai.extract_from_text(raw_text, source_description=f"Image OCR from {Path(image_path).name}")

    verifier = MistralVerifier()
    verification = verifier.verify_extraction(raw_text, extracted)

    return {
        "source": image_path,
        "raw_text": raw_text,
        "extracted_data": extracted,
        "verification": verification,
        "pipeline_path": f"ocr_{ocr_engine}_ai_{ai_provider}",
    }


def process_docx_file(docx_path: str, ai_provider: str) -> dict:
    raw_text = extract_text_from_docx(docx_path)

    ai = get_ai_extractor(ai_provider)
    extracted = ai.extract_from_text(raw_text, source_description=f"DOCX text from {Path(docx_path).name}")

    verifier = MistralVerifier()
    verification = verifier.verify_extraction(raw_text, extracted)

    return {
        "source": docx_path,
        "raw_text": raw_text,
        "extracted_data": extracted,
        "verification": verification,
        "pipeline_path": f"docx_text_ai_{ai_provider}",
    }


def process_pdf_file(pdf_path: str, ocr_engine: str, ai_provider: str) -> dict:
    raw_text = extract_text_from_pdf_if_possible(pdf_path)

    if raw_text:
        ai = get_ai_extractor(ai_provider)
        extracted = ai.extract_from_text(raw_text, source_description=f"PDF text from {Path(pdf_path).name}")

        verifier = MistralVerifier()
        verification = verifier.verify_extraction(raw_text, extracted)

        return {
            "source": pdf_path,
            "raw_text": raw_text,
            "extracted_data": extracted,
            "verification": verification,
            "pipeline_path": f"pdf_text_ai_{ai_provider}",
        }

    page_image_paths = convert_pdf_to_images(pdf_path)
    page_results = [process_image_file(path, ocr_engine, ai_provider) for path in page_image_paths]

    merged = merge_extraction_results(page_results)
    return {
        "source": pdf_path,
        "raw_text": "\n".join(r.get("raw_text", "") for r in page_results),
        "extracted_data": merged,
        "verification": {"issues": [], "overall_confidence": "medium", "ready_for_review": True},
        "pipeline_path": f"pdf_scanned_ocr_{ocr_engine}_ai_{ai_provider}",
    }


def process_single_file(file_path: str, ocr_engine: str, ai_provider: str) -> dict:
    suffix = Path(file_path).suffix.lower()

    if suffix in IMAGE_EXTENSIONS:
        return process_image_file(file_path, ocr_engine, ai_provider)

    if suffix in DOCX_EXTENSIONS:
        return process_docx_file(file_path, ai_provider)

    if suffix in PDF_EXTENSIONS:
        return process_pdf_file(file_path, ocr_engine, ai_provider)

    raise ValueError(f"Unsupported file type: {suffix}")


def process_uploaded_files(db, files=None, text_input: str | None = None, employee_id: int | None = None):
    files = files or []
    all_results = []

    for upload_file in files:
        saved_path = save_uploaded_file(upload_file)
        result = process_single_file(
            saved_path,
            ocr_engine=DEFAULT_OCR_ENGINE,
            ai_provider=DEFAULT_AI_PROVIDER,
        )
        all_results.append(result)

    if text_input and text_input.strip():
        ai = get_ai_extractor(DEFAULT_AI_PROVIDER)
        extracted = ai.extract_from_text(text_input, source_description="Pasted text")
        verifier = MistralVerifier()
        verification = verifier.verify_extraction(text_input, extracted)

        all_results.append({
            "source": "text_input",
            "raw_text": text_input,
            "extracted_data": extracted,
            "verification": verification,
            "pipeline_path": f"text_ai_{DEFAULT_AI_PROVIDER}",
        })

    if not all_results:
        raise ValueError("No documents or text were provided")

    merged = merge_extraction_results(all_results)
    mapped = map_extracted_to_employee_fields(merged)
    employee = save_employee_draft(db, mapped, employee_id=employee_id)

    return {
        "employee_id": employee.id,
        "employee": employee,
        "documents_processed": len(all_results),
        "merged_data": merged,
        "mapped_data": mapped,
        "results": all_results,
    }