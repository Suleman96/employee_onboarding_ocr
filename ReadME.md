# Employee Onboarding OCR System

An AI-powered employee onboarding platform for hospitality companies. Upload employee documents, extract data automatically with OCR and local AI, review it in a clean web UI, and generate city-specific employment contracts in one click.

---

## What It Does

Onboarding in hotels and service companies is still heavily manual — HR teams read documents one by one, copy data into systems, and generate contracts by hand. This system replaces that with an automated pipeline:

1. **Upload** — accept scanned IDs, PDFs, Word documents, or photos
2. **Extract** — OCR reads the document; a local LLM (Ollama/Qwen) structures the data
3. **Review** — a web UI lets the HR team verify and correct extracted fields
4. **Approve** — one-click approval with required-field validation
5. **Generate** — city-specific employment contracts rendered from `.docx` templates
6. **Audit** — every action is logged with a full audit trail

---

## Key Features

- **Multi-format document intake** — PDF, DOCX, JPG/PNG/HEIC, WebP
- **Multi-language OCR** — German, English, Polish, Russian, Turkish, Hungarian (Tesseract + EasyOCR + PaddleOCR)
- **AI extraction** — local Ollama (Qwen 2.5 7B) with optional paid fallback (Mistral)
- **Image preprocessing** — auto blur/darkness detection, contrast enhancement before OCR
- **Employee data model** — personal info, identity documents, address, health insurance, tax, banking, and employment details
- **Approval workflow** — draft → under review → approved / rejected
- **Contract generation** — city-aware resolver (Berlin, Wien, Köln group) picks the right `.docx` template and renders it via Jinja2/docxtpl
- **PDF export** — converts generated contracts to PDF automatically
- **Audit logging** — every create, update, approve, and generate action is recorded
- **n8n integration** — REST endpoint for automated intake from n8n workflows

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, FastAPI, Uvicorn |
| Database | SQLite (dev), SQLAlchemy ORM |
| Frontend | Jinja2 templates, HTML, CSS, JavaScript |
| OCR | Tesseract, EasyOCR, PaddleOCR, Mistral Pixtral (vision fallback) |
| AI Extraction | Ollama (local) — Qwen 2.5 7B / Qwen 2.5-VL |
| Document handling | python-docx, PyMuPDF, pdf2image, PyPDF2 |
| Contract rendering | docxtpl, docx2pdf |
| Image processing | OpenCV, Pillow |
| Utilities | python-dotenv, loguru, tenacity, apscheduler |

---

## Project Structure

```
employee_onboarding_ocr/
│
├── main.py                  # FastAPI app — all routes and request handlers
├── database.py              # SQLAlchemy models (Employee, AuditLog) and session
├── schemas.py               # Pydantic schemas for validation
├── pipeline.py              # Document ingestion pipeline (upload → OCR → AI → save)
├── config.py                # All settings — paths, model names, thresholds
├── update_employee.py       # Merges extraction results into employee records
│
├── ai/
│   ├── extractor.py         # Local Ollama extraction (structured JSON from raw text)
│   └── verifier.py          # Local Ollama verification pass
│
├── ocr/
│   ├── engines.py           # OCR engine selector (Tesseract / EasyOCR / PaddleOCR)
│   ├── preprocessor.py      # Image enhancement before OCR
│   ├── quality.py           # Blur and darkness analysis
│   ├── mistral_pixtral_vision.py  # Paid vision fallback
│   └── easyocr.py           # EasyOCR wrapper
│
├── contracts/
│   ├── resolver.py          # Maps employee attributes → correct .docx template
│   ├── generator.py         # Renders template and exports DOCX + PDF
│   ├── hours.py             # Weekly/daily hours schedule helpers
│   ├── berlin/              # Berlin contract templates (befristet + unbefristet)
│   ├── koeln_group/         # Köln, Hamburg, Frankfurt, Düsseldorf, Bergisch Gladbach
│   └── wien/                # Vienna contract templates
│
├── templates/               # Jinja2 HTML templates for the web UI
├── static/                  # CSS and JavaScript
├── uploads/                 # Uploaded and preprocessed files (auto-created)
├── output/                  # Generated contracts (DOCX + PDF)
├── data/                    # SQLite database file
└── logs/                    # Application logs
```

---

## Getting Started

### Prerequisites

- Python 3.13
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) — install and add to PATH
- [Ollama](https://ollama.com/) — run locally with `ollama pull qwen2.5:7b`

### Installation

```bash
# Clone the repo
git clone <repo-url>
cd employee_onboarding_ocr

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Copy `.env.local` and adjust as needed:

```env
# OCR
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
TESSERACT_LANGS=deu+eng+pol+rus+tur+hun

# Local AI (Ollama)
LOCAL_TEXT_MODEL=qwen2.5:7b
LOCAL_VISION_MODEL=qwen2.5vl:7b
OLLAMA_BASE_URL=http://localhost:11434

# Paid fallback (disabled by default)
PAID_FALLBACK_ENABLED=false
MISTRAL_API_KEY=
```

### Run the App

```bash
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

---

## Workflow

```
Document Upload
     │
     ▼
File type detected (PDF / DOCX / Image)
     │
     ├── DOCX ──► extract text + embedded images
     ├── PDF  ──► extract text; if blank → convert to images
     └── Image ─► preprocess (blur/darkness check) → OCR
                                                          │
                                                          ▼
                                               AI extraction (Ollama)
                                               structured JSON output
                                                          │
                                                          ▼
                                               HR reviews & corrects
                                               in the web UI
                                                          │
                                                          ▼
                                               Approve (validates required fields)
                                                          │
                                                          ▼
                                               Generate Contract
                                               (city resolver picks template)
                                                          │
                                                          ▼
                                               DOCX + PDF saved to output/
```

---

## Contract System

The contract resolver automatically picks the right employment contract template based on:

- **City** — Berlin, Wien, Köln group (Hamburg, Frankfurt, Düsseldorf, Bergisch Gladbach)
- **Contract type** — `befristet` (fixed-term) or `unbefristet` (permanent)
- **Occupation** — HSK, NR, STW, public area, hausmann, and more
- **Work schedule** — weekly hours, days per week, daily hours
- **Hotel subgroup** — Adlon or GHB (Berlin unbefristet only)

See [`contract_structure.md`](contract_structure.md) for the full template directory layout and resolver logic.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Employee list dashboard |
| `GET` | `/upload` | New employee form |
| `POST` | `/employees/new` | Create employee from form |
| `POST` | `/api/employees/n8n-intake` | Create employee from n8n (JSON) |
| `GET` | `/review/{id}` | View employee record |
| `GET` | `/review/{id}/edit` | Edit employee form |
| `POST` | `/review/{id}` | Save employee edits |
| `GET` | `/approve-employee/{id}` | Approve employee |
| `GET` | `/reject-employee/{id}` | Reject employee |
| `GET` | `/generate-contract/{id}` | Generate and save contract |
| `GET` | `/download-contract/{id}` | Download latest DOCX |
| `GET` | `/audit-logs` | View audit log UI |
| `GET` | `/api/audit-logs` | Audit logs (JSON) |
| `GET` | `/health` | Health check |

---

## Roadmap

- [ ] Document upload endpoint with full OCR pipeline wired to FastAPI
- [ ] Mistral vision fallback for very poor quality scans
- [ ] Multi-document batch upload per employee
- [ ] Role-based access control (manager vs. admin)
- [ ] Ordio HR system export
- [ ] Email notifications on approval