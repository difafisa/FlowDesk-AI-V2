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
