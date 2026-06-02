import requests, re, logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def get_soup(url: str, extra_headers: dict = None) -> BeautifulSoup | None:
    headers = {**HEADERS, **(extra_headers or {})}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")
    except Exception as e:
        logger.error(f"GET hatası [{url}]: {e}")
        return None

def parse_price(text: str) -> float | None:
    """'1.234,56 TL' → 1234.56"""
    if not text:
        return None
    clean = re.sub(r"[^\d,.]", "", text.strip())
    if "," in clean and "." in clean:
        clean = clean.replace(".", "").replace(",", ".")
    elif "," in clean:
        clean = clean.replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return None
