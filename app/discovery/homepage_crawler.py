import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

from url_filter import URLFilter


class HomepageCrawler:

    def __init__(self, timeout=15, max_depth=2, max_pages=200):

        self.timeout = timeout
        self.max_depth = max_depth
        self.max_pages = max_pages

        self.filter = URLFilter()

        self.headers = {
            "User-Agent": "CitizenAI/1.0"
        }

    def crawl(self, website):

        base_domain = urlparse(website).netloc

        visited = set()

        discovered = set()

        queue = deque()

        queue.append((website, 0))

        while queue:

            current_url, depth = queue.popleft()

            if current_url in visited:
                continue

            if depth > self.max_depth:
                continue

            if len(visited) >= self.max_pages:
                break

            visited.add(current_url)

            try:

                response = requests.get(
                    current_url,
                    headers=self.headers,
                    timeout=self.timeout
                )

                if response.status_code != 200:
                    continue

                soup = BeautifulSoup(response.text, "lxml")

                for tag in soup.find_all("a", href=True):

                    href = tag["href"].strip()

                    full_url = urljoin(current_url, href)

                    parsed = urlparse(full_url)

                    # Same website only
                    if parsed.netloc != base_domain:
                        continue

                    normalized = self.filter.normalize(full_url)

                    if normalized is None:
                        continue

                    if not self.filter.is_valid(normalized):
                        continue

                    if normalized not in discovered:
                        discovered.add(normalized)

                    if normalized not in visited:
                        queue.append((normalized, depth + 1))

            except Exception:
                continue

        return sorted(discovered)