from sitemap_parser import SitemapParser

parser = SitemapParser()

urls = parser.parse(
    "https://www.india.gov.in/sitemap.xml"
)

print()

print("TOTAL URLS:", len(urls))

print()

for u in urls[:20]:
    print(u)