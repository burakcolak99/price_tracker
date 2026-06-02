from .base import get_soup, parse_price
import logging

logger = logging.getLogger(__name__)

BASE_URLS = [
    "https://www.trendyol.com/sr?q=ram+bellek&categoryId=60015&pi={}",
]
PAGES = 3

def scrape() -> list[dict]:
    products = []
    for url_tpl in BASE_URLS:
        for page in range(1, PAGES + 1):
            url  = url_tpl.format(page)
            soup = get_soup(url)
            if not soup:
                continue

            cards = soup.select("div.p-card-wrppr")
            if not cards:
                break

            for card in cards:
                try:
                    a_tag    = card.select_one("a")
                    href     = a_tag["href"] if a_tag else None
                    full_url = f"https://www.trendyol.com{href}" if href else None

                    name_el  = card.select_one("span.prdct-desc-cntnr-name") or \
                               card.select_one("h3.prdct-desc-cntnr-name")
                    name     = name_el.get_text(strip=True) if name_el else "?"

                    price_el = card.select_one("div.prc-box-dscntd") or \
                               card.select_one("div.prc-dsc") or \
                               card.select_one("div.prc-box-orgnl")
                    price    = parse_price(price_el.get_text()) if price_el else None

                    if price and full_url:
                        products.append({
                            "id":    href,
                            "name":  name,
                            "price": price,
                            "url":   full_url,
                            "site":  "trendyol",
                        })
                except Exception as e:
                    logger.debug(f"Trendyol kart hatası: {e}")

    logger.info(f"Trendyol: {len(products)} ürün bulundu.")
    return products
