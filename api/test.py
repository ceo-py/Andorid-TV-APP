from playwright.sync_api import sync_playwright
import threading
import re

captured_urls = []
url_lock = threading.Lock()


def extract_jwplayer_config(html_content):
    pattern = re.compile(r'"(?P<video_url>https?://[^"]*m3u8[^"]*)"')
    return pattern.findall(html_content)[0]


def handle_response(response):
    try:
        content = response.text()
        if ".m3u8" in content:
            print(".m3u8 found")
            print(extract_jwplayer_config(response.text()))
    except:
        pass

    if response.status == 200 and any(
        m3u8_pattern in response.url for m3u8_pattern in ("index.m3u8", ".m3u8")
    ):
        with url_lock:
            if response.url not in captured_urls:
                print(f"\n✅ Found m3u8 URL: {response.url}\n")
                captured_urls.append(response.url)


def run(p):
    # target_url = "https://www.seirsanduk.com/bnt-1-online.xhtml" # <-- REPLACE THIS
    target_url = "https://www.gledaitv.fan/diema-sport-hd-live-tv.html"  # <-- REPLACE THIS

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.on("response", handle_response)

    try:
        page.goto(target_url, wait_until="networkidle")

        page.wait_for_selector('p:has-text("Не давам съгласие")')
        page.click('p:has-text("Не давам съгласие")')

        page.wait_for_selector('a:has-text("Player 1")') 
        page.click('a:has-text("Player 1")') 

        if not captured_urls:
            page.wait_for_timeout(5000)

    except Exception as e:
        print(f"Error during navigation: {e}")

    finally:
        browser.close()


with sync_playwright() as p:
    run(p)
