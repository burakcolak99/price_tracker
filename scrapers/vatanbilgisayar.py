from .base import get_soup, parse_price
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.vatanbilgisayar.com/bilgisayar-ram-bellek/?page={}"
PAGES = 3

def scrape() -> list[dict]:
    products = []
    for page in range(1, PAGES + 1):
        soup = get_soup(BASE_URL.format(page), wait_selector="div.product-list--item")
        if not soup:
            continue
        cards = soup.select("div.product-list--item")
        if not cards:
            break
        for card in cards:
            try:
                a_tag    = card.select_one("a")
                href     = a_tag["href"] if a_tag else None
                full_url = f"https://www.vatanbilgisayar.com{href}" if href else None
                name_el  = card.select_one("span.product-list--title")
                name     = name_el.get_text(strip=True) if name_el else "?"
                price_el = card.select_one("span.product-list--price") or card.select_one("div.product-list--price")
                price    = parse_price(price_el.get_text()) if price_el else None
                if price and full_url:
                    products.append({"id": href, "name": name, "price": price, "url": full_url, "site": "vatanbilgisayar"})
            except Exception as e:
                logger.debug(f"Vatan kart hatasi: {e}")
    logger.info(f"Vatanbilgisayar: {len(products)} urun bulundu.")
    return products
