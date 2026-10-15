"""Phase 7 — Jalankan backend API.

Pakai:
    python scripts/serve.py                 # http://localhost:8000 (docs: /docs)
    set PORT=9000 && python scripts/serve.py  # port lain
    set DEV_RELOAD=1 && python scripts/serve.py  # auto-reload saat develop

Prasyarat (sama seperti scripts/ask.py):
    docker compose up -d db   +   .env berisi LLM_API_KEY, LLM_BASE_URL,
    LLM_MODEL, TYPESAFE_API_KEY
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "flowdesk.api.app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEV_RELOAD", "") == "1",
    )
