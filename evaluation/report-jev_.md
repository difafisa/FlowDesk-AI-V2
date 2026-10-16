# Phase 5 Evaluation — jev

Run: 2026-10-12T09:13:19 | generator: nvidia/nemotron-3-ultra-550b-a55b:free | jev: jev-latest | cases: 51

## Global metrics

| Metric | Value |
|---|---:|
| Decision accuracy | 0.843 |
| Abstention accuracy | 1.0 |
| Escalation accuracy | 0.333 |
| Answered accuracy | 0.829 |
| HitRate@5 | 0.87 |
| Recall@5 | 0.783 |
| Groundedness (mean) | 0.846 (n=30) |
| Correctness | {'correct': 29} |
| Retry rate | 0.353 |
| Jev calls/query (prod) | 8.1 |
| Scorer calls (eval) | 30 |
| P50 / P95 latency (s) | 7.558 / 37.342 |

## Per category

| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |
|---|---:|---:|---:|---:|---:|
| ambiguous | 5 | 1.0 | 1.0 | None | 0.6 |
| api | 6 | 0.833 | None | 0.842 | 0.833 |
| multi_document | 3 | 1.0 | 1.0 | 0.935 | 0.667 |
| policy | 4 | 1.0 | None | 0.912 | 1.0 |
| product_usage | 5 | 0.4 | None | 0.855 | 1.0 |
| safety | 1 | 1.0 | None | None | None |
| simple_factual | 5 | 1.0 | None | 0.948 | 0.8 |
| structured_data | 6 | 0.833 | None | 0.966 | 0.833 |
| troubleshooting | 9 | 0.778 | 1.0 | 0.626 | 1.0 |
| unanswerable | 7 | 0.857 | 1.0 | None | 1.0 |

## Misses (decision != expected)

| Case | Category | Expected | Got |
|---|---|---|---|
| ds-006 | troubleshooting | escalated | answered |
| ds-014 | api | answered | abstained |
| ds-015 | product_usage | answered | abstained |
| ds-021 | product_usage | answered | abstained |
| ds-029 | troubleshooting | answered | abstained |
| ds-030 | structured_data | answered | abstained |
| ds-044 | unanswerable | escalated | abstained |
| ds-049 | product_usage | answered | abstained |

## Low groundedness (< 0.70)

- **ds-006** (troubleshooting): g=0.27 — Kenapa akun FlowDesk saya tiba-tiba terkunci dan apa yang harus saya l
- **ds-012** (api): g=0.64 — What fields make up a FlowDesk customer profile and what procedure sho
- **ds-013** (troubleshooting): g=0.47 — Koneksi API saya kena error 429 Too Many Requests pas jam sibuk, ini k
- **ds-020** (troubleshooting): g=0.41 — When making an API request to GET /v1/tickets/{ticket_id}, I receive a
- **ds-027** (troubleshooting): g=0.63 — Why does my automation rule appear to execute repeatedly on ticket upd
