import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID",   "YOUR_CHAT_ID")

# Kaç dakikada bir kontrol (ücretsiz sunucu için 60+ önerilir)
CHECK_INTERVAL_MINUTES = 60

# Aktif siteler — False yaparak devre dışı bırakabilirsin
SITES = {
    "trendyol":        True,
    "hepsiburada":     True,
    "amazon":          True,
    "vatanbilgisayar": True,
    "incehesap":       True,
    "itopya":          True,
}
