import requests, logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

def send(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logger.error(f"Telegram hatası: {e}")

def alert_drop(site: str, name: str, url: str,
               old_price: float, new_price: float):
    diff = old_price - new_price
    pct  = (diff / old_price) * 100
    message = (
        f"🔻 <b>FİYAT DÜŞTÜ — {site.upper()}</b>\n\n"
        f"🖥 <b>{name}</b>\n\n"
        f"💸 Eski fiyat : <s>{old_price:,.0f} TL</s>\n"
        f"💚 Yeni fiyat : <b>{new_price:,.0f} TL</b>\n"
        f"📉 Düşüş      : <b>{diff:,.0f} TL  (%-{pct:.1f})</b>\n\n"
        f"🔗 <a href='{url}'>Ürüne Git</a>"
    )
    send(message)
