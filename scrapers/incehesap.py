from .base import get_soup, parse_price
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.incehesap.com/ram-fiyatlari/?sayfa={}"
PAGES = 3

def scrape() -> list[dict]:
    products = []
    for page in range(1, PAGES + 1):
        soup = get_soup(BASE_URL.format(page), wait_selector="div.product-card")
        if not soup:
            continue
        cards = soup.select("div.product-card")
        if not cards:
            cards = (soup.select("[class*='product-card']") or
                     soup.select("[class*='product-item']") or
                     soup.select("article[class*='product']"))
        if not cards:
            logger.debug(f"Incehesap sayfa {page}: kart bulunamadi")
            continue
        for card in cards:
            try:
                a_tag    = card.select_one("a")
                href     = a_tag["href"] if a_tag else None
                full_url = f"https://www.incehesap.com{href}" if href and href.startswith("/") else href
                name_el  = (card.select_one("div.product-card-name") or
                            card.select_one("[class*='product-name']") or
                            card.select_one("[class*='title']") or
                            card.select_one("h2") or
                            card.select_one("h3"))
                name     = name_el.get_text(strip=True) if name_el else "?"
                price_el = (card.select_one("span.product-card-price--current") or
                            card.select_one("[class*='price--current']") or
                            card.select_one("[class*='current-price']") or
                            card.select_one("div.product-card-price") or
                            card.select_one("[class*='price']"))
                price    = parse_price(price_el.get_text()) if price_el else None
                if price and full_url:
                    products.append({"id": href, "name": name, "price": price, "url": full_url, "site": "incehesap"})
            except Exception as e:
                logger.debug(f"Incehesap kart hatasi: {e}")
    logger.info(f"Incehesap: {len(products)} urun bulundu.")
    return products
