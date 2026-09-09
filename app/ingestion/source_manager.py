import json
from pathlib import Path


class SourceManager:
    def __init__(self, sources_file=None):
        if sources_file is None:
            base_dir = Path(__file__).resolve().parent.parent
            sources_file = base_dir / "data" / "sources.json"

        self.sources_file = Path(sources_file)

    def load_sources(self):
        """Load all sources from sources.json"""
        with open(self.sources_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    def get_all_urls(self):
        """Return a unique list of all URLs"""
        data = self.load_sources()

        urls = []

        for category, category_urls in data.items():
            urls.extend(category_urls)

        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(urls))

        return unique_urls

    def get_category_urls(self, category):
        """Return URLs for a specific category"""
        data = self.load_sources()
        return data.get(category, [])

    def get_categories(self):
        """Return all category names"""
        data = self.load_sources()
        return list(data.keys())