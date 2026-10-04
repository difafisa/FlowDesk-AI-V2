# scripts/debug_ret018.py
import sys; sys.path.insert(0, "src")
from flowdesk.embedding.embedder import Embedder
from flowdesk.retrieval.retriever import Retriever
from flowdesk.storage.pgvector_store import VectorStore

store = VectorStore("postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")
r = Retriever(store, Embedder())
for label, q in [
    ("ID (asli)", "Bagaimana cara kerja aksi send_webhook pada automasi FlowDesk dan paket langganan minimal apa yang dibutuhkan?"),
    ("EN (padanan)", "How does the send_webhook automation action work in FlowDesk and what plan is required for it?"),
    ("ID (topik tunggal)", "Aksi automation apa saja yang mendukung trigger ticket.created?"),
]:
    print("\n===", label, "===")
    for i, h in enumerate(r.retrieve(q, k=20), 1):
        mark = " <<<" if ("automation" in h["document"] or "feature-comparison" in h["document"]) else ""
        print("#%2d  %.4f  %-38s | %s%s" % (i, h["dist"], h["document"],
              (h["subsection"] or h["section"] or "")[:40], mark))
