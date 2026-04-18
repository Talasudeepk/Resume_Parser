# AI Resume Parser

AI Resume Parser is a full-stack application that uploads PDF or DOCX resumes, extracts text, and returns structured candidate data. The backend is built with FastAPI and spaCy-powered parsing, while the frontend provides a polished Vite React interface for upload, preview, and export workflows.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React, Vite, Axios, react-syntax-highlighter, jsPDF |
| Backend | FastAPI, Uvicorn, python-multipart, pdfplumber, python-docx |
| NLP / Parsing | spaCy (`en_core_web_sm`), regex-based field extraction |

## Prerequisites

- Node.js 18+
- Python 3.11+
- spaCy English model: `en_core_web_sm`

## Setup

### Backend

```powershell
cd C:\Resume_parser
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
Copy-Item .env.example .env
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```powershell
cd C:\Resume_parser\frontend
npm install
Copy-Item .env.example .env
npm run dev
```

## API Reference

### `POST /upload`

Uploads a resume file and returns structured parsed data.

#### Request

- Content type: `multipart/form-data`
- Field: `file`
- Supported types: `.pdf`, `.docx`
- Max size: `10MB`

Example request with `curl`:

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@resume.pdf"
```

#### Success Response

```json
{
  "filename": "resume.pdf",
  "file_type": "pdf",
  "parsed": {
    "name": "John Doe",
    "email": ["john@example.com"],
    "phone": ["+1-9999999999"],
    "skills": ["Python", "React"]
  }
}
```

#### Error Response

```json
{
  "error": true,
  "message": "Only PDF and DOCX files are supported.",
  "code": "UNSUPPORTED_TYPE"
}
```

## Screenshots
<img width="1881" height="937" alt="image" src="https://github.com/user-attachments/assets/50f6efd1-cb1d-48c3-9b77-ff4f624aa856" />

<img width="1859" height="940" alt="image" src="https://github.com/user-attachments/assets/6fc09802-4cbe-4245-b7da-4e9258f62b2e" />


## Known Limitations

- Image-based or scanned resumes may return limited or empty structured data.
- DOCX files do not currently have an in-browser preview panel.
- Parsing is rule-based for contact details and skills, so unusual resume formats can reduce accuracy.

## License

MIT
