"""Smoke test Tahap 0 — sekali jalan untuk memastikan Jev asli hidup.
Bukan bagian pytest (tidak dipanggil di test otomatis, memanggil API asli)."""
from dotenv import load_dotenv
load_dotenv()

from flowdesk.jev.client import JevClient

c = JevClient()
d = c.decide(
    "Does the Pro plan support webhooks?",
    "[1] Pro plan: $49/mo, includes API access and webhooks.",
)
print(d)
