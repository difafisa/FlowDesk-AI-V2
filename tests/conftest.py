"""Konfigurasi pytest terpusat (Tahap 7.2 — restrukturisasi tests/ per PRD).

sys.path ke src/ cukup diatur SEKALI di sini; conftest berlaku untuk
tests/ dan semua subfoldernya. Selama venv memakai editable install
(pip install -e .) ini teknis berlebih, tapi menjamin test tetap jalan
di environment tanpa editable install: CI, venv segar, container.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
