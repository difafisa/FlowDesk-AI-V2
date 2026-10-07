# Phase 4 — Benchmark: baseline

Run: 2026-10-07T11:10:17 | generator: deepseek/deepseek-v4.1-flash | jev: jev-latest | top-K=5

## Results

| Metric | Value |
|---|---:|
| Cases | 6 (labeled: 6) |
| Decision accuracy | 100% |
| HitRate@5 | ... |
| Recall@5 | ... |
| Citation correctness | 100% |
| Citation completeness | 100% |
| Retry rate | 17% |
| Avg Jev calls/query | 1 |
| P50 latency (s) | 2.107 |
| P95 latency (s) | 34.423 |

## Per-case decisions

| Case | Expected | Decision | Match | Jev calls | Latency (s) |
|---|---|---|---|---:|---:|
| G1 | answered | answered | OK | 1 | 34.423 |
| G2 | answered | answered | OK | 1 | 9.382 |
| G3 | abstained | abstained | OK | 2 | 2.107 |
| G4 | escalated | escalated | OK | 1 | 2.216 |
| G5 | escalated | escalated | OK | 1 | 0.977 |
| G6 | injection_blocked | injection_blocked | OK | 0 | 0.0 |
