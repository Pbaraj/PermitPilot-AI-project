# PermitPilot AI

**PermitPilot AI** is a Munich-focused, multilingual, multi-agent permit document review assistant. It helps users upload an engineering or building-permit PDF, extract important project information, check document completeness, retrieve Munich/Bavaria regulation context, and generate a preliminary readiness report.

The current MVP focuses on **Munich / Lokalbaukommission (LBK)** because building permit requirements are highly jurisdiction-specific. The system is built in a modular way so that other jurisdictions can be added later through new checklist, regulation, and RAG knowledge files.

> **Important:** PermitPilot AI is a preliminary document-screening and decision-support tool. It does **not** approve permits, does **not** provide legal advice, and does **not** replace review by a qualified architect, engineer, lawyer, Prüfingenieur, or permitting authority.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Why Munich / Lokalbaukommission?](#why-munich--lokalbaukommission)
- [Key Features](#key-features)
- [Current Demo Result](#current-demo-result)
- [System Architecture](#system-architecture)
- [Multi-Agent Workflow](#multi-agent-workflow)
- [GenAI + RAG Workflow](#genai--rag-workflow)
- [LLM Provider Support](#llm-provider-support)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [How to Use the App](#how-to-use-the-app)
- [Example Output](#example-output)
- [Screenshots](#screenshots)
- [Security and Data Privacy](#security-and-data-privacy)
- [Recommended .gitignore](#recommended-gitignore)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [MCP Readiness](#mcp-readiness)
- [Interview Explanation](#interview-explanation)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Project Overview

PermitPilot AI reviews uploaded permit or engineering PDFs and produces a structured readiness report. It is designed to help applicants, students, engineers, and reviewers identify missing or unclear documents before a formal building-permit submission.

The app currently supports:

- PDF text extraction
- German document handling
- Language detection
- Internal translation
- Munich/LBK checklist validation
- Evidence extraction from uploaded PDFs
- Evidence quality labels
- Regulation matching
- Local RAG retrieval over Munich/Bavaria regulation knowledge
- Hugging Face LLM reviewer
- Rule-based fallback reviewer
- Markdown report export
- Formatted PDF report export

---

## Why Munich / Lokalbaukommission?

Building permit requirements differ strongly by city, state, and procedure. A broad “global permit checker” would be too shallow for a serious MVP.

Therefore, this project focuses on:

```text
Munich / Lokalbaukommission
Bavaria-related building document requirements
Munich permit document completeness screening
```

The Munich focus makes the project more realistic because the app can use:

- Munich/LBK-specific checklist items
- Bavaria/Munich regulation references
- Munich-relevant RAG context
- German-English permit terminology
- Practical missing-document risk analysis

The architecture is still extensible. Other cities can be added later by creating new:

```text
checklist JSON files
regulation rule JSON files
RAG knowledge base files
jurisdiction mapping logic
```

---

## Key Features

### 1. PDF Upload and Text Extraction

The backend extracts text from uploaded PDFs using PyMuPDF. Each page is processed and stored with page number, raw text, detected language, and normalized text.

### 2. Multilingual Document Processing

The app detects the language of the uploaded PDF. If the document is German, it can translate extracted text internally for the downstream review workflow.

Current tested case:

```text
Input document language: German
Detected language: de
Translation: German → English
```

### 3. Munich/LBK Checklist Review

The checklist agent checks whether required Munich/LBK-related documents are present or missing.

Example checklist items:

- Application form / Antragsformular
- Project name / Bauvorhaben
- Project address / Baugrundstück
- Applicant / Bauherr or Antragsteller
- Designer / Entwurfsverfasser
- Official site plan / Amtlicher Lageplan
- Building drawings / Bauzeichnungen
- Floor plans / Grundrisse
- Sections and elevations / Schnitte und Ansichten
- Building description / Baubeschreibung
- Construction statistics form / Statistischer Erhebungsbogen
- Structural stability proof / Standsicherheitsnachweis
- Fire safety proof / Brandschutznachweis
- Energy / GEG documentation
- Drainage plan / Entwässerungsplan
- Signatures / Unterschriften

### 4. Evidence Quality Detection

The app does not only check if a keyword appears. It also distinguishes between positive and negative evidence.

Evidence quality labels include:

```text
Found with evidence
Mentioned as missing
Not found
Unclear / conditional
```

Example:

```text
Das Brandschutzkonzept und der Energieausweis sind nicht beigefügt.
```

The system correctly treats this as:

```text
Fire safety proof: Missing
Evidence quality: Mentioned as missing

Energy / GEG documentation: Missing
Evidence quality: Mentioned as missing
```

### 5. Risk Analysis

The risk agent highlights missing or unclear documents and assigns severity levels.

High-priority examples:

- Fire safety proof missing
- Energy / GEG documentation missing
- Drainage plan missing
- Building drawings missing
- Sections/elevations missing

### 6. Munich/Bavaria Regulation Matching

The regulation matching agent links checklist results to Munich/Bavaria references and notes.

Example matched references:

```text
BauVorlV §7 - Site plan / Lageplan
BauVorlV §8 - Building drawings / Bauzeichnungen
BauVorlV §9 - Building description / Baubeschreibung
BauVorlV §11 - Fire safety proof / Brandschutznachweis
Munich LBK building application guidance
Munich digital building application guidance
```

### 7. Local RAG Retrieval

PermitPilot AI retrieves relevant Munich/Bavaria regulation context from a local knowledge base.

For each retrieved context, the report shows:

```text
Title
Source
Relevance score
Matched query
Retrieved context
```

Example retrieved RAG chunks:

- BauVorlV §11 - Fire safety proof / Brandschutznachweis
- BauVorlV §8 - Building drawings / Bauzeichnungen
- BauVorlV §9 - Building description / Baubeschreibung
- Tree stock declaration / Baumbestandserklärung
- Statistical survey form / Statistischer Erhebungsbogen
- Munich LBK application documents

### 8. Hugging Face LLM Reviewer

The LLM reviewer uses the checklist results, missing items, regulation matches, risks, and RAG context to create a concise AI screening decision.

Current tested provider:

```text
LLM provider: huggingface
LLM model: deepseek-ai/DeepSeek-V4-Pro:fastest
```

### 9. Fallback Reviewer

If the cloud LLM fails, returns invalid JSON, or is disabled, the app automatically uses a deterministic fallback reviewer. This makes the app more robust and safe for demos.

### 10. Markdown and PDF Export

The final report can be downloaded as:

```text
Markdown report
Formatted PDF report
```

The PDF report includes:

- Header
- Page numbers
- Document overview
- Project summary
- AI screening decision
- Readiness score
- Checklist completeness table
- Regulation matching table
- Retrieved RAG context
- Risk notes
- Recommended next steps
- Disclaimer

---

## Current Demo Result

Test file:

```text
SampleG.pdf
```

Demo result:

```text
Permit Readiness: 47%
Detected language: de
Reviewer mode: Hugging Face LLM reviewer
LLM provider: huggingface
LLM model: deepseek-ai/DeepSeek-V4-Pro:fastest
RAG context: Munich/Bavaria regulation context retrieved
```

The AI reviewer identified the document set as incomplete and highlighted missing high-priority items such as:

```text
Fire safety proof / Brandschutznachweis
Energy / GEG documentation
Drainage plan / Entwässerungsplan
Building drawings / Bauzeichnungen
Sections and elevations / Schnitte und Ansichten
Building description / Baubeschreibung
Application form / Antragsformular
Designer / Entwurfsverfasser
Construction statistics form / Statistischer Erhebungsbogen
```

---

## System Architecture

```text
PDF Upload
    ↓
PDF Extraction Service
    ↓
Language Detection
    ↓
Translation Agent
    ↓
Document Reader Agent
    ↓
Checklist Agent
    ↓
Regulation Matching Agent
    ↓
RAG Regulation Agent
    ↓
Risk Agent
    ↓
LLM Review Agent
    ↓
Report Writer Agent
    ↓
Reviewer Notes Agent
    ↓
Output Translation Agent
    ↓
Markdown / PDF Report + Frontend UI
```

---

## Multi-Agent Workflow

PermitPilot AI is implemented as a multi-agent workflow. Each agent has a clear responsibility.

### Translation Agent

Handles internal translation when the uploaded PDF is not already in English.

### Document Reader Agent

Extracts project-level information such as project name, project address, applicant/client, and building type/use.

### Checklist Agent

Checks document completeness against the selected jurisdiction checklist.

### Regulation Matching Agent

Maps checklist items to Munich/Bavaria regulation references.

### RAG Regulation Agent

Retrieves relevant regulation context from the local Munich/Bavaria knowledge base.

### Risk Agent

Creates missing-document and submission-risk items.

### LLM Review Agent

Uses the review state, RAG context, and checklist results to produce an AI screening decision.

### Report Writer Agent

Generates the final Markdown report.

### Reviewer Agent

Adds general reviewer notes.

### Output Translation Agent

Can translate the final report into the selected output language.

---

## GenAI + RAG Workflow

PermitPilot AI uses a hybrid architecture:

```text
Rule-based document checking
+
Evidence extraction
+
Local RAG retrieval
+
LLM reviewer
+
Fallback safety logic
```

The RAG component retrieves supporting Munich/Bavaria context, then the LLM reviewer uses this retrieved context to explain why missing documents may matter.

The LLM is not allowed to approve or reject permits. It only creates a preliminary screening decision.

---

## LLM Provider Support

The backend supports multiple LLM backends through `llm_service.py`.

Priority order:

```text
1. Hugging Face Inference Providers
2. OpenRouter
3. Ollama local LLM
4. OpenAI
5. Rule-based fallback reviewer
```

Current tested provider:

```text
Hugging Face
Model: deepseek-ai/DeepSeek-V4-Pro:fastest
```

Optional providers:

```text
OpenRouter: openai/gpt-oss-120b:free
Ollama: llama3.2:3b
OpenAI: gpt-4.1-mini
```

If no LLM provider is enabled, the app still works using the fallback reviewer.

---

## Tech Stack

### Backend

```text
Python
FastAPI
Pydantic
PyMuPDF
langdetect
Argos Translate
ReportLab
python-dotenv
Hugging Face Inference Providers
OpenRouter optional
Ollama optional
OpenAI optional
```

### Frontend

```text
React
Vite
JavaScript
CSS
Fetch API
```

### Architecture Style

```text
Multi-agent workflow
Rule-based validation
Local RAG retrieval
Cloud/local LLM integration
Human-in-the-loop decision support
```

---

## Project Structure

```text
permitpilot-ai/
│
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── checklist_agent.py
│       │   ├── document_reader_agent.py
│       │   ├── llm_review_agent.py
│       │   ├── output_translation_agent.py
│       │   ├── rag_regulation_agent.py
│       │   ├── regulation_match_agent.py
│       │   ├── report_writer_agent.py
│       │   ├── reviewer_agent.py
│       │   ├── risk_agent.py
│       │   └── translation_agent.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── argos_translation_service.py
│       │   ├── language_service.py
│       │   ├── llm_service.py
│       │   ├── pdf_report_service.py
│       │   ├── pdf_service.py
│       │   ├── rag_service.py
│       │   └── text_normalizer.py
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── permit_schema.py
│       │   └── report_schema.py
│       │
│       ├── workflows/
│       │   ├── __init__.py
│       │   └── permit_workflow.py
│       │
│       └── data/
│           ├── checklists/
│           │   ├── general_permit_checklist.json
│           │   ├── germany_building_permit_checklist.json
│           │   ├── germany_bavaria_munich_checklist.json
│           │   └── munich_lbk_checklist.json
│           │
│           ├── regulations/
│           │   └── munich_lbk_rules.json
│           │
│           └── regulation_knowledge/
│               └── munich_lbk_knowledge.json
│
└── frontend/
    ├── package.json
    ├── index.html
    │
    └── src/
        ├── App.jsx
        ├── api.js
        ├── main.jsx
        ├── style.css
        │
        └── components/
            ├── UploadBox.jsx
            └── ReportViewer.jsx
```

---

## Backend Setup

### 1. Go to the backend folder

```powershell
cd C:\BABU\CV\CV\permitpilot-ai\backend
```

### 2. Create or activate Conda environment

```powershell
conda create -n permitpilot python=3.11
conda activate permitpilot
```

If the environment already exists:

```powershell
conda activate permitpilot
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create `.env`

Create:

```text
backend/.env
```

Use the environment variable template shown below.

### 5. Run backend

```powershell
uvicorn app.main:app --reload
```

Backend API docs:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

### 1. Go to frontend folder

```powershell
cd C:\BABU\CV\CV\permitpilot-ai\frontend
```

### 2. Install dependencies

```powershell
npm install
```

### 3. Run frontend

```powershell
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## Environment Variables

Create:

```text
backend/.env
```

Example:

```env
# Hugging Face cloud LLM
USE_HUGGINGFACE=true
HF_TOKEN=your_huggingface_token_here
HF_MODEL=deepseek-ai/DeepSeek-V4-Pro:fastest
HF_BASE_URL=https://router.huggingface.co/v1

# OpenRouter cloud LLM
USE_OPENROUTER=false
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=openai/gpt-oss-120b:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Optional local LLM
USE_OLLAMA=false
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434

# Optional OpenAI
USE_OPENAI=false
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4.1-mini
```

For safer local-only mode:

```env
USE_HUGGINGFACE=false
USE_OPENROUTER=false
USE_OLLAMA=false
USE_OPENAI=false
```

This disables cloud LLM calls and uses the rule-based fallback reviewer.

---

## API Endpoints

### Review Permit PDF

```http
POST /api/review-permit
```

Form data:

```text
file: PDF file
output_language: English, German, French, etc.
jurisdiction: general, germany, bavaria, munich
```

Returns:

```text
filename
detected_languages
translation_notes
project_summary
checklist_results
risks
readiness_score
reviewer_notes
final_report_markdown
```

### Download PDF Report

```http
POST /api/download-report-pdf
```

JSON body:

```json
{
  "filename": "permit-review-report.pdf",
  "markdown": "final markdown report text"
}
```

Returns:

```text
application/pdf
```

---

## How to Use the App

1. Start the backend.
2. Start the frontend.
3. Open the frontend in the browser.
4. Upload a permit or engineering PDF.
5. Select report language.
6. Select jurisdiction.

Recommended demo setting:

```text
Report language: English
Jurisdiction: Munich / Lokalbaukommission
```

7. Click **Review document**.
8. Review:
   - Permit readiness score
   - AI screening decision
   - Translation notes
   - Project summary
   - Missing required items
   - Checklist results
   - Munich regulation matching
   - Retrieved Munich regulation context
   - Risk analysis
9. Download Markdown or PDF report.

---

## Example Output

Example from German sample document:

```text
Permit Readiness: 47%
Detected language: de
Reviewer mode: Hugging Face LLM reviewer
LLM provider: huggingface
LLM model: deepseek-ai/DeepSeek-V4-Pro:fastest
RAG context: Munich/Bavaria regulation context retrieved
```

Example AI screening decision:

```text
Preliminary review: Document set is incomplete; several required items are missing,
including fire safety proof, energy documentation, and drainage plan.
Submission not yet ready for formal review.
```

Example priority actions:

```text
1. Provide fire safety proof (Brandschutznachweis)
2. Provide energy/GEG documentation
3. Provide drainage plan (Entwässerungsplan)
```

---

## Screenshots

Add screenshots to:

```text
docs/screenshots/
```

Recommended screenshots:

```text
1. Upload screen
2. AI Screening Decision with Hugging Face reviewer
3. Checklist Results with Evidence Quality
4. Retrieved Munich Regulation Context
5. PDF Report Preview
```

Example Markdown:

```markdown
![Upload screen](docs/screenshots/upload-screen.png)
![AI Screening Decision](docs/screenshots/ai-screening.png)
![Checklist Results](docs/screenshots/checklist-results.png)
![RAG Context](docs/screenshots/rag-context.png)
![PDF Report](docs/screenshots/pdf-report.png)
```

---

## Security and Data Privacy

Real permit documents may contain:

```text
Names
Addresses
Property information
Signatures
Technical drawings
Engineering data
Legal or administrative information
```

Be careful when using cloud LLM providers.

Cloud mode can send document-derived text to external services such as:

```text
Hugging Face
OpenRouter
OpenAI
```

For confidential or client documents, use one of these safer options:

```text
Use local-only fallback mode
Use local Ollama mode
Anonymize personal data before upload
Get permission from the document owner/client
Do not upload sensitive documents to public demos
```

Never commit real API keys.

Do not push:

```text
backend/.env
frontend/.env
```

Use `.env.example` instead.

---

## Recommended .gitignore

```gitignore
# Environment files
.env
backend/.env
frontend/.env

# Python
__pycache__/
*.pyc
.venv/
venv/
.env/

# Node
node_modules/
dist/

# Local reports and temporary outputs
*.pdf
*.docx
*.tmp

# Keep main docs
!README.md
```

---

## Limitations

PermitPilot AI has important limitations:

- It is not an official permit submission system.
- It does not approve or reject permits.
- It does not provide legal advice.
- It does not replace qualified professional review.
- It may miss information if the PDF text extraction is poor.
- It may not handle scanned PDFs unless OCR is added.
- It currently focuses mainly on Munich/LBK.
- Regulation knowledge is simplified for MVP purposes.
- Cloud LLM output may vary by provider and model.
- RAG context supports screening but does not replace official legal text.

---

## Future Improvements

Possible next steps:

```text
Add OCR support for scanned permit PDFs
Add ChromaDB or FAISS vector database for stronger RAG
Add source citations with official document URLs
Add confidence scores for checklist detection
Add more Munich/LBK document types
Add Bavaria-wide mode
Add Berlin/Hamburg jurisdiction modules
Add admin panel for checklist editing
Add user authentication
Add project history database
Add Docker setup
Add deployment on Azure/GCP/AWS
Add optional MCP server for exposing agents as tools
Add automated tests
Add CI/CD with GitHub Actions
```

---

## MCP Readiness

The current system does not need MCP for the MVP, but it is structurally ready for it.

Future MCP tools could expose:

```text
extract_pdf_text()
detect_language()
run_checklist_review()
retrieve_regulation_context()
run_llm_review()
generate_pdf_report()
```

This would allow external AI clients to call PermitPilot tools through a standardized tool interface.

---

## Disclaimer

PermitPilot AI is an AI-assisted preliminary screening tool. It is not legal advice, not an official permit decision, and not a replacement for qualified professional or authority review.

Final verification and permit decisions must remain with the responsible human authority, architect, engineer, legal expert, or qualified reviewer.

---

## License

This project is intended for educational, portfolio, and demonstration purposes.

Add your preferred license here, for example:

```text
MIT License
```
