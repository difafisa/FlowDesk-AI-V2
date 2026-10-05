## Progress
- [x] Phase 1 — Knowledge base (22 docs: MD/PDF/CSV/JSON)
- [x] Phase 2 — Ingestion, structure-aware chunking, pgvector retrieval
      Eval: Hit Rate@5 93%/93% (EN/ID), 30 test cases, bge-m3 vs e5-base
- [x] Phase 3 — Basic RAG, context control & guardrails
      Baseline RAG+LLM (deepseek-v4.1-flash via OpenRouter): 28/30 answered,
      citation rate 79%, avg latency 4.5s; manual gate 8/8 PASS
- [ ] Phase 4 — LangGraph + Jev decision layer

## Known issues (backlog berbasis bukti)
- Citation spam (multi-citation per klaim) → penyaringan via Jev (Phase 4)
- Duplikasi dokumen di top-5 → dedupe per-document saat context assembly
- Multi-intent query (ret-018, S3 partial answer) → query rewriting (Improvement 03)
- Reasoning model kadang terpotong (S8 "Flow") → reasoning budget config
