# Phase 5 Evaluation — llm-judge

Run: 2026-10-12T12:17:11 | generator: nvidia/nemotron-3-ultra-550b-a55b | jev: jev-latest | cases: 51

## Global metrics

| Metric | Value |
|---|---:|
| Decision accuracy | 0.725 |
| Abstention accuracy | 0.083 |
| Escalation accuracy | 1.0 |
| Answered accuracy | 0.914 |
| HitRate@5 | 0.87 |
| Recall@5 | 0.783 |
| Groundedness (mean) | 0.843 (n=36) |
| Correctness | {'correct': 30, 'partial': 2} |
| Retry rate | 0.098 |
| Jev calls/query (prod) | 1.08 |
| Scorer calls (eval) | 36 |
| P50 / P95 latency (s) | 14.526 / 38.331 |

## Per category

| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |
|---|---:|---:|---:|---:|---:|
| ambiguous | 5 | 0.0 | 0.0 | 0.83 | 0.6 |
| api | 6 | 1.0 | None | 0.877 | 0.833 |
| multi_document | 3 | 0.667 | 0.0 | 0.955 | 0.667 |
| policy | 4 | 1.0 | None | 0.87 | 1.0 |
| product_usage | 5 | 0.6 | None | 0.833 | 1.0 |
| safety | 1 | 1.0 | None | None | None |
| simple_factual | 5 | 1.0 | None | 0.93 | 0.8 |
| structured_data | 6 | 0.833 | None | 0.97 | 0.833 |
| troubleshooting | 9 | 0.889 | 0.0 | 0.664 | 1.0 |
| unanswerable | 7 | 0.429 | 0.2 | 0.74 | 1.0 |

## Misses (decision != expected)

| Case | Category | Expected | Got |
|---|---|---|---|
| ds-003 | troubleshooting | abstained | answered |
| ds-015 | product_usage | answered | abstained |
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

- **ds-003** (troubleshooting): g=0.66 — Why am I not getting webhook deliveries to my configured server endpoi
- **ds-013** (troubleshooting): g=0.68 — Koneksi API saya kena error 429 Too Many Requests pas jam sibuk, ini k
- **ds-014** (api): g=0.68 — What HTTP status code and error code are returned when an API request 
- **ds-020** (troubleshooting): g=0.38 — When making an API request to GET /v1/tickets/{ticket_id}, I receive a
- **ds-027** (troubleshooting): g=0.11 — Why does my automation rule appear to execute repeatedly on ticket upd
