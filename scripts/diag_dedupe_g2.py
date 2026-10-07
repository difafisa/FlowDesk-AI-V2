"""Diag hipotesis G2 — apakah dedupe per dokumen membuang chunk harga Pro?
Read-only: hanya SELECT via retriever + print. Tidak menulis apa pun."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from dotenv import load_dotenv
load_dotenv()

from flowdesk.embedding.embedder import Embedder
from flowdesk.retrieval.retriever import Retriever
from flowdesk.storage.pgvector_store import VectorStore

Q = "Berapa harga paket Pro dan berapa rate limit API-nya?"

store = VectorStore(os.environ.get(
    "FLOWDESK_DSN", "postgresql://flowdesk:flowdesk@localhost:5432/flowdesk"))
chunks = Retriever(store, Embedder()).retrieve(Q, k=10)

seen = set()
n_price, n_price_kept = 0, 0
print(f"{'#':>2} {'dedupe':<6} {'chunk_id':<24} {'document':<20} snippet")
for i, ch in enumerate(chunks, 1):
    low = ch["content"].lower()
    is_price = ("pro" in low and any(
        s in low for s in ("price", "harga", "$", "per month", "/mo")))
    kept = ch["document"] not in seen
    seen.add(ch["document"])
    n_price += is_price
    n_price_kept += (is_price and kept)
    snip = ch["content"].replace("\n", " ")[:55]
    print(f"{i:>2} {'KEEP' if kept else 'DROP':<6} {str(ch['chunk_id'])[:23]:<24} "
          f"{str(ch['document'])[:19]:<20} {snip}")

print(f"\nchunk 'harga Pro' di top-10 : {n_price}")
print(f"yang lolos dedupe           : {n_price_kept}")
if n_price > n_price_kept:
    print(">>> HIPOTESIS TERBUKTI: dedupe membuang chunk harga Pro")
else:
    print(">>> dedupe TIDAK membuangnya — penyebab G2 ada di tempat lain")
