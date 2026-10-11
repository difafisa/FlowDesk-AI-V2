# Phase 5 Evaluation — llm-judge

Run: 2026-10-11T15:13:45 | generator: deepseek/deepseek-v4.1-flash | jev: jev-latest | cases: 10

## Global metrics

| Metric | Value |
|---|---:|
| Decision accuracy | 0.8 |
| Abstention accuracy | 0.667 |
| Escalation accuracy | 1.0 |
| Answered accuracy | 0.8 |
| HitRate@5 | 0.778 |
| Recall@5 | 0.722 |
| Groundedness (mean) | None (n=0) |
| Correctness | {} |
| Retry rate | 0.2 |
| Jev calls/query (prod) | 1.1 |
| Scorer calls (eval) | 0 |
| P50 / P95 latency (s) | 6.284 / 21.938 |

## Per category

| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |
|---|---:|---:|---:|---:|---:|
| ambiguous | 1 | 0.0 | 0.0 | None | 1.0 |
| api | 1 | 1.0 | None | None | 0.0 |
| multi_document | 1 | 1.0 | 1.0 | None | 0.0 |
| policy | 1 | 1.0 | None | None | 1.0 |
| product_usage | 1 | 0.0 | None | None | 1.0 |
| safety | 1 | 1.0 | None | None | None |
| simple_factual | 1 | 1.0 | None | None | 1.0 |
| structured_data | 1 | 1.0 | None | None | 1.0 |
| troubleshooting | 2 | 1.0 | 1.0 | None | 1.0 |

## Misses (decision != expected)

| Case | Category | Expected | Got |
|---|---|---|---|
| ds-015 | product_usage | answered | abstained |
| ds-037 | ambiguous | abstained | escalated |

## Low groundedness (< 0.70)

(tidak ada)
