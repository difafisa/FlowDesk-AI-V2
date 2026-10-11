# Phase 5 — Evaluation: RAG+LLM vs RAG+LLM+Jev

## Objective
Membuktikan (bukan mengasumsikan) nilai tambah Jev decision layer
pada dataset 51 kasus, 9 kategori PRD — metrik decision, generation,
cost, dan latency pada retrieval & generator yang identik.

## Setup
- Dataset: 51 kasus (9 kategori + safety), expected labels
- Generator: deepseek/deepseek-v4.1-flash (identik kedua varian)
- Retrieval: bge-m3 + pgvector, top-K=5 (identik)
- Varian A (RAG+LLM): legacy single-judge LLM (prompt JSON + regex parse)
- Varian B (RAG+LLM+Jev): hybrid passage gate + completeness + scope check
- Groundedness: Jev-scored, hanya varian B (scorer ditambah post-hoc;
  perbandingan A/B generation ditandai not-compared)

## Results

| Metric | RAG+LLM | RAG+LLM+Jev | Δ |
|---|---:|---:|---:|
| Decision accuracy | <-> | <-> | <-> |
| Abstention accuracy | <-> | <-> | <-> |
| Escalation accuracy | <-> | <-> | <-> |
| Answered accuracy | <-> | <-> | <-> |
| Groundedness (mean) | not compared | <-> | — |
| HitRate@5 | <-> | <-> | 0 (kontrol) |
| Jev calls/query | <-> | <-> | <-> |
| P50 latency (s) | <-> | <-> | <-> |
| P95 latency (s) | <-> | <-> | <-> |

## Findings

### Improved
- <dari data: abstention, ambiguous class, dsb.>

### Regressions
- <dari data: over-abstain di product_usage/troubleshooting, dsb.>

### Trade-offs
- <cost 8.1 vs 1.08 calls, P95, dsb.>

## Conclusion
The Jev decision layer ... <1-2 kalimat: "gagal aman vs gagal berbahaya">
