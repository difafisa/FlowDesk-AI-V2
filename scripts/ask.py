"""Demo CLI Phase 3. Jalankan dari root:  python scripts/ask.py
Set dulu environment variables (atau file .env yang di-load oleh shell):
  LLM_API_KEY  = key provider-mu
  LLM_BASE_URL = https://api.openai.com/v1  (default) / https://openrouter.ai/api/v1
                 / http://localhost:11434/v1 (Ollama)
  LLM_MODEL    = gpt-4o-mini / model lain sesuai provider
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()   
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from flowdesk.embedding.embedder import Embedder
from flowdesk.rag.llm_client import LLMClient
from flowdesk.rag.pipeline import run_pipeline
from flowdesk.retrieval.retriever import Retriever
from flowdesk.storage.pgvector_store import VectorStore


def main():
    llm = LLMClient(
        base_url=os.environ.get("LLM_BASE_URL"),
        model=os.environ.get("LLM_MODEL"),
    )
    store = VectorStore("postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")
    retriever = Retriever(store, Embedder())

    print("FlowDesk Phase 3 demo — ketik pertanyaan, kosongkan untuk keluar.")
    while True:
        q = input("\nQ: ").strip()
        if not q:
            break
        r = run_pipeline(llm, retriever, q)
        print(f"\n[{r.status}] {r.answer}")
        if r.sources:
            print("sources:", ", ".join(
                f"[{s['index']}] {s['document']}" + (f" p.{s['page']}" if s["page"] else "")
                for s in r.sources))


if __name__ == "__main__":
    if len(sys.argv) > 1:          # mode satu-perintah: python ask.py "pertanyaan"
        question = " ".join(sys.argv[1:])
        llm = LLMClient(base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
                        model=os.environ.get("LLM_MODEL", "gpt-4o-mini"))
        store = VectorStore("postgresql://flowdesk:flowdesk@localhost:5432/flowdesk")
        retr = Retriever(store, Embedder())
        r = run_pipeline(llm, retr, question)
        print(f"\n[{r.status}] {r.answer}")
        if r.sources:
            print("sources:", ", ".join(f"[{s['index']}] {s['document']}" for s in r.sources))
    else:
        main()                      # mode interaktif seperti biasa

