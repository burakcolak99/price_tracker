from .base import get_soup, parse_price
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.amazon.com.tr/s?k=ram+bellek&rh=n%3A12466490031&page={}"
PAGES = 3

def scrape() -> list[dict]:
    products = []
    for page in range(1, PAGES + 1):
        soup = get_soup(BASE_URL.format(page), extra_headers={
            "Accept-Language": "tr-TR,tr;q=0.9"
        })
        if not soup:
            continue

        cards = soup.select("div[data-component-type='s-search-result']")
        if not cards:
            break

        for card in cards:
            try:
                a_tag    = card.select_one("a.a-link-normal.s-no-outline")
                href     = a_tag["href"] if a_tag else None
                full_url = f"https://www.amazon.com.tr{href}" if href else None

                name_el  = card.select_one("span.a-text-normal") or \
                           card.select_one("h2 span")
                name     = name_el.get_text(strip=True) if name_el else "?"

                whole    = card.select_one("span.a-price-whole")
                fraction = card.select_one("span.a-price-fraction")
                if whole:
                    raw   = whole.get_text(strip=True).replace(".", "").replace(",", "")
                    frac  = fraction.get_text(strip=True) if fraction else "0"
                    price = float(f"{raw}.{frac}")
                else:
                    price = None

                if price and full_url:
                    products.append({
                        "id":    href,
                        "name":  name,
                        "price": price,
                        "url":   full_url,
                        "site":  "amazon",
                    })
            except Exception as e:
                logger.debug(f"Amazon kart hatası: {e}")

    logger.info(f"Amazon: {len(products)} ürün bulundu.")
    return products
