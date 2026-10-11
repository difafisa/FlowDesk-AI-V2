# Phase 5 Backlog (known issues — ter-track, sengaja ditunda)

| # | Item | Alasan ditunda | Kapan |
|---|---|---|---|
| S1 | Kalibrasi over-abstain (answered acc; 10 false-abstain product_usage/troubleshooting; kandidat evidence_min 0.55->0.45, completeness 0.75->0.65) | Eksperimen iteratif mahal; tak menahan Phase 6 | Setelah Phase 6/7 |
| S2 | calibration-notes.md + kunci threshold final + JEV_MODEL versi | Ikut S1 | Bareng S1 |
| S3 | scope_check utk kasus komersial (ds-044 on-premise -> harus escalate) | 1 kasus/51; fallback aman | Bareng S1 |
| S4 | Regression check (check_regression.py + ambang) | Nilai penuh saat CI ada | Phase 7 |
| S5 | Verifikasi label dataset: ds-006 (kandidat answered), klaim angka expected_answer (12-months, 3-retries, base URL) | Rerun dataset berubah tak valid | Sebelum eval besar berikutnya |
| S6 | ~~Duplikat ds-018/ds-033~~ DONE (dataset final 51 kasus) | — | — |
| S7 | Jev calls counter akurat (hitung di JevClient, bukan estimasi trace) | Estimasi trace cukup utk laporan | Sebelum laporan final portofolio |
| S8 | Early exit T3 + need_more dead code (warisan audit Phase 4) | Optimasi; perilaku sudah benar | Post-MVP improvement |
