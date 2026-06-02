from . import trendyol, hepsiburada, amazon, vatanbilgisayar, incehesap, itopya

SCRAPERS = {
    "trendyol":        trendyol.scrape,
    "hepsiburada":     hepsiburada.scrape,
    "amazon":          amazon.scrape,
    "vatanbilgisayar": vatanbilgisayar.scrape,
    "incehesap":       incehesap.scrape,
    "itopya":          itopya.scrape,
}
