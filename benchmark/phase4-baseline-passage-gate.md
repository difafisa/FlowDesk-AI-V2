# Phase 4 — Benchmark: passage-gate

Run: 2026-10-07T19:26:52 | generator: deepseek/deepseek-v4.1-flash | jev: jev-latest | top-K=5

## Results

| Metric | Value |
|---|---:|
| Cases | 36 (labeled: 36) |
| Decision accuracy | 78% |
| HitRate@5 | 93% |
| Recall@5 | 0.900 |
| Citation correctness | 100% |
| Citation completeness | 90% |
| Retry rate | 33% |
| Avg Jev calls/query | 7.889 |
| P50 latency (s) | 3.472 |
| P95 latency (s) | 5.640 |

## Per-case decisions

| Case | Expected | Decision | Match | Jev calls | Latency (s) |
|---|---|---|---|---:|---:|
| ret-001 | answered | answered | OK | 6 | 23.285 |
| ret-002 | answered | answered | OK | 6 | 3.701 |
| ret-003 | abstained | abstained | OK | 12 | 2.364 |
| ret-004 | answered | answered | OK | 6 | 5.217 |
| ret-005 | answered | answered | OK | 6 | 3.454 |
| ret-006 | escalated | answered | X | 12 | 5.025 |
| ret-007 | answered | answered | OK | 6 | 5.101 |
| ret-008 | answered | answered | OK | 6 | 3.914 |
| ret-009 | answered | answered | OK | 6 | 4.102 |
| ret-010 | answered | answered | OK | 6 | 4.046 |
| ret-011 | answered | answered | OK | 6 | 4.262 |
| ret-012 | answered | answered | OK | 6 | 2.226 |
| ret-013 | answered | abstained | X | 6 | 5.64 |
| ret-014 | answered | answered | OK | 12 | 4.309 |
| ret-015 | answered | abstained | X | 12 | 1.723 |
| ret-016 | answered | abstained | X | 6 | 5.468 |
| ret-017 | answered | answered | OK | 6 | 5.043 |
| ret-018 | abstained | abstained | OK | 12 | 2.095 |
| ret-019 | answered | answered | OK | 6 | 4.123 |
| ret-020 | answered | answered | OK | 6 | 4.664 |
| ret-021 | answered | abstained | X | 12 | 2.087 |
| ret-022 | answered | answered | OK | 6 | 2.285 |
| ret-023 | abstained | abstained | OK | 12 | 2.086 |
| ret-024 | answered | abstained | X | 6 | 3.11 |
| ret-025 | answered | answered | OK | 6 | 1.939 |
| ret-026 | abstained | abstained | OK | 12 | 2.161 |
| ret-027 | answered | answered | OK | 12 | 5.865 |
| ret-028 | answered | answered | OK | 6 | 2.886 |
| ret-029 | answered | abstained | X | 12 | 2.18 |
| ret-030 | answered | abstained | X | 12 | 2.104 |
| G1 | answered | answered | OK | 6 | 4.662 |
| G2 | answered | answered | OK | 6 | 3.472 |
| G3 | abstained | abstained | OK | 12 | 2.013 |
| G4 | escalated | escalated | OK | 7 | 0.99 |
| G5 | abstained | abstained | OK | 7 | 1.015 |
| G6 | injection_blocked | injection_blocked | OK | 0 | 0.0 |
