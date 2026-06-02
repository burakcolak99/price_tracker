import time, logging
from config import CHECK_INTERVAL_MINUTES, SITES
from scrapers import SCRAPERS
from storage import load, save, get_previous, update
from notifier import send, alert_drop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")


def run_check():
    db = load()
    total_drops = 0

    for site_name, scrape_fn in SCRAPERS.items():
        if not SITES.get(site_name, True):
            continue

        logger.info(f"── {site_name} taranıyor...")
        try:
            products = scrape_fn()
        except Exception as e:
            logger.error(f"{site_name} scrape hatası: {e}")
            continue

        for p in products:
            prev = get_previous(db, site_name, p["id"])

            if prev is None:
                logger.info(f"  [YENİ] {p['name']} → {p['price']:,.0f} TL")

            elif p["price"] < prev:
                logger.info(
                    f"  [DÜŞTÜ] {p['name']} "
                    f"{prev:,.0f} → {p['price']:,.0f} TL"
                )
                alert_drop(
                    site=site_name,
                    name=p["name"],
                    url=p["url"],
                    old_price=prev,
                    new_price=p["price"],
                )
                total_drops += 1

            update(db, site_name, p["id"], {
                "name":  p["name"],
                "price": p["price"],
                "url":   p["url"],
            })

    save(db)
    logger.info(f"✅ Kontrol tamamlandı. {total_drops} fiyat düşüşü bulundu.\n")


if __name__ == "__main__":
    send("🤖 <b>RAM Fiyat Takip Botu Başlatıldı!</b>\n"
         "6 site izleniyor: Trendyol, Hepsiburada, Amazon TR, "
         "Vatanbilgisayar, İncehesap, İtopya\n"
         "📊 İlk tarama başlıyor...")

    while True:
        run_check()
        logger.info(f"⏳ {CHECK_INTERVAL_MINUTES} dakika bekleniyor...")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)
