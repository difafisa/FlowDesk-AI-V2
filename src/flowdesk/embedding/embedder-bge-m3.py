"""Multilingual embedding dengan BAAI/bge-m3 (1024 dim, dense).
bge-m3 TIDAK butuh prefix 'query:'/'passage:' — jangan ditambahkan."""
from sentence_transformers import SentenceTransformer

MODEL = "BAAI/bge-m3"          # alternatif baseline: intfloat/multilingual-e5-base (768d)

class Embedder:
    def __init__(self, model_name: str = MODEL):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_embedding_dimension()   # 1024 utk bge-m3

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(
            texts,
            normalize_embeddings=True,     # penting: wajib normalize utk cosine
            show_progress_bar=True).tolist()

    def embed_query(self, query: str) -> list[float]:
        return self.model.encode(
            [query], normalize_embeddings=True).tolist()[0]
