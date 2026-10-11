# Phase 5 Evaluation — jev

Run: 2026-10-10T09:29:00 | generator: deepseek/deepseek-v4.1-flash | jev: jev-latest | cases: 6

## Global metrics

| Metric | Value |
|---|---:|
| Decision accuracy | 0.833 |
| Abstention accuracy | 1.0 |
| Escalation accuracy | 0.0 |
| Answered accuracy | 1.0 |
| HitRate@5 | 0.833 |
| Recall@5 | 0.833 |
| Groundedness (mean) | 0.852 (n=6) |
| Correctness | {'correct': 4} |
| Retry rate | 0.333 |
| Jev calls/query (prod) | 8 |
| Scorer calls (eval) | 6 |
| P50 / P95 latency (s) | 3.036 / 26.892 |

## Per category

| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |
|---|---:|---:|---:|---:|---:|
| api | 2 | 1.0 | None | 0.795 | 0.5 |
| simple_factual | 1 | 1.0 | None | 0.97 | 1.0 |
| structured_data | 1 | 1.0 | None | 0.94 | 1.0 |
| troubleshooting | 2 | 0.5 | 1.0 | 0.805 | 1.0 |

## Misses (decision != expected)

| Case | Category | Expected | Got |
|---|---|---|---|
| ds-006 | troubleshooting | escalated | answered |

## Low groundedness (< 0.70)

- **ds-003** (troubleshooting): g=0.69 — Why am I not getting webhook deliveries to my configured server endpoi
- **ds-004** (api): g=0.65 — Bagaimana cara melakukan autentikasi pada FlowDesk API dan format head
