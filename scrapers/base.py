import re, logging, time, random, subprocess, sys
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

logger = logging.getLogger(__name__)

# Sistem bağımlılıklarını ve Chromium'u runtime'da bir kez kur
_installed = False
def _ensure_chromium():
    global _installed
    if _installed:
        return
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install-deps", "chromium"],
            check=True, capture_output=True, text=True
        )
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True, capture_output=True, text=True
        )
        logger.info("Chromium kurulumu tamamlandi.")
    except Exception as e:
        logger.warning(f"Chromium kurulum uyarisi: {e}")
    _installed = True

_ensure_chromium()


def get_soup(url: str, wait_selector: str = None, scroll: bool = True, retries: int = 2):
    for attempt in range(1, retries + 2):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-gpu",
                        "--window-size=1280,800",
                    ]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                    locale="tr-TR",
                    java_script_enabled=True,
                    ignore_https_errors=True,
                )
                page = context.new_page()

                # Gereksiz kaynakları engelle (hız için)
                page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf,eot}",
                           lambda route: route.abort())

                # Sayfayı yükle
                page.goto(url, wait_until="load", timeout=45000)

                # JS render için networkidle bekle
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except PWTimeout:
                    logger.debug(f"networkidle timeout, devam ediliyor: {url}")

                # Hedef selector'ı bekle
                if wait_selector:
                    try:
                        page.wait_for_selector(wait_selector, timeout=20000)
                    except PWTimeout:
                        logger.warning(f"Selector bulunamadi ({wait_selector}), HTML loglanıyor: {url}")
                        html_preview = page.content()[:500]
                        logger.debug(f"HTML preview: {html_preview}")
                        browser.close()
                        if attempt <= retries:
                            logger.info(f"Yeniden deneniyor ({attempt}/{retries}): {url}")
                            time.sleep(3)
                            continue
                        return None

                # Scroll ile lazy-load tetikle
                if scroll:
                    for _ in range(5):
                        page.mouse.wheel(0, 1500)
                        time.sleep(random.uniform(0.8, 1.5))
                    time.sleep(2)

                html = page.content()
                browser.close()

                soup = BeautifulSoup(html, "html.parser")
                return soup

        except Exception as e:
            logger.error(f"Playwright hatasi [{url}] (deneme {attempt}): {e}")
            if attempt <= retries:
                time.sleep(3)
                continue
            return None
    return None


def parse_price(text: str) -> float | None:
    if not text:
        return None
    text = text.strip()
    # TL, ₺ ve boşlukları temizle
    clean = re.sub(r"[^\d,.]", "", text)
    if not clean:
        return None
    # 1.234,56 formatı
    if "," in clean and "." in clean:
        if clean.rfind(".") < clean.rfind(","):
            clean = clean.replace(".", "").replace(",", ".")
        else:
            clean = clean.replace(",", "")
    elif "," in clean:
        clean = clean.replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return None
