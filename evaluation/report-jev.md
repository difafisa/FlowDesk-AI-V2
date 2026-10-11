# Phase 5 Evaluation — jev

Run: 2026-10-11T15:32:48 | generator: deepseek/deepseek-v4.1-flash | jev: jev-latest | cases: 10

## Global metrics

| Metric | Value |
|---|---:|
| Decision accuracy | 0.4 |
| Abstention accuracy | 1.0 |
| Escalation accuracy | 0.0 |
| Answered accuracy | 0.0 |
| HitRate@5 | 0.778 |
| Recall@5 | 0.722 |
| Groundedness (mean) | None (n=0) |
| Correctness | {} |
| Retry rate | 0.0 |
| Jev calls/query (prod) | 6.3 |
| Scorer calls (eval) | 0 |
| P50 / P95 latency (s) | 1.435 / 11.683 |

## Per category

| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |
|---|---:|---:|---:|---:|---:|
| ambiguous | 1 | 1.0 | 1.0 | None | 1.0 |
| api | 1 | 0.0 | None | None | 0.0 |
| multi_document | 1 | 1.0 | 1.0 | None | 0.0 |
| policy | 1 | 0.0 | None | None | 1.0 |
| product_usage | 1 | 0.0 | None | None | 1.0 |
| safety | 1 | 1.0 | None | None | None |
| simple_factual | 1 | 0.0 | None | None | 1.0 |
| structured_data | 1 | 0.0 | None | None | 1.0 |
| troubleshooting | 2 | 0.5 | 1.0 | None | 1.0 |

## Misses (decision != expected)

| Case | Category | Expected | Got |
|---|---|---|---|
| ds-001 | api | answered | abstained |
| ds-002 | structured_data | answered | abstained |
| ds-005 | simple_factual | answered | abstained |
| ds-006 | troubleshooting | escalated | abstained |
| ds-007 | policy | answered | abstained |
| ds-015 | product_usage | answered | abstained |

## Low groundedness (< 0.70)

(tidak ada)
