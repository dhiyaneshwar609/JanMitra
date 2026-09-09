from playwright.sync_api import sync_playwright


class BrowserRenderer:

    def render(self, url):

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto(url, wait_until="networkidle", timeout=60000)

            html = page.content()

            print("=" * 80)
            print("HTML LENGTH:", len(html))
            print(html[:5000])
            print("=" * 80)

            browser.close()

            return html