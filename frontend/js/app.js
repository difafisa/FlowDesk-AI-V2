/* Phase 7 (PRD) — Frontend chat: /ask, /feedback, badge status, sources, trace. */

const API_TIMEOUT_MS = 120_000;  // P95 workflow ~38s; gelombang retry bisa lebih — beri margin

/* --- session: satu tab = satu sesi di panel Sessions Langfuse --- */
let sessionId = sessionStorage.getItem("flowdesk_session");
if (!sessionId) {
  sessionId = "web-" + (crypto.randomUUID ? crypto.randomUUID() : Date.now());
  sessionStorage.setItem("flowdesk_session", sessionId);
}

const chat        = document.getElementById("chat");
const input       = document.getElementById("input");
const sendBtn     = document.getElementById("send");
const debugToggle = document.getElementById("debug-toggle");
let busy = false;

/* ---------------- util ---------------- */

/* Jawaban berasal dari LLM & metadata dari DB — SEMUA di-escape sebelum
   masuk innerHTML (XSS). Marker [n] ditambah setelah escape. */
const esc = (s) => String(s ?? "").replace(/[&<>"']/g,
  (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

const withCitations = (html) => html.replace(/\[(\d+)\]/g, '<sup class="cite">[$1]</sup>');

function scrollDown() { chat.scrollTop = chat.scrollHeight; }

function addBubble(role, html) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerHTML = `<div class="bubble">${html}</div>`;
  chat.appendChild(div);
  scrollDown();
  return div.querySelector(".bubble");
}

/* ---------------- render jawaban ---------------- */

function renderSources(sources) {
  if (!sources?.length) return "";
  const items = sources.map((s) =>
    `<div class="source"><b>[${s.index}]</b> ${esc(s.document)}` +
    `${s.page ? ` — hlm. ${s.page}` : ""}</div>`).join("");
  return `<div class="sources">${items}</div>`;
}

function renderTrace(trace) {
  if (!trace?.length) return "";
  const items = trace.map((t) => `<li>${esc(JSON.stringify(t))}</li>`).join("");
  return `<details class="trace"><summary>trace workflow (${trace.length} langkah)</summary>` +
         `<ol>${items}</ol></details>`;
}

function renderMeta(d) {
  const bits = [];
  if (d.latency_s != null) bits.push(`${d.latency_s}s`);
  if (d.retries) bits.push(`retry ×${d.retries}`);
  if (d.jev?.decision) bits.push(`Jev: ${esc(d.jev.decision)}`);
  if (d.run_id) bits.push(`run ${esc(d.run_id.slice(0, 8))}…`);
  return bits.length ? `<div class="meta">${bits.join(" · ")}</div>` : "";
}

function renderFeedback(runId) {
  return `
    <div class="feedback" data-run-id="${esc(runId ?? "")}">
      <button class="fb-yes" title="Jawaban membantu">👍</button>
      <button class="fb-no"  title="Jawaban tidak membantu">👎</button>
      <span class="saved" hidden></span>
    </div>`;
}

function renderAnswer(d) {
  const badge = `<span class="badge ${esc(d.status)}">${esc(d.status)}</span>`;
  const body  = `<p>${withCitations(esc(d.answer || "(tidak ada jawaban)"))}</p>`;
  return badge + body + renderSources(d.sources) + renderMeta(d)
       + (d.trace ? renderTrace(d.trace) : "") + renderFeedback(d.run_id);
}

/* ---------------- /ask ---------------- */

async function ask(question) {
  addBubble("user", esc(question));
  const holder = addBubble("assistant",
    `<span class="typing"><i></i><i></i><i></i></span>` +
    `<span class="wait"> mencari &amp; menilai evidence… <b class="elapsed">0s</b></span>`);

  const t0 = performance.now();
  const tick = setInterval(() => {
    const el = holder.querySelector(".elapsed");
    if (el) el.textContent = Math.round((performance.now() - t0) / 1000) + "s";
  }, 1000);

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), API_TIMEOUT_MS);
  let d;
  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question, session_id: sessionId, debug: debugToggle.checked }),
      signal: ctrl.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    d = await res.json();
  } catch (e) {
    d = {
      status: "error",
      answer: e.name === "AbortError"
        ? "Waktu tunggu habis — server sedang sibuk. Coba kirim ulang pertanyaannya."
        : "Maaf, terjadi gangguan koneksi ke server. Coba lagi sebentar.",
    };
  } finally {
    clearTimeout(timer);
    clearInterval(tick);
  }
  holder.innerHTML = renderAnswer(d);
  scrollDown();
}

/* ---------------- /feedback ---------------- */

async function sendFeedback(box, helpful, comment = null) {
  const runId = box.dataset.runId || null;    // kosong -> backend pakai id lokal
  const btns  = box.querySelectorAll("button");
  let saved   = box.querySelector(".saved");
  if (!saved) { saved = document.createElement("span");
                saved.className = "saved"; box.appendChild(saved); }
  btns.forEach((b) => (b.disabled = true));
  saved.hidden = true;
  try {
    const res = await fetch("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ run_id: runId, helpful, comment }),
    });
    if (!res.ok) throw new Error();
    saved.textContent = "✓ feedback tercatat";
  } catch {
    btns.forEach((b) => (b.disabled = false));
    saved.textContent = "✗ gagal tersimpan — coba lagi";
  }
  saved.hidden = false;
}

/* klik 👍 -> langsung kirim; klik 👎 -> minta komentar opsional dulu */
chat.addEventListener("click", (e) => {
  const box = e.target.closest(".feedback");
  if (!box) return;
  if (e.target.classList.contains("fb-yes")) {
    sendFeedback(box, true);
  } else if (e.target.classList.contains("fb-no")) {
    box.innerHTML = `
      <input class="comment" placeholder="Apa yang kurang tepat? (opsional)" maxlength="500">
      <button class="fb-send">Kirim</button>
      <button class="fb-skip">Lewati</button>`;
    box.querySelector(".comment").focus();
  } else if (e.target.classList.contains("fb-send")) {
    const c = box.querySelector(".comment").value.trim();
    sendFeedback(box, false, c || null);
  } else if (e.target.classList.contains("fb-skip")) {
    sendFeedback(box, false, null);
  }
});

chat.addEventListener("keydown", (e) => {
  if (e.target.classList.contains("comment") && e.key === "Enter") {
    e.preventDefault();
    sendFeedback(e.target.closest(".feedback"), false,
                 e.target.value.trim() || null);
  }
});

/* ---------------- composer ---------------- */

/* Tombol Kirim dikunci saat menunggu: backend menyerialisasi /ask
   (satu koneksi pgvector), jadi query kedua hanya antre — lebih jujur
   menahannya di UI. Textarea tetap aktif utk mengetik pertanyaan berikut. */
function setBusy(b) {
  busy = b;
  sendBtn.disabled = b;
  if (!b) input.focus();
}

async function submit() {
  const q = input.value.trim();
  if (!q || busy) return;
  input.value = "";
  input.style.height = "auto";
  setBusy(true);
  try { await ask(q); }
  finally { setBusy(false); }
}

sendBtn.addEventListener("click", submit);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); }
});
input.addEventListener("input", () => {            // auto-grow
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 140) + "px";
});
