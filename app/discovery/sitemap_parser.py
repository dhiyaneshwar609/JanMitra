"""
sitemap_parser.py

Downloads and parses sitemap.xml files.
Supports sitemap indexes and normal URL sets.
"""

import requests
import xml.etree.ElementTree as ET

from url_filter import URLFilter


class SitemapParser:

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.filter = URLFilter()

    def download(self, sitemap_url):
        try:
            response = requests.get(
                sitemap_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "CitizenAI/1.0"
                }
            )

            if response.status_code == 200:
                return response.text

        except Exception as e:
            print("Download Error:", e)

        return None

    def parse(self, sitemap_url):

        xml_data = self.download(sitemap_url)

        if not xml_data:
            return []

        try:

            root = ET.fromstring(xml_data)

        except Exception as e:

            print("XML Error:", e)
            return []

        urls = []

        namespace = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
        }

        # Normal sitemap
        if root.tag.endswith("urlset"):

            for url in root.findall("sm:url", namespace):

                loc = url.find("sm:loc", namespace)

                if loc is not None:

                    website = loc.text.strip()

                    if self.filter.is_valid(website):
                        urls.append(website)

        # Sitemap Index
        elif root.tag.endswith("sitemapindex"):

            for sitemap in root.findall("sm:sitemap", namespace):

                loc = sitemap.find("sm:loc", namespace)

                if loc is None:
                    continue

                child = loc.text.strip()

                urls.extend(self.parse(child))

        return list(set(urls))