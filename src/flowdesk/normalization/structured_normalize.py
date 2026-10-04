"""JSON/CSV -> canonical structured records + text representation untuk retrieval."""
import csv, json
from pathlib import Path

def load_records(path: Path) -> list[dict]:
    """Kembalikan list record canonical. Struktur asli TIDAK dirusak:
    record tetap punya dict asli di field 'data'."""
    records: list[dict] = []
    if path.suffix == ".json":
        items = json.loads(path.read_text(encoding="utf-8"))
        items = items if isinstance(items, list) else [items]
        records = [{"data": it} for it in items]
    elif path.suffix == ".csv":
        with path.open(encoding="utf-8") as f:
            records = [{"data": row} for row in csv.DictReader(f)]
    for i, r in enumerate(records):
        r["record_id"] = f"{path.stem}-{i:03d}"
        r["source"] = str(path.relative_to(path.parents[2]))
    return records

def record_to_text(record: dict) -> str:
    """Representasi text TIPIS untuk embedding (format Plan: Pro / Price: $49...).
    Nilai dict/list di-flatten rekursif, bukan dump JSON mentah."""
    def kv(d, prefix=""):
        parts = []
        for k, v in d.items():
            key = f"{prefix} {k}".strip().replace("_", " ")
            if isinstance(v, dict):
                parts += kv(v, key)
            elif isinstance(v, list):
                parts.append(f"{key}: " + "; ".join(str(x) for x in v))
            else:
                parts.append(f"{key}: {v}")
        return parts
    return ". ".join(kv(record["data"]))
