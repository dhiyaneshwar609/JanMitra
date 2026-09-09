from homepage_crawler import HomepageCrawler

crawler = HomepageCrawler(
    max_depth=2,
    max_pages=100
)

urls = crawler.crawl("https://www.tn.gov.in")

print()

print("TOTAL URLS:", len(urls))

print()

for url in urls[:50]:
    print(url)