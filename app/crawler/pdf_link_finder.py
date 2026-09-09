from bs4 import BeautifulSoup
from urllib.parse import urljoin


class PDFLinkFinder:

    def find(self, html, base_url):
        """
        Find all PDF links from a webpage.
        """

        soup = BeautifulSoup(html, "html.parser")

        pdf_links = []

        for tag in soup.find_all("a", href=True):

            href = tag["href"].strip()

            if ".pdf" in href.lower():

                full_url = urljoin(base_url, href)

                pdf_links.append(full_url)

        return list(dict.fromkeys(pdf_links))