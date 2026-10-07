"""Sentralisasi konfigurasi guardrail Phase 3.
Semua angka di sini = starting point, bukan final; diubah setelah eksperimen
dan sesuai kebutuhan model LLM yang dipakai (PRD 3.1 / 3.3 / 3.5)."""

# --- Input (PRD 3.1) ---
MAX_INPUT_TOKENS = 512        # di atas ini: moderate (minta user meringkas)
HARD_INPUT_LIMIT = 4000       # di atas ini: hard reject 

# --- Output (PRD 3.5) ---
MAX_OUTPUT_TOKENS = 512       # jawaban support harus concise & actionable

# --- Context (PRD 3.3) ---
CONTEXT_TOKEN_BUDGET = 1500   # total token context yang boleh masuk ke LLM
TOP_K = 5                     # baseline retrieval, sama dengan evaluasi Phase 2

# --- Jev / workflow (Phase 4) ---
MAX_JEV_RETRIES = 1          # uncertain -> retry maksimal sekali
RETRY_TOP_K = 10             # retry retrieve dengan K lebih besar

JEV_MODEL = "jev-latest"     # bisa dikunci ke versi, mis. "jev-1.13.0", saat eksperimen
JEV_TIMEOUT_S = 10.0         # mayoritas query ~100ms; 10s = longgar tapi fail-safe cepat

# Noul-gated routing (starting point, bukan final):
# noul = P(evidence cukup). Tiga zona, threshold di KODE bukan di model.
JEV_THRESHOLDS = {
    "noul_sufficient":   0.75,   # >= ini -> sufficient  (generate)
    "noul_insufficient": 0.35,   # <= ini -> insufficient (escalate, tanpa retry)
}   # di antara keduanya -> uncertain (retry K=10)
