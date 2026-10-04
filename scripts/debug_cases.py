# scripts/debug_cases.py — lihat top-5 untuk kasus gagal
import sys; sys.path.insert(0, "src")
from flowdesk.embedding.embedder import Embedder
from flowdesk.retrieval.retriever import Retriever
from flowdesk.storage.pgvector_store import VectorStore

store = VectorStore("postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")
r = Retriever(store, Embedder())
for q in ["Does the Pro plan support webhooks for ticket.created?",
          "How can I automatically assign newly created tickets to specific agents using workflow automation?",
          "Bagaimana cara kerja aksi send_webhook pada automasi FlowDesk dan paket langganan minimal apa yang dibutuhkan?"]:
    print("\nQ:", q)
    for h in r.retrieve(q, k=5):
        print(f"  {h['dist']:.4f}  {h['document']}  | {h['subsection'] or h['section']}")
