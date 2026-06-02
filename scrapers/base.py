import re, logging, time, random, subprocess, sys
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

logger = logging.getLogger(__name__)

# Sistem bağımlılıklarını ve Chromium'u runtime'da kur
try:
    subprocess.run(
        [sys.executable, "-m", "playwright", "install-deps", "chromium"],
        check=True, capture_output=True, text=True
    )
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True, capture_output=True, text=True
    )
    logger.info("Chromium ve sistem bağımlılıkları kuruldu.")
except Exception as e:
    logger.warning(f"Chromium kurulum uyarisi: {e}")


def get_soup(url: str, wait_selector: str = None, scroll: bool = True):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="tr-TR",
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=10000)
                except PWTimeout:
                    logger.debug(f"Selector bulunamadi: {wait_selector}")

            if scroll:
                for _ in range(3):
                    page.mouse.wheel(0, 1500)
                    time.sleep(random.uniform(0.5, 1.2))

            html = page.content()
            browser.close()
            return BeautifulSoup(html, "lxml")
    except Exception as e:
        logger.error(f"Playwright hatasi [{url}]: {e}")
        return None


def parse_price(text: str) -> float | None:
    if not text:
        return None
    clean = re.sub(r"[^\d,.]", "", text.strip())
    if "," in clean and "." in clean:
        clean = clean.replace(".", "").replace(",", ".")
    elif "," in clean:
        clean = clean.replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return None
