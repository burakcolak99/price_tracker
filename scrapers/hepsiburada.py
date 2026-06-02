from .base import get_soup, parse_price
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.hepsiburada.com/bellek-ramler-c-47?sayfa={}"
PAGES = 3

def scrape() -> list[dict]:
    products = []
    for page in range(1, PAGES + 1):
        soup = get_soup(BASE_URL.format(page), wait_selector="li.productListContent-item")
        if not soup:
            continue
        cards = soup.select("li.productListContent-item")
        if not cards:
            break
        for card in cards:
            try:
                a_tag    = card.select_one("a")
                href     = a_tag["href"] if a_tag else None
                full_url = f"https://www.hepsiburada.com{href}" if href and href.startswith("/") else href
                name_el  = card.select_one("h3") or card.select_one("span[class*='title']")
                name     = name_el.get_text(strip=True) if name_el else "?"
                price_el = card.select_one("span.price-value") or card.select_one("[class*='finalPrice']")
                price    = parse_price(price_el.get_text()) if price_el else None
                if price and full_url:
                    products.append({"id": href, "name": name, "price": price, "url": full_url, "site": "hepsiburada"})
            except Exception as e:
                logger.debug(f"Hepsiburada kart hatasi: {e}")
    logger.info(f"Hepsiburada: {len(products)} urun bulundu.")
    return products
