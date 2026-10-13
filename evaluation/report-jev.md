# Phase 5 Evaluation — jev

Run: 2026-10-13T08:24:52 | generator: nvidia/nemotron-3-ultra-550b-a55b | jev: jev-latest | cases: 51

## Global metrics

| Metric | Value |
|---|---:|
| Decision accuracy | 0.863 |
| Abstention accuracy | 0.75 |
| Escalation accuracy | 0.5 |
| Answered accuracy | 0.917 |
| HitRate@5 | 0.87 |
| Recall@5 | 0.793 |
| Groundedness (mean) | 0.847 (n=36) |
| Correctness | {'correct': 32} |
| Retry rate | 0.216 |
| Jev calls/query (prod) | 7.29 |
| Scorer calls (eval) | 36 |
| P50 / P95 latency (s) | 9.887 / 38.635 |

## Per category

| Category | n | Decision acc | Abstention | Groundedness | HitRate@5 |
|---|---:|---:|---:|---:|---:|
| ambiguous | 5 | 0.8 | 0.8 | 0.9 | 0.4 |
| api | 6 | 1.0 | None | 0.902 | 0.833 |
| multi_document | 3 | 0.667 | 0.0 | 0.877 | 0.667 |
| policy | 4 | 1.0 | None | 0.863 | 1.0 |
| product_usage | 5 | 1.0 | None | 0.748 | 1.0 |
| safety | 1 | 1.0 | None | None | None |
| simple_factual | 5 | 1.0 | None | 0.93 | 1.0 |
| structured_data | 6 | 0.833 | None | 0.97 | 0.833 |
| troubleshooting | 9 | 0.778 | 1.0 | 0.713 | 1.0 |
| unanswerable | 7 | 0.714 | 0.8 | 0.59 | 1.0 |

## Misses (decision != expected)

| Case | Category | Expected | Got |
|---|---|---|---|
| ds-018 | multi_document | abstained | answered |
| ds-023 | unanswerable | abstained | answered |
| ds-024 | troubleshooting | answered | abstained |
| ds-029 | troubleshooting | answered | abstained |
| ds-030 | structured_data | answered | abstained |
| ds-038 | ambiguous | abstained | answered |
| ds-044 | unanswerable | escalated | abstained |

## Low groundedness (< 0.70)

- **ds-006** (troubleshooting): g=0.37 — Kenapa akun FlowDesk saya tiba-tiba terkunci dan apa yang harus saya l
- **ds-013** (troubleshooting): g=0.62 — Koneksi API saya kena error 429 Too Many Requests pas jam sibuk, ini k
- **ds-017** (policy): g=0.67 — Apakah tagihan perpanjangan langganan bulanan (subscription renewal) b
- **ds-023** (unanswerable): g=0.59 — Apa rekomendasi terbaik dalam penamaan tag profil pelanggan dan penggu
- **ds-027** (troubleshooting): g=0.69 — Why does my automation rule appear to execute repeatedly on ticket upd
- **ds-049** (product_usage): g=0.37 — Bagaimana cara menutup (close) tiket di FlowDesk setelah masalah pelan
