import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.models.schemas import ChatRequest, ChatResponse
from app.etl.extract import extract_from_paths, extract_from_urls
from app.etl.transform import transform
from app.etl.load import load_subject
from app.db.vector_store import VectorStore
from app.rag.retriever import Retriever
from app.style.style import compose_reply
from app.voice.tts import synthesize_elevenlabs
from app.storage.facts import save as save_facts_style, load as load_facts_style


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
static_dir = Path("static")
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
store = VectorStore()
retriever = Retriever(store)


@app.get("/", response_class=HTMLResponse)
def index():
    html = Path("static/index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.post("/ingest/sample")
async def ingest_sample(subject_id: str = Form(...)):
    base = Path("data/sample_subject")
    paths = [base / "bio.txt", base / "preferences.txt", base / "writing_sample.txt"]
    items = extract_from_paths(paths)
    mf, style = transform(subject_id, items)
    save_facts_style(subject_id, mf, style)
    load_subject(subject_id, items, store)
    return {"facts_count": len(mf.facts), "preferences_count": len(mf.preferences), "tone": style.tone}


@app.post("/ingest/files")
async def ingest_files(subject_id: str = Form(...), files: List[UploadFile] = File(None)):
    paths = []
    upload_dir = Path("uploads") / subject_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    if files:
        for f in files:
            p = upload_dir / f.filename
            content = await f.read()
            p.write_bytes(content)
            paths.append(p)
    items = extract_from_paths(paths)
    mf, style = transform(subject_id, items)
    save_facts_style(subject_id, mf, style)
    load_subject(subject_id, items, store)
    return {"facts_count": len(mf.facts), "preferences_count": len(mf.preferences), "tone": style.tone}


@app.post("/ingest/urls")
async def ingest_urls(subject_id: str = Form(...), urls: List[str] = Form([])):
    items = extract_from_urls(urls, readability=True)
    mf, style = transform(subject_id, items)
    save_facts_style(subject_id, mf, style)
    load_subject(subject_id, items, store)
    return {"facts_count": len(mf.facts), "preferences_count": len(mf.preferences), "tone": style.tone}


@app.post("/chat")
async def chat(req: ChatRequest) -> ChatResponse:
    items = retriever.search(req.subject_id, req.message, k=5)
    mf, style = load_facts_style(req.subject_id)
    reply = compose_reply(req.message, style=style, items=items)
    audio_url = None
    if req.voice and req.voice_id:
        out = synthesize_elevenlabs(reply, req.voice_id, Path("audio") / req.subject_id)
        audio_url = f"/static/{Path(out).name}" if out else None
        if out:
            dst = Path("static") / Path(out).name
            if not dst.exists():
                dst.write_bytes(Path(out).read_bytes())
    citations = [{"source": it.metadata.get("source", ""), "snippet": it.text[:200]} for it in items]
    return ChatResponse(reply=reply, citations=citations, audio_url=audio_url)


def __style_default(subject_id: str):
    from app.models.schemas import StyleGuide
    return StyleGuide(subject_id=subject_id, tone="neutral", writing_examples=[], response_tips=["be concise", "cite sources", "mirror phrasing"])


@app.get("/facts/{subject_id}")
def get_facts(subject_id: str):
    mf, style = load_facts_style(subject_id)
    return {"facts": [f.model_dump() for f in mf.facts], "preferences": [p.model_dump() for p in mf.preferences], "style": style.model_dump()}


@app.post("/facts/{subject_id}")
def update_facts(subject_id: str, payload: dict):
    from app.models.schemas import MirrorFacts, StyleGuide
    mf = MirrorFacts(subject_id=subject_id, facts=[
        
    ], preferences=[])
    facts = payload.get("facts", [])
    prefs = payload.get("preferences", [])
    style_in = payload.get("style")
    mf.facts = [
        
    ]
    for f in facts:
        from app.models.schemas import Fact
        mf.facts.append(Fact(**f))
    for p in prefs:
        from app.models.schemas import Preference
        mf.preferences.append(Preference(**p))
    style = None
    if style_in:
        style = StyleGuide(**style_in)
    else:
        _, style = load_facts_style(subject_id)
    save_facts_style(subject_id, mf, style)
    return {"ok": True, "facts_count": len(mf.facts), "preferences_count": len(mf.preferences)}
