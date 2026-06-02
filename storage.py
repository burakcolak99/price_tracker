import json, os

DB_FILE = "prices.json"

def load() -> dict:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save(data: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_previous(db: dict, site: str, product_id: str) -> float | None:
    return db.get(site, {}).get(product_id, {}).get("price")

def update(db: dict, site: str, product_id: str, product: dict):
    db.setdefault(site, {})[product_id] = product
