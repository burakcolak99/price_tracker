from .base import get_soup, parse_price
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.amazon.com.tr/s?k=ram+bellek&i=computers&rh=n%3A12466490031&page={}"
PAGES = 3

def scrape() -> list[dict]:
    products = []
    for page in range(1, PAGES + 1):
        soup = get_soup(BASE_URL.format(page), wait_selector="div[data-component-type='s-search-result']")
        if not soup:
            continue
        cards = soup.select("div[data-component-type='s-search-result']")
        if not cards:
            logger.debug(f"Amazon sayfa {page}: kart bulunamadi")
            continue
        for card in cards:
            try:
                # Sponsorlu ürünleri de dahil et ama sadece ASIN olanları al
                asin = card.get("data-asin", "")
                if not asin:
                    continue
                a_tag    = card.select_one("a.a-link-normal[href*='/dp/']") or card.select_one("a.a-link-normal")
                href     = a_tag["href"] if a_tag else None
                full_url = f"https://www.amazon.com.tr{href}" if href and href.startswith("/") else href
                name_el  = (card.select_one("span.a-text-normal") or
                            card.select_one("h2 span") or
                            card.select_one("h2"))
                name     = name_el.get_text(strip=True) if name_el else "?"
                whole    = card.select_one("span.a-price-whole")
                fraction = card.select_one("span.a-price-fraction")
                if whole:
                    raw   = re.sub(r"[^\d]", "", whole.get_text(strip=True))
                    frac  = re.sub(r"[^\d]", "", fraction.get_text(strip=True)) if fraction else "0"
                    price_str = f"{raw}.{frac}" if frac else raw
                    try:
                        price = float(price_str)
                    except ValueError:
                        price = None
                else:
                    price = None
                if price and full_url:
                    products.append({"id": asin, "name": name, "price": price, "url": full_url, "site": "amazon"})
            except Exception as e:
                logger.debug(f"Amazon kart hatasi: {e}")
    logger.info(f"Amazon: {len(products)} urun bulundu.")
    return products

import re
