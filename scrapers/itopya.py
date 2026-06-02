from .base import get_soup, parse_price
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.itopya.com/rambellek_k10/?page={}"
PAGES = 3

def scrape() -> list[dict]:
    products = []
    for page in range(1, PAGES + 1):
        soup = get_soup(BASE_URL.format(page), wait_selector="div.product-item")
        if not soup:
            continue
        cards = soup.select("div.product-item") or soup.select("div.col.product")
        if not cards:
            break
        for card in cards:
            try:
                a_tag    = card.select_one("a.product-name") or card.select_one("a")
                href     = a_tag["href"] if a_tag else None
                full_url = href if href and href.startswith("http") else f"https://www.itopya.com{href}"
                name_el  = card.select_one("a.product-name") or card.select_one("div.product-title")
                name     = name_el.get_text(strip=True) if name_el else "?"
                price_el = card.select_one("span.product-price") or card.select_one("div.price")
                price    = parse_price(price_el.get_text()) if price_el else None
                if price and full_url:
                    products.append({"id": href, "name": name, "price": price, "url": full_url, "site": "itopya"})
            except Exception as e:
                logger.debug(f"Itopya kart hatasi: {e}")
    logger.info(f"Itopya: {len(products)} urun bulundu.")
    return products
