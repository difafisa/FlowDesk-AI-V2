# Phase 6 T4 — Debugging view: akar masalah per miss

Dibuat: 2026-10-13T08:25:57 — klasifikasi digabung dengan label dataset TERKINI

## Label berubah sejak run (transparansi)

| Case | Label saat run | Label kini |
|---|---|---|
| ds-006 | escalated | answered |

## Varian jev (run 2026-10-13T08:24:52, generator nvidia/nemotron-3-ultra-550b-a55b)

### Distribusi akar masalah

| Akar masalah | Jumlah | Tindakan yang disarankan |
|---|---:|---|
| gate_miss | 3 | S1 — kalibrasi threshold (evidence_min 0.55->0.45, completeness 0.75->0.65) |
| gate_too_loose | 3 | PERIKSA MANUAL — mode gagal berbahaya (menjawab tanpa dasar) |
| scope_miss | 1 | S3 — kalibrasi scope_check / routing escalate |

### Detail miss

| Case | Kategori | Expected | Got | Akar | hit@5 | groundedness | retried | Pertanyaan |
|---|---|---|---|---|---:|---:|---|---|
| ds-024 | troubleshooting | answered | abstained | gate_miss | 1.0 | - | ya | Browser saya mental terus balik ke halaman login setiap habis masukin  |
| ds-029 | troubleshooting | answered | abstained | gate_miss | 1.0 | - | ya | We are getting throttled during high traffic on the Pro tier—what is t |
| ds-030 | structured_data | answered | abstained | gate_miss | 1.0 | - | ya | Apa perbedaan fitur pelaporan antara Standard Reporting dan Advanced A |
| ds-018 | multi_document | abstained | answered | gate_too_loose | 0.0 | 0.76 | ya | Bagaimana cara kerja aksi send_webhook pada automasi FlowDesk dan pake |
| ds-023 | unanswerable | abstained | answered | gate_too_loose | 1.0 | 0.59 | ya | Apa rekomendasi terbaik dalam penamaan tag profil pelanggan dan penggu |
| ds-038 | ambiguous | abstained | answered | gate_too_loose | 1.0 | 0.9 | tidak | How do I reset it? |
| ds-044 | unanswerable | escalated | abstained | scope_miss | - | - | tidak | Apakah pelanggan dapat membeli opsi instalasi FlowDesk secara on-premi |
### Kualitas (keputusan benar, jawaban perlu perhatian)

- **ds-006** (troubleshooting): low_groundedness(0.37) — Kenapa akun FlowDesk saya tiba-tiba terkunci dan apa yang harus saya l
- **ds-013** (troubleshooting): low_groundedness(0.62) — Koneksi API saya kena error 429 Too Many Requests pas jam sibuk, ini k
- **ds-017** (policy): low_groundedness(0.67) — Apakah tagihan perpanjangan langganan bulanan (subscription renewal) b
- **ds-027** (troubleshooting): low_groundedness(0.69) — Why does my automation rule appear to execute repeatedly on ticket upd
- **ds-049** (product_usage): low_groundedness(0.37) — Bagaimana cara menutup (close) tiket di FlowDesk setelah masalah pelan

## Varian llm-judge (run 2026-10-12T12:17:11, generator nvidia/nemotron-3-ultra-550b-a55b)

### Distribusi akar masalah

| Akar masalah | Jumlah | Tindakan yang disarankan |
|---|---:|---|
| scope_miss | 8 | S3 — kalibrasi scope_check / routing escalate |
| gate_too_loose | 4 | PERIKSA MANUAL — mode gagal berbahaya (menjawab tanpa dasar) |
| gate_miss | 3 | S1 — kalibrasi threshold (evidence_min 0.55->0.45, completeness 0.75->0.65) |

### Detail miss

| Case | Kategori | Expected | Got | Akar | hit@5 | groundedness | retried | Pertanyaan |
|---|---|---|---|---|---:|---:|---|---|
| ds-015 | product_usage | answered | abstained | gate_miss | 1.0 | - | ya | Bagaimana alur dan langkah-langkah awal untuk membuat workspace baru d |
| ds-030 | structured_data | answered | abstained | gate_miss | 1.0 | - | ya | Apa perbedaan fitur pelaporan antara Standard Reporting dan Advanced A |
| ds-049 | product_usage | answered | abstained | gate_miss | 1.0 | - | ya | Bagaimana cara menutup (close) tiket di FlowDesk setelah masalah pelan |
| ds-003 | troubleshooting | abstained | answered | gate_too_loose | 1.0 | 0.66 | tidak | Why am I not getting webhook deliveries to my configured server endpoi |
| ds-023 | unanswerable | abstained | answered | gate_too_loose | 1.0 | 0.74 | tidak | Apa rekomendasi terbaik dalam penamaan tag profil pelanggan dan penggu |
| ds-038 | ambiguous | abstained | answered | gate_too_loose | 1.0 | 0.74 | ya | How do I reset it? |
| ds-040 | ambiguous | abstained | answered | gate_too_loose | 1.0 | 0.92 | tidak | What is the limit for tickets? |
| ds-006 | troubleshooting | answered | escalated | scope_miss | 1.0 | - | tidak | Kenapa akun FlowDesk saya tiba-tiba terkunci dan apa yang harus saya l |
| ds-018 | multi_document | abstained | escalated | scope_miss | 0.0 | - | tidak | Bagaimana cara kerja aksi send_webhook pada automasi FlowDesk dan pake |
| ds-035 | unanswerable | abstained | escalated | scope_miss | - | - | tidak | Kenapa aplikasi mobile FlowDesk crash saat membuka attachment? |
| ds-037 | ambiguous | abstained | escalated | scope_miss | 1.0 | - | tidak | Berapa biayanya? |
| ds-039 | ambiguous | abstained | escalated | scope_miss | 0.0 | - | tidak | Bagaimana cara melihat log di FlowDesk? |
| ds-041 | ambiguous | abstained | escalated | scope_miss | 0.0 | - | tidak | Kenapa saya tidak bisa membuka halaman pengaturan? |
| ds-042 | unanswerable | abstained | escalated | scope_miss | - | - | tidak | Apakah FlowDesk menyediakan aplikasi native untuk iOS dan Android di A |
| ds-043 | unanswerable | abstained | escalated | scope_miss | 1.0 | - | tidak | Berapa target batas waktu resolusi tiket (SLA resolution time) dalam h |
### Kualitas (keputusan benar, jawaban perlu perhatian)

- **ds-013** (troubleshooting): low_groundedness(0.68), correctness_partial — Koneksi API saya kena error 429 Too Many Requests pas jam sibuk, ini k
- **ds-014** (api): low_groundedness(0.68) — What HTTP status code and error code are returned when an API request 
- **ds-020** (troubleshooting): low_groundedness(0.38) — When making an API request to GET /v1/tickets/{ticket_id}, I receive a
- **ds-027** (troubleshooting): low_groundedness(0.11), correctness_partial — Why does my automation rule appear to execute repeatedly on ticket upd

## Shared miss — gagal di KEDUA varian (bukan salah judge)

- **ds-018** (multi_document): expected abstained — lihat detail di tiap varian; akar masalah di hulu (retrieval/generator/label)
- **ds-023** (unanswerable): expected abstained — lihat detail di tiap varian; akar masalah di hulu (retrieval/generator/label)
- **ds-030** (structured_data): expected answered — lihat detail di tiap varian; akar masalah di hulu (retrieval/generator/label)
- **ds-038** (ambiguous): expected abstained — lihat detail di tiap varian; akar masalah di hulu (retrieval/generator/label)

## Catatan

- rows eval tidak menyimpan jev reason/trace lengkap — untuk bedah per kasus, buka trace Langfuse (run_id) atau jalankan ulang kasus via ask.py (backlog S7).
- Setelah kalibrasi S1, jalankan ulang run_eval + debug_cases untuk mengukur perbaikan (loop evaluasi).
