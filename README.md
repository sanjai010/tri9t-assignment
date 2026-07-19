# Tri9T AI Engineering Assignment — CT-200 Document API

## Setup

```bash
git clone https://github.com/sanjai010/tri9t-assignment
cd tri9t-assignment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Ingest Documents

```bash
python -m app.ingest data/ct200_manual.pdf
python -m app.ingest data/ct200_manual_v2.pdf
```

## Run API

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs

## Run Tests

```bash
python -m pytest tests/ -v
```

## API Endpoints

- `GET /sections?version=1` — list top-level sections
- `GET /nodes/{id}` — get node with children
- `GET /search?q=cuff` — search headings and body
- `GET /nodes/{id}/diff` — compare node across versions

## Key Design Decisions

- PDF parsed using pdfplumber — preserves text order
- Section 3.3 appears after 3.4 in PDF — parser preserves this intentionally
- Section 2.1.1.1 skips hierarchy — parented to nearest ancestor (2.1)
- Duplicate "Error Codes" heading (4.2 and 7.1) — two distinct nodes with different parents
- Content hash (MD5) used for staleness detection between versions