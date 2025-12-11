from typing import List, Dict
from app.db.vector_store import VectorStore


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def load_subject(subject_id: str, items: List[Dict[str, str]], store: VectorStore):
    payload = []
    idx = 0
    for it in items:
        for ch in chunk_text(it["text"]):
            payload.append({
                "id": f"{subject_id}-{idx}",
                "text": ch,
                "metadata": {"subject_id": subject_id, "source": it["source"]}
            })
            idx += 1
    store.upsert(collection_name=subject_id, items=payload)
