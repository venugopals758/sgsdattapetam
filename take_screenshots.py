from playwright.sync_api import sync_playwright
import os

BASE_URL = "http://127.0.0.1:8005"
OUT_DIR  = os.path.join(os.path.dirname(__file__), "media", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

PAGES = [
    ("home",      "/"),
    ("donations", "/donations/"),
    ("seva",      "/seva/"),
    ("events",    "/events/"),
    ("about",     "/about/"),
    ("contact",   "/contact/"),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    for name, path in PAGES:
        url = BASE_URL + path
        print(f"  Capturing {name} - {url}")
        page.goto(url, wait_until="networkidle")
        # scroll to trigger animations then scroll back
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(400)
        out = os.path.join(OUT_DIR, f"{name}.png")
        page.screenshot(path=out, full_page=True)
        print(f"    Saved: {out}")

    browser.close()
    print("\nAll screenshots saved to media/screenshots/")
