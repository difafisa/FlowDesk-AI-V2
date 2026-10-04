import re
from pathlib import Path

def normalize_md(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\n{3,}", "\n\n", text)         
    text = re.sub(r"[ \t]+\n", "\n", text)          
    return text.strip()
