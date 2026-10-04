"""Retrieval pipeline baseline: vector search -> optional rerank."""
from flowdesk.embedding.embedder import Embedder
from flowdesk.storage.pgvector_store import VectorStore

class Retriever:
    def __init__(self, store: VectorStore, embedder: Embedder):
        self.store, self.embedder = store, embedder

    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        qvec = self.embedder.embed_query(query)
        return self.store.search(qvec, k=k)
        # Reranker (bge-reranker-v2-m3) ditambahkan SETELAH baseline dievaluasi.
