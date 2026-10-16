# Phase 5 Evaluation — llm-judge

Run: 2026-10-12T08:34:10 | generator: nvidia/nemotron-3-ultra-550b-a55b:free | jev: jev-latest | cases: 13

## Global metrics

| Metric | Value |
|---|---:|
| Decision accuracy | 0.615 |
| Abstention accuracy | 0.0 |
| Escalation accuracy | 1.0 |
| Answered accuracy | 0.857 |
| HitRate@5 | 0.833 |
| Recall@5 | 0.792 |
| Groundedness (mean) | 0.89 (n=8) |
| Correctness | {'correct': 6} |
| Retry rate | 0.0 |
| Jev calls/query (prod) | 0.92 |
| Scorer calls (eval) | 8 |
| P50 / P95 latency (s) | 29.724 / 69.055 |

## Per category

| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |
|---|---:|---:|---:|---:|---:|
| ambiguous | 1 | 0.0 | 0.0 | None | 1.0 |
| api | 2 | 1.0 | None | 0.9 | 0.5 |
| multi_document | 1 | 0.0 | 0.0 | None | 0.0 |
| policy | 1 | 1.0 | None | 0.95 | 1.0 |
| product_usage | 1 | 0.0 | None | None | 1.0 |
| safety | 1 | 1.0 | None | None | None |
| simple_factual | 1 | 1.0 | None | 0.96 | 1.0 |
| structured_data | 1 | 1.0 | None | 0.97 | 1.0 |
| troubleshooting | 3 | 0.667 | 0.0 | 0.815 | 1.0 |
| unanswerable | 1 | 0.0 | 0.0 | 0.81 | 1.0 |

## Misses (decision != expected)

| Case | Category | Expected | Got |
|---|---|---|---|
| ds-003 | troubleshooting | abstained | answered |
| ds-015 | product_usage | answered | escalated |
| ds-018 | multi_document | abstained | escalated |
| ds-023 | unanswerable | abstained | answered |
| ds-037 | ambiguous | abstained | escalated |

## Low groundedness (< 0.70)

(tidak ada)
