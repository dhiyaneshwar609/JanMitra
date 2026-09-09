"""
discovery_manager.py

Coordinates the complete discovery process.
"""
from homepage_crawler import HomepageCrawler
import json
from pathlib import Path

from robots_parser import RobotsParser
from sitemap_parser import SitemapParser
from categorizer import Categorizer


class DiscoveryManager:

    def __init__(self):

        self.robots = RobotsParser()
        self.sitemap = SitemapParser()
        self.categorizer = Categorizer()
        self.homepage = HomepageCrawler()

    def load_sources(self, filepath):

        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def discover_from_site(self, website):

        print(f"\nDiscovering : {website}")

        robot_data = self.robots.parse(website)

        urls = []

        if robot_data["sitemaps"]:

            print(f"Found {len(robot_data['sitemaps'])} sitemap(s)")

            for sitemap in robot_data["sitemaps"]:
                urls.extend(self.sitemap.parse(sitemap))

        else:

            print("No sitemap found.")
            print("Using homepage crawler...")

            urls.extend(self.homepage.crawl(website))

        return urls
    

    def run(self, source_file, output_file):

        data = self.load_sources(source_file)

        all_urls = []

        # Central websites
        for website in data.get("central", []):

            all_urls.extend(
                self.discover_from_site(website)
            )

        # State websites
        for website in data.get("states", []):

            all_urls.extend(
                self.discover_from_site(website)
            )

        # Remove duplicates
        all_urls = list(set(all_urls))

        print("\nTotal URLs:", len(all_urls))

        categorized = self.categorizer.categorize(all_urls)

        with open(output_file, "w", encoding="utf-8") as f:

            json.dump(
                categorized,
                f,
                indent=4,
                ensure_ascii=False
            )

        print("\nSaved:", output_file)