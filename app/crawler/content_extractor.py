import requests
import trafilatura

from app.crawler.browser_renderer import BrowserRenderer


class ContentExtractor:

    def __init__(self, timeout=20):

        self.timeout = timeout

        self.headers = {
            "User-Agent": "CitizenAI/1.0"
        }

        self.browser = BrowserRenderer()

    def extract(self, url):

        try:

            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return None

            downloaded = response.text

            extracted = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                include_links=False,
                favor_precision=True
            )

            if not extracted:
                return None

            html_for_metadata = downloaded

            # Fallback for JavaScript-heavy pages
            if len(extracted) < 2000:

                print(f"[Fallback] Rendering with Playwright: {url}")

                rendered_html = self.browser.render(url)

                rendered = trafilatura.extract(
                    rendered_html,
                    include_comments=False,
                    include_tables=True,
                    include_links=False,
                    favor_precision=True
                )

                if rendered and len(rendered) > len(extracted):
                    extracted = rendered
                    html_for_metadata = rendered_html

            metadata = trafilatura.extract_metadata(html_for_metadata)

            title = ""

            if metadata:
                title = metadata.title or ""

            # Debug output (remove later if not needed)
            print("=" * 80)
            print("URL:", url)
            print("TITLE:", title)
            print("CONTENT LENGTH:", len(extracted))
            print(extracted[:1500])
            print("=" * 80)

            return {
                "url": url,
                "title": title,
                "content": extracted,
                "content_type": "html"
            }

        except Exception as e:

            print("Extraction Error:", e)
            return None