import json
import re
from pathlib import Path
from bs4 import BeautifulSoup


class DataCleaner:

    def clean_text(self, text):

        if not text:
            return ""

        text = BeautifulSoup(text, "html.parser").get_text()

        text = re.sub(r"\s+", " ", text)

        text = re.sub(r"\n+", "\n", text)

        return text.strip()

    def clean_file(self, input_file, output_file):

        with open(input_file, "r", encoding="utf-8") as f:
            documents = json.load(f)

        cleaned = []

        for doc in documents:

            content = self.clean_text(doc.get("content", ""))

            if len(content) < 100:
                continue

            doc["content"] = content

            cleaned.append(doc)

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False)

        print(f"Cleaned {len(cleaned)} documents")