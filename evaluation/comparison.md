# Phase 5 — Evaluation: RAG+LLM vs RAG+LLM+Jev

## Objective
Membuktikan (bukan mengasumsikan) nilai tambah Jev decision layer
pada dataset 51 kasus, 9 kategori PRD — metrik decision, generation,
cost, dan latency pada retrieval & generator yang identik.

## Setup
- Dataset: 51 kasus (9 kategori + safety), expected labels
- Generator: nvidia/nemotron-3-ultra-550b-a55b (identik kedua varian)
- Retrieval: multilingual-e5-base + pgvector, top-K=5 (identik)
- Varian A (RAG+LLM): single-judge LLM (prompt JSON + regex parse) — run 2026-10-12
- Varian B (RAG+LLM+Jev): passage gate + completeness + scope check — run 2026-10-13
- Groundedness di-scorer dengan Jev pada kedua varian; karena scorer
  ditambah post-hoc, angka generation dibaca indikatif (bukan head-to-head ketat)

## Results

| Metric | RAG+LLM | RAG+LLM+Jev | Δ |
|---|---:|---:|---:|
| Decision accuracy | 0.725 | 0.863 | +0.138 |
| Abstention accuracy | 0.083 | 0.750 | +0.667 |
| Escalation accuracy | 1.0 | 0.5 | −0.5 |
| Answered accuracy | 0.914 | 0.917 | +0.003 |
| Groundedness (mean) | 0.843* | 0.847 | ~0 (*indikatif) |
| Correctness | 30 correct + 2 partial | 32 correct | +2 |
| HitRate@5 | 0.87 | 0.87 | 0 (kontrol) |
| Recall@5 | 0.783 | 0.793 | +0.010 |
| Retry rate | 0.098 | 0.216 | +0.118 |
| Jev calls/query | 1.08 | 7.29 | +6.21 |
| P50 latency (s) | 14.526 | 9.887 | −4.639 |
| P95 latency (s) | 38.331 | 38.635 | +0.304 |

## Findings

### Improved
- Abstention 0.083 → 0.750: baseline menjawab paksa atau meng-escalate
  pertanyaan yang seharusnya abstain — 14 miss, seluruh kategori ambiguous
  jatuh ke 0.0. Varian Jev menahan diri (7 miss; ambiguous 0.8).
  Contoh nyata: ds-003 (webhook deliveries) dijawab baseline, ditahan Jev.
- Decision accuracy +13.8 poin persentase (0.725 → 0.863).
- P50 lebih cepat (9.9s vs 14.5s) meski calls lebih banyak — passage gate
  dieksekusi paralel per chunk, single-judge serial.
- Correctness 32 correct vs 30 (+2 partial).

### Regressions
- Escalation accuracy 1.0 → 0.5: ds-044 (pertanyaan on-premise komersial)
  di-abstain padahal expected escalate — scope_check belum menangkap kasus
  komersial (BACKLOG S3).
- Over-abstain di troubleshooting/product_usage/structured_data
  (ds-024, ds-029, ds-030) — kandidat kalibrasi threshold (BACKLOG S1).

### Trade-offs
- Biaya: 7.29 vs 1.08 Jev calls/query (~6.7×).
- Retry rate naik (0.098 → 0.216); P95 setara (~38s).

## Conclusion
Layer Jev mengubah kegagalan sistem dari "gagal berbahaya" (menjawab tanpa
evidence cukup) menjadi "gagal aman" (abstain dan minta retry/escalate),
dengan biaya ~6.7× panggilan Jev dan presisi escalation yang masih perlu
kalibrasi (S1, S3).
