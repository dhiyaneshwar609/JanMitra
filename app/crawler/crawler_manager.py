import json
from pathlib import Path

from content_extractor import ContentExtractor
from pdf_extractor import PDFExtractor


class CrawlerManager:

    def __init__(self):

        self.html_extractor = ContentExtractor()
        self.pdf_extractor = PDFExtractor()

    def crawl(self, input_file, output_file):

        with open(input_file, "r", encoding="utf-8") as f:
            website_data = json.load(f)

        documents = []

        total = sum(len(v) for v in website_data.values())
        current = 0

        for category, websites in website_data.items():

            for item in websites:

                current += 1

                url = item["url"]
                source = item.get("name", "")

                print(f"[{current}/{total}] {url}")

                if url.lower().endswith(".pdf"):

                    result = self.pdf_extractor.extract(url)

                else:

                    result = self.html_extractor.extract(url)

                if result is None:
                    continue

                result["category"] = category
                result["source"] = source

                documents.append(result)

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)

        print()
        print(f"Saved {len(documents)} documents")