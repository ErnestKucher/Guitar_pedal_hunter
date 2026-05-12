import json
from pathlib import Path

SEEN_FILE = Path("data/seen.json")

def load_seen():
    if not SEEN_FILE.exists():
        return {}

    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_seen(data):
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)