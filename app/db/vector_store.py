from typing import List, Dict, Any
import os
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    HAS_CHROMA = True
except Exception:
    HAS_CHROMA = False


class VectorStore:
    def __init__(self, persist_directory: str = "data/chroma"):
        self.persist_directory = persist_directory
        if HAS_CHROMA:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        else:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.base = Path("data/vectors")
            self.base.mkdir(parents=True, exist_ok=True)

    def get_collection(self, name: str):
        if HAS_CHROMA:
            return self.client.get_or_create_collection(name=name, embedding_function=self.embedding_fn)
        return name

    def upsert(self, collection_name: str, items: List[Dict[str, Any]]):
        if HAS_CHROMA:
            collection = self.get_collection(collection_name)
            ids = [i["id"] for i in items]
            documents = [i["text"] for i in items]
            metadatas = [i.get("metadata", {}) for i in items]
            collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
            return
        docs = [i["text"] for i in items]
        metas = [i.get("metadata", {}) for i in items]
        embs = self.model.encode(docs, normalize_embeddings=True)
        path = self.base / f"{collection_name}.npz"
        if path.exists():
            data = np.load(path, allow_pickle=True)
            prev_docs = list(data["docs"]) + docs
            prev_metas = list(data["metas"]) + metas
            prev_embs = np.vstack([data["embs"], embs])
            np.savez(path, docs=np.array(prev_docs, dtype=object), metas=np.array(prev_metas, dtype=object), embs=prev_embs)
        else:
            np.savez(path, docs=np.array(docs, dtype=object), metas=np.array(metas, dtype=object), embs=embs)

    def query(self, collection_name: str, text: str, n_results: int = 5):
        if HAS_CHROMA:
            collection = self.get_collection(collection_name)
            result = collection.query(query_texts=[text], n_results=n_results, include=["metadatas", "documents", "distances"])
            items = []
            for i in range(len(result["documents"][0])):
                items.append({
                    "text": result["documents"][0][i],
                    "metadata": result["metadatas"][0][i],
                    "score": float(result["distances"][0][i])
                })
            return items
        path = Path("data/vectors") / f"{collection_name}.npz"
        if not path.exists():
            return []
        data = np.load(path, allow_pickle=True)
        docs = list(data["docs"]) 
        metas = list(data["metas"]) 
        embs = data["embs"]
        q = self.model.encode([text], normalize_embeddings=True)[0]
        sims = np.dot(embs, q)
        idxs = np.argsort(-sims)[:n_results]
        items = []
        for i in idxs:
            items.append({"text": str(docs[i]), "metadata": dict(metas[i]), "score": float(sims[i])})
        return items
