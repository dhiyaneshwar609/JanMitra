"""
robots_parser.py

Downloads and parses robots.txt from government websites.
Automatically discovers sitemap.xml if robots.txt doesn't specify one.
"""

import requests
from urllib.parse import urljoin


class RobotsParser:

    COMMON_SITEMAPS = [
        "/sitemap.xml",
        "/sitemap_index.xml",
        "/sitemap-index.xml"
    ]

    def __init__(self, timeout=10):
        self.timeout = timeout

    def get_robots_url(self, website):
        return urljoin(website, "/robots.txt")

    def fetch(self, website):

        try:
            response = requests.get(
                self.get_robots_url(website),
                timeout=self.timeout,
                headers={
                    "User-Agent": "CitizenAI/1.0"
                }
            )

            if response.status_code == 200:
                return response.text

        except Exception:
            pass

        return ""

    def extract_sitemaps(self, robots_text):

        sitemaps = []

        for line in robots_text.splitlines():

            line = line.strip()

            if line.lower().startswith("sitemap:"):
                sitemaps.append(line.split(":",1)[1].strip())

        return sitemaps

    def extract_disallow(self, robots_text):

        rules = []

        for line in robots_text.splitlines():

            line=line.strip()

            if line.lower().startswith("disallow:"):
                rules.append(line.split(":",1)[1].strip())

        return rules

    def discover_common_sitemaps(self, website):

        found=[]

        for path in self.COMMON_SITEMAPS:

            url=urljoin(website,path)

            try:

                r=requests.get(url,timeout=5)

                if r.status_code==200:

                    found.append(url)

            except:
                pass

        return found

    def parse(self,website):

        robots=self.fetch(website)

        sitemaps=self.extract_sitemaps(robots)

        if not sitemaps:
            sitemaps=self.discover_common_sitemaps(website)

        return {
            "robots_url":self.get_robots_url(website),
            "sitemaps":sitemaps,
            "disallow":self.extract_disallow(robots)
        }