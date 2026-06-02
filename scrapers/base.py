import requests, re, logging, time, random
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
]

def get_soup(url: str, extra_headers: dict = None, retries: int = 3) -> BeautifulSoup | None:
    for attempt in range(retries):
        headers = {**random.choice(HEADERS_LIST), **(extra_headers or {})}
        try:
            session = requests.Session()
            session.headers.update(headers)
            r = session.get(url, timeout=20, allow_redirects=True)
            r.raise_for_status()
            try:
                return BeautifulSoup(r.text, "lxml")
            except Exception:
                return BeautifulSoup(r.text, "html.parser")
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else 0
            if status == 403:
                wait = (attempt + 1) * 5 + random.randint(1, 5)
                logger.warning(f"403 Forbidden [{url}] — {wait}s beklenip tekrar denenecek (deneme {attempt+1}/{retries})")
                time.sleep(wait)
            else:
                logger.error(f"HTTP hatası [{url}]: {e}")
                break
        except Exception as e:
            logger.error(f"GET hatası [{url}]: {e}")
            break
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
