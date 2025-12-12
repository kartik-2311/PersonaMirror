# PersonaMirror

PersonaMirror is a local-first toolkit to build a personalized AI "Mirror" of an individual from their own data, then chat with it using grounded retrieval and optional voice output.

## Features

- ETL pipeline to ingest `.txt`, `.md`, `.pdf`, `.docx`, and URLs (readability extraction)
- Structured transform to `MirrorFacts` and `StyleGuide` with provenance
- Local vector store with Chroma when available, otherwise a simple NPZ-based fallback
- Chat UI with citations and optional ElevenLabs TTS voice responses
- Facts Browser/Editor to curate and persist personal facts and preferences

## Architecture

- Backend: `FastAPI` (`app/main.py`)
- ETL: `app/etl/extract.py`, `app/etl/transform.py`, `app/etl/load.py`
- Vector store: `app/db/vector_store.py` (Chroma or NPZ fallback)
- Retrieval: `app/rag/retriever.py`
- Style composition: `app/style/style.py`
- Voice: `app/voice/tts.py` (ElevenLabs)
- Persistence: `app/storage/facts.py`
- Frontend: `static/index.html`, `static/app.js`, `static/styles.css`

## Quick Start (Windows)

1. Create a virtual environment and install dependencies

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

2. Run the dev server with autoreload

```
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

3. Open the UI

- Visit `http://127.0.0.1:8000/`
- Load the sample mirror via the "Load Sample Mirror" section
- Start chatting, view citations, optionally enable voice

## Using the UI

- Load Sample Mirror
  - Enter a subject id (e.g., `sample`) and click `Load`
- Ingest Files
  - Enter a subject id and select `.txt`, `.md`, `.pdf`, `.docx` files
- Ingest URLs
  - Use the `/ingest/urls` endpoint (from code or a simple form you add) — readability extraction is enabled by default
- Chat
  - Enter the subject id and a message; optionally provide an ElevenLabs `voice_id` and enable `Voice`
- Facts Browser
  - Load facts for a subject, edit inline, add/delete, and save

## API Reference

- `POST /ingest/sample` — Ingests built-in sample files
  - Form fields: `subject_id`
- `POST /ingest/files` — Ingest uploaded files
  - Form fields: `subject_id`, `files[]`
- `POST /ingest/urls` — Ingest from URLs with readability extraction
  - Form fields: `subject_id`, `urls[]`
- `POST /chat` — Chat with the Mirror
  - JSON body: `{ "subject_id": "sample", "message": "...", "voice": false, "voice_id": null }`
- `GET /facts/{subject_id}` — Retrieve facts, preferences, style
- `POST /facts/{subject_id}` — Replace facts and preferences (style preserved unless supplied)

Key implementation references:
- Chat handling: `app/main.py:72`
- Facts API: `app/main.py:94`
- Extractors: `app/etl/extract.py:7`
- Vector fallback logic: `app/db/vector_store.py:1`

## Data & Storage

- Uploads: `uploads/<subject_id>/`
- Vector store
  - Chroma: `data/chroma/`
  - Fallback NPZ: `data/vectors/<subject_id>.npz`
- Facts and style JSON
  - Facts: `data/facts/<subject_id>.json`
  - Style: `data/style/<subject_id>.json`
- Sample data: `data/sample_subject/`

## Configuration

- ElevenLabs TTS API key
  - Set environment variable `ELEVENLABS_API_KEY`
  - Provide `voice_id` in the UI for speech responses

## Troubleshooting

- `lxml.html.clean` import error
  - Installed `lxml_html_clean`; ensure `requirements.txt` is up to date and re-run install
- Chroma not found
  - The system falls back to NPZ vectors automatically; to use Chroma, keep it installed
- Windows PowerShell `Invoke-WebRequest` prompts
  - Use `-UseBasicParsing` to avoid script execution warnings in local tests

## Development Notes

- The transform step is currently heuristic; you can swap in LLM-assisted parsers later for richer fact extraction and style modeling
- Retrieval uses `SentenceTransformer('all-MiniLM-L6-v2')`; change model in `app/db/vector_store.py` as needed
- Keep sensitive data local; review the `data/` directory layout and deletion practices for privacy

## Roadmap

- LLM-assisted transform with provenance scoring
- Multilingual ingestion and ASR/TTS for Indic languages
- Rich style emulation/fine-tuning and persona controls
- PDF table and resume section-aware parsing
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1
 --port 8000 --reload
