"""Multilingual embedding dengan intfloat/multilingual-e5-base (768 dim, dense).
e5 WAJIB prefix 'query:'/'passage:' — keduanya sudah diterapkan di bawah.
(BAAI/bge-m3, 1024d tanpa prefix, adalah kandidat alternatif Phase 2 yang
kalah pada eval retrieval — dipertahankan sebagai catatan eksperimen.)"""

from sentence_transformers import SentenceTransformer

MODEL = "intfloat/multilingual-e5-base"   # baseline terpilih Phase 2 (768d);
                                          # alternatif teruji: BAAI/bge-m3 (1024d, tanpa prefix)

class Embedder:
    def __init__(self, model_name: str = MODEL):
        self.model = SentenceTransformer(model_name) 
        self.dim = self.model.get_embedding_dimension()   # 1024 utk bge-m3

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(
            [f"passage: {t}" for t in texts],
            normalize_embeddings=True,
            show_progress_bar=True).tolist()

    def embed_query(self, query: str) -> list[float]:
        return self.model.encode(
            [f"query: {query}"], normalize_embeddings=True).tolist()[0]

