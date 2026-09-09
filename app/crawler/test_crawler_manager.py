from crawler_manager import CrawlerManager

manager = CrawlerManager()

manager.crawl(
    "../data/government_websites.json",
    "../data/raw_documents.json"
)