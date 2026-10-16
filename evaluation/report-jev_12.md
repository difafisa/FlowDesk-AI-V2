# Phase 5 Evaluation — jev

Run: 2026-10-12T08:58:30 | generator: nvidia/nemotron-3-ultra-550b-a55b:free | jev: jev-latest | cases: 13

## Global metrics

| Metric | Value |
|---|---:|
| Decision accuracy | 0.846 |
| Abstention accuracy | 1.0 |
| Escalation accuracy | 0.0 |
| Answered accuracy | 0.857 |
| HitRate@5 | 0.833 |
| Recall@5 | 0.792 |
| Groundedness (mean) | 0.839 (n=7) |
| Correctness | {'correct': 6} |
| Retry rate | 0.462 |
| Jev calls/query (prod) | 8.31 |
| Scorer calls (eval) | 7 |
| P50 / P95 latency (s) | 9.783 / 44.336 |

## Per category

| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |
|---|---:|---:|---:|---:|---:|
| ambiguous | 1 | 1.0 | 1.0 | None | 1.0 |
| api | 2 | 1.0 | None | 0.9 | 0.5 |
| multi_document | 1 | 1.0 | 1.0 | None | 0.0 |
| policy | 1 | 1.0 | None | 0.95 | 1.0 |
| product_usage | 1 | 0.0 | None | None | 1.0 |
| safety | 1 | 1.0 | None | None | None |
| simple_factual | 1 | 1.0 | None | 0.94 | 1.0 |
| structured_data | 1 | 1.0 | None | 0.95 | 1.0 |
| troubleshooting | 3 | 0.667 | 1.0 | 0.615 | 1.0 |
| unanswerable | 1 | 1.0 | 1.0 | None | 1.0 |

## Misses (decision != expected)

| Case | Category | Expected | Got |
|---|---|---|---|
| ds-006 | troubleshooting | escalated | answered |
| ds-015 | product_usage | answered | abstained |

## Low groundedness (< 0.70)

- **ds-006** (troubleshooting): g=0.42 — Kenapa akun FlowDesk saya tiba-tiba terkunci dan apa yang harus saya l
