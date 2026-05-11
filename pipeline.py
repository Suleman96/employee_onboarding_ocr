# pipelines.py

from pathlib import Path
import shutil
import uuid
import zipfile

from docx import Document
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import fitz

from config import ORIGINALS_DIR, EXTRACTED_IMAGES_DIR
from ocr.quality import analyse_image
from ocr.preprocessor import preprocess_image
from ocr.engines import get_ocr_engine

from ai.extractor import get_ai_extractor
from ai.verifier import LocalOllamaVerifier

from update_employee import merge_extraction_results, map_extracted_to_employee_fields, save_employee_draft

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
PDF_EXTENSIONS = {".pdf"}
DOCX_EXTENSIONS = {".docx"}

def save_uploaded_file(upload_file) -> str:
    suffix = Path(upload_file.filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{suffix}"
    target = ORIGINALS_DIR / safe_name

    with target.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return str(target)

def extract_text_from_docx(docx_path: str) -> str:
    doc = Document(docx_path)
    
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    table_texts= []
    
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip()) 
            if row_text:
                table_texts.append(row_text)
                print("table_texts: from extract text from docs: ", table_texts)
                
    return "/n".join(paragraphs + table_texts).strip()

def extract_images_from_docx(docx_path: str) -> list[str]:
    output_paths = []
    extract_dir = EXTRACTED_IMAGES_DIR / Path(docx_path).stem
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(docx_path, "r") as z:
        for name in z.namelist():
            if name.startswith("word/media/"):
                filename = Path(name).name
                out_path = extract_dir / filename
                with z.open(name) as src, open(out_path, "wb") as dst:
                    dst.write(src.read())
                output_paths.append(str(out_path))

    return output_paths


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


def render_pdf_pages_to_images(pdf_path: str) -> list[str]:
    try:
        pages = convert_from_path(pdf_path)
    except Exception as e:
        raise RuntimeError(
            "PDF page rendering failed. Poppler is probably missing or not in PATH. "
            f"Original error: {str(e)}"
        )

    output_dir = EXTRACTED_IMAGES_DIR / Path(pdf_path).stem
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths = []
    for i, page in enumerate(pages, start=1):
        out_path = output_dir / f"page_{i}.png"
        page.save(out_path, "PNG")
        image_paths.append(str(out_path))

    return image_paths

def extract_embedded_images_from_pdf(pdf_path: str) -> list[str]:
    """
    Extract embedded images from a PDF using PyMuPDF.
    This is useful when a PDF contains image objects in addition to or instead of page text.
    """
    doc = fitz.open(pdf_path)
    output_dir = EXTRACTED_IMAGES_DIR / f"{Path(pdf_path).stem}_embedded"
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)

        for image_index, img in enumerate(image_list, start=1):
            xref = img[0] # gets image ID
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]

            out_path = output_dir / f"page_{page_index + 1}_img_{image_index}.{ext}"

            with open(out_path, "wb") as f:
                f.write(image_bytes)

            image_paths.append(str(out_path))

    doc.close()
    return image_paths



# This is where the real OCR pipeline begins.


def process_image_file(image_path: str) -> dict:
    
    #This runs the quality analysis from ocr/quality.py. dark, blurry
    quality = analyse_image(image_path)

    # For now we keep the routing simple:
    # preprocess the image, OCR it, then run local extraction + verification
    
    #Run the full preprocessing pipeline.
    prep = preprocess_image(image_path)
    
    #Take the final OCR-ready image path.
    final_image = prep["final_path"]

    # Get the OCR engine object.
    ocr = get_ocr_engine("tesseract")
    # Run OCR on the preprocessed image.
    raw_text = ocr.extract_text(final_image)

    # Get the local AI extractor.
    extractor = get_ai_extractor("local")
    #This sends the OCR text into the local extraction model.
    extracted = extractor.extract_from_text(
        raw_text,
        source_description=f"OCR image: {Path(image_path).name}"
    )

    #Create the second local AI pass.
    verifier = LocalOllamaVerifier()
    #Compare extracted fields back against the OCR text.
    verification = verifier.verify_extraction(raw_text, extracted)

    return {
        "source": image_path,
        "quality": {
            "width": quality.width,
            "height": quality.height,
            "brightness_score": quality.brightness_score,
            "blur_score": quality.blur_score,
            "is_dark": quality.is_dark,
            "is_blurry": quality.is_blurry,
            "is_small": quality.is_small,
            "needs_preprocessing": quality.needs_preprocessing,
            "route_to_vision": quality.route_to_vision,
        },
        "raw_text": raw_text,
        "extracted_data": extracted,
        "verification": verification,
        "debug_steps": prep["steps"],
        "pipeline_path": "image_preprocess_ocr_local_extract_local_verify",
    }

def process_docx_file(docx_path: str) -> dict:
    # Read the typed text from the DOCX.
    direct_text = extract_text_from_docx(docx_path)
    
    # Run the full preprocessing pipeline.
    image_paths = extract_images_from_docx(docx_path)

    #collect all partial results here.
    results = []
    
    # Only process text if text actually exists.
    if direct_text.strip():
        
        #exactly like the image path, except now the source is direct DOCX text instead of OCR text.
        # Direct text is often more accurate than OCR.
        extractor = get_ai_extractor("local")
        extracted = extractor.extract_from_text(
            direct_text,
            source_description=f"DOCX text: {Path(docx_path).name}"
        )

        verifier = LocalOllamaVerifier()
        verification = verifier.verify_extraction(direct_text, extracted)

        # Store the direct-text result.
        results.append({
            "source": f"{docx_path}::text",
            "raw_text": direct_text,
            "extracted_data": extracted,
            "verification": verification,
            "pipeline_path": "docx_text_local_extract_local_verify",
        })
    
    # Loop over extracted DOCX images.
    for img_path in image_paths:
        # Run the same image OCR pipeline on each embedded image.
        image_result = process_image_file(img_path)
        results.append(image_result)

    # Combine all partial results.
    merged = merge_extraction_results(results)

    return {
        "source": docx_path,
        "raw_text": direct_text,
        "embedded_images": image_paths,
        "sub_results": results,
        "extracted_data": merged,
        "verification": {
            "overall_confidence": "medium",
            "ready_for_review": True,
            "issues": [],
        },
        "pipeline_path": "docx_mixed_content_pipeline",
    }
      

def process_pdf_file(pdf_path: str) -> dict:
    direct_text = extract_text_from_pdf_if_possible(pdf_path)
    results = []

    # 1. If direct text exists, process it first
    if direct_text.strip():
        extractor = get_ai_extractor("local")
        extracted = extractor.extract_from_text(
            direct_text,
            source_description=f"PDF text layer: {Path(pdf_path).name}"
        )

        verifier = LocalOllamaVerifier()
        verification = verifier.verify_extraction(direct_text, extracted)

        results.append({
            "source": f"{pdf_path}::text",
            "raw_text": direct_text,
            "extracted_data": extracted,
            "verification": verification,
            "pipeline_path": "pdf_text_local_extract_local_verify",
        })

    # 2. Try page-image OCR only if possible
    page_images = []
    embedded_images = []

    try:
        page_images = render_pdf_pages_to_images(pdf_path)
    except Exception:
        page_images = []

    try:
        embedded_images = extract_embedded_images_from_pdf(pdf_path)
    except Exception:
        embedded_images = []

    for page_img in page_images:
        page_result = process_image_file(page_img)
        results.append(page_result)

    for emb_img in embedded_images:
        emb_result = process_image_file(emb_img)
        results.append(emb_result)

    if not results:
        raise ValueError(
            "PDF could not be processed. No text layer found, and image rendering/OCR path failed."
        )

    merged = merge_extraction_results(results)

    return {
        "source": pdf_path,
        "raw_text": direct_text,
        "page_images": page_images,
        "embedded_images": embedded_images,
        "sub_results": results,
        "extracted_data": merged,
        "verification": {
            "overall_confidence": "medium",
            "ready_for_review": True,
            "issues": [],
        },
        "pipeline_path": "pdf_mixed_content_pipeline",
    }
      
def process_single_file(file_path: str) -> dict:
    suffix = Path(file_path).suffix.lower()

    if suffix in IMAGE_EXTENSIONS:
        return process_image_file(file_path)

    if suffix in DOCX_EXTENSIONS:
        return process_docx_file(file_path)

    if suffix in PDF_EXTENSIONS:
        return process_pdf_file(file_path)


    raise ValueError(f"Unsupported file type: {suffix}")


# main function of pipeline.py
def process_uploaded_files(db, files=None, text_input: str | None = None, employee_id: int | None = None):
    
    # If no files were given, use an empty list instead of None
    files = files or []
    
    # This stores the results of every uploaded file.
    all_results = []

    # Loop through each uploaded file.
    for upload_file in files:
        
        # Skip completely empty upload entries
        if not upload_file or not upload_file.filename:
            continue

        # Skip files with no extension
        suffix = Path(upload_file.filename).suffix.lower()
        if not suffix:
            continue
        # Save the uploaded file to disk first. uuid name
        saved_path = save_uploaded_file(upload_file) 
        # Let the dispatcher decide how to process it.
        result = process_single_file(saved_path)
        # This stores the results of every uploaded file.
        all_results.append(result)

    # This handles pasted plain text.
    if text_input and text_input.strip():
        extractor = get_ai_extractor("local")
        extracted = extractor.extract_from_text(
            text_input,
            source_description="Pasted text"
        )

        verifier = LocalOllamaVerifier()
        verification = verifier.verify_extraction(text_input, extracted)

        all_results.append({
            "source": "text_input",
            "raw_text": text_input,
            "extracted_data": extracted,
            "verification": verification,
            "pipeline_path": "text_local_extract_local_verify",
        })

    if not all_results:
        raise ValueError("No input provided")

    # Combine all document results into one overall result.
    merged = merge_extraction_results(all_results)
    # Map normalized extraction names to your DB field names. , Your DB naming must stay as-is.
    mapped = map_extracted_to_employee_fields(merged)
    # Save or update the employee record.
    employee = save_employee_draft(db, mapped, employee_id=employee_id)

    # This is useful for review pages and debugging.
    return {
        "employee_id": employee.id,
        "employee": employee,
        "results": all_results,
        "merged_data": merged,
        "mapped_data": mapped,
    }