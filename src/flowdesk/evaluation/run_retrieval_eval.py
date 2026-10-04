"""Hit Rate@K dan Recall@K untuk matrix multilingual (PRD 2.9).
Output hanya angka hasil eksekusi aktual."""
from flowdesk.embedding.embedder import Embedder
import json
from pathlib import Path
from flowdesk.retrieval.retriever import Retriever
from flowdesk.storage.pgvector_store import VectorStore

def _norm(s: str) -> str:
    return Path(s).as_posix().lower()

def evaluate(retriever: Retriever, testset: list[dict], k: int = 5):
    buckets: dict[str, dict] = {}
    for case in testset:
        hits = retriever.retrieve(case["question"], k=k)
        got = {_norm(h["document"]) for h in hits}
        expected = {_norm(s) for s in case["expected_sources"]}
        found = got & expected
        doc_ranks = {}
        for i, h in enumerate(hits):
            doc = _norm(h["document"])
            if doc in expected and doc not in doc_ranks:
                doc_ranks[doc] = i + 1
        ranks_str = ",".join(f"{Path(d).name}={r}" for d, r in sorted(doc_ranks.items(), key=lambda x: x[1])) or "N/A"
        print(f"{case['id']}\t{case['lang']}\t{'Y' if found else 'N'}\tranks={ranks_str}\trecall={len(found)}/{len(expected)}")


        key = case["lang"]          # atau matrix penuh via field 'doc_lang'
        b = buckets.setdefault(key, {"hit": 0, "recall": 0.0, "n": 0})
        b["n"] += 1
        if found: b["hit"] += 1
        b["recall"] += len(found) / len(expected)
    print(f"K={k}")
    for lang, b in sorted(buckets.items()):
        print(f"{lang}: HitRate@{k}={b['hit']/b['n']:.0%}  Recall@{k}={b['recall']/b['n']:.3f}  (n={b['n']})")

if __name__ == "__main__":
    import psycopg
    store = VectorStore("postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")
    retr = Retriever(store, Embedder())
    CASES_PATH = Path(__file__).parent / "retrieval_testset.json"
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    evaluate(retr, cases, k=5)
