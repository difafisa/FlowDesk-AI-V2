# Phase 5 Evaluation — llm-judge

Run: 2026-10-12T11:01:27 | generator: nvidia/nemotron-3-ultra-550b-a55b | jev: jev-latest | cases: 51

## Global metrics

| Metric | Value |
|---|---:|
| Decision accuracy | 0.725 |
| Abstention accuracy | 0.083 |
| Escalation accuracy | 1.0 |
| Answered accuracy | 0.914 |
| HitRate@5 | 0.87 |
| Recall@5 | 0.783 |
| Groundedness (mean) | 0.847 (n=36) |
| Correctness | {'correct': 31, 'partial': 1} |
| Retry rate | 0.137 |
| Jev calls/query (prod) | 1.12 |
| Scorer calls (eval) | 36 |
| P50 / P95 latency (s) | 18.407 / 45.404 |

## Per category

| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |
|---|---:|---:|---:|---:|---:|
| ambiguous | 5 | 0.0 | 0.0 | 0.745 | 0.6 |
| api | 6 | 1.0 | None | 0.863 | 0.833 |
| multi_document | 3 | 0.667 | 0.0 | 0.94 | 0.667 |
| policy | 4 | 1.0 | None | 0.85 | 1.0 |
| product_usage | 5 | 0.6 | None | 0.86 | 1.0 |
| safety | 1 | 1.0 | None | None | None |
| simple_factual | 5 | 1.0 | None | 0.944 | 0.8 |
| structured_data | 6 | 0.833 | None | 0.966 | 0.833 |
| troubleshooting | 9 | 0.889 | 0.0 | 0.71 | 1.0 |
| unanswerable | 7 | 0.429 | 0.2 | 0.73 | 1.0 |

## Misses (decision != expected)

| Case | Category | Expected | Got |
|---|---|---|---|
| ds-003 | troubleshooting | abstained | answered |
| ds-015 | product_usage | answered | escalated |
| ds-018 | multi_document | abstained | escalated |
| ds-023 | unanswerable | abstained | answered |
| ds-030 | structured_data | answered | abstained |
| ds-035 | unanswerable | abstained | escalated |
| ds-037 | ambiguous | abstained | escalated |
| ds-038 | ambiguous | abstained | answered |
| ds-039 | ambiguous | abstained | escalated |
| ds-040 | ambiguous | abstained | answered |
| ds-041 | ambiguous | abstained | escalated |
| ds-042 | unanswerable | abstained | escalated |
| ds-043 | unanswerable | abstained | escalated |
| ds-049 | product_usage | answered | abstained |

## Low groundedness (< 0.70)

- **ds-013** (troubleshooting): g=0.4 — Koneksi API saya kena error 429 Too Many Requests pas jam sibuk, ini k
- **ds-014** (api): g=0.63 — What HTTP status code and error code are returned when an API request 
- **ds-017** (policy): g=0.69 — Apakah tagihan perpanjangan langganan bulanan (subscription renewal) b
- **ds-020** (troubleshooting): g=0.63 — When making an API request to GET /v1/tickets/{ticket_id}, I receive a
- **ds-027** (troubleshooting): g=0.35 — Why does my automation rule appear to execute repeatedly on ticket upd
- **ds-038** (ambiguous): g=0.54 — How do I reset it?
