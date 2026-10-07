"""Demo CLI Phase 4. Jalankan dari root:  python scripts/ask.py
Set dulu environment variables (atau file .env yang di-load oleh shell):
  LLM_API_KEY, LLM_BASE_URL, LLM_MODEL  -> generator jawaban
  TYPESAFE_API_KEY                      -> Jev (decision gate)
Mode satu-perintah:  python scripts/ask.py "pertanyaan"
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from flowdesk.embedding.embedder import Embedder
from flowdesk.graph.workflow import build_graph, run_workflow
from flowdesk.jev.client import JevClient
from flowdesk.rag.llm_client import LLMClient
from flowdesk.retrieval.retriever import Retriever
from flowdesk.storage.pgvector_store import VectorStore


def make_graph():
    llm = LLMClient(
        base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
        model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
    )
    store = VectorStore("postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")
    retriever = Retriever(store, Embedder())
    return build_graph(llm, JevClient(), retriever)   # Jev asli (TypeSafe Noul)


def print_result(r: dict):
    print(f"\n[{r['status']}] {r['answer']}")
    if r.get("sources"):
        print("sources:", ", ".join(
            f"[{s['index']}] {s['document']}" + (f" p.{s['page']}" if s["page"] else "")
            for s in r["sources"]))
    if r.get("jev"):
        print(f"jev: {r['jev'].get('decision')} — {r['jev'].get('reason')}")


def main():
    graph = make_graph()
    print("FlowDesk Phase 4 demo (LangGraph + Jev asli) — ketik pertanyaan, kosongkan untuk keluar.")
    while True:
        q = input("\nQ: ").strip()
        if not q:
            break
        print_result(run_workflow(graph, q))


if __name__ == "__main__":
    if len(sys.argv) > 1:          # mode satu-perintah
        question = " ".join(sys.argv[1:])
        print_result(run_workflow(make_graph(), question))
    else:
        main()                     # mode interaktif
