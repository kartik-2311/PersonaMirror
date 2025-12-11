from typing import List
from app.db.vector_store import VectorStore
from app.models.schemas import RetrievedItem


class Retriever:
    def __init__(self, store: VectorStore):
        self.store = store

    def search(self, subject_id: str, query: str, k: int = 5) -> List[RetrievedItem]:
        items = self.store.query(collection_name=subject_id, text=query, n_results=k)
        return [RetrievedItem(text=i["text"], metadata=i["metadata"], score=i["score"]) for i in items]
