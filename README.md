# FlowDesk v2 — AI Knowledge & Support Assistant

RAG support assistant yang tidak hanya menjawab, tetapi tahu kapan harus
menjawab, kapan mencari evidence lagi, dan kapan harus abstain/escalate.
Stack: LangGraph (workflow) + Jev (bounded decision) + pgvector (retrieval)
+ Langfuse (observability) + FastAPI + Docker.

## Progress — MVP COMPLETE
- [x] Phase 1 — Knowledge base (22 docs: MD/PDF/CSV/JSON, 5 kategori)
- [x] Phase 2 — Ingestion, structure-aware chunking, pgvector retrieval
      Eval: Hit Rate@5 93%/93% (EN/ID), 30 test cases, bge-m3 vs e5-base
- [x] Phase 3 — Basic RAG, context control & guardrails
      deepseek-v4.1-flash: 28/30 answered, citation rate 79%, manual gate 8/8 PASS
- [x] Phase 4 — LangGraph + Jev decision layer
      Passage gate (3 Noul/chunk, paralel + cache antar gelombang),
      completeness check, scope check, citation verifier; 36-case gate A/B
- [x] Phase 5 — Evaluation (51 kasus, 9 kategori PRD + safety)
      RAG+LLM vs RAG+LLM+Jev: decision acc 0.725 → 0.863,
      abstention 0.083 → 0.750 — detail: evaluation/comparison.md
- [x] Phase 6 — Observability + feedback
      Langfuse (trace/span/generation/session) + 👍/👎 → Postgres + score
- [x] Phase 7 — Testing + Docker
      146 test di 8 kategori PRD (unit + integration);
      `docker compose up` = Frontend + Backend + PostgreSQL end-to-end

## Menjalankan

    docker compose up -d
    # UI       -> http://localhost:8080
    # API docs -> http://localhost:8000/docs
    # re-ingest KB (mis. dokumen berubah):
    docker compose run -e INGEST_FORCE=1 ingest

Dev tanpa Docker: `python scripts/serve.py` (db lokal + .env).
Test: `python -m pytest tests/ -q` (integration auto-skip tanpa DB).
Regression gate: `python scripts/check_regression.py` (exit 1 = regresi).

## Hasil A/B Phase 5 (ringkas)

| Metrik | RAG+LLM | RAG+LLM+Jev |
|---|---:|---:|
| Decision accuracy | 0.725 | **0.863** |
| Abstention accuracy | 0.083 | **0.750** |
| Answered accuracy | 0.914 | 0.917 |
| HitRate@5 (kontrol retrieval) | 0.87 | 0.87 |
| Jev calls/query | 1.08 | 7.29 |

Kesimpulan: layer Jev mengubah sistem dari "gagal berbahaya" (menjawab
tanpa evidence cukup) menjadi "gagal aman" (abstain saat evidence kurang),
dengan biaya ~6.7× panggilan Jev. Analisis lengkap: evaluation/comparison.md.

## Known issues / backlog
Lengkap di evaluation/BACKLOG.md. Teratas:
- S1 — kalibrasi over-abstain (troubleshooting/product_usage/structured_data)
- S3 — scope_check kasus komersial (ds-044) → escalation accuracy 0.5
- S5 — verifikasi label dataset; S7 — Jev calls counter; S8 — early exit
- 7.5-residual — UI menampilkan sources pada jawaban abstained;
  cold-start container ~1–2 menit (muat model embedding)
