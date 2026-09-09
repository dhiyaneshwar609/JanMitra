from app.crawler.content_extractor import ContentExtractor

extractor = ContentExtractor()

result = extractor.extract(
    "https://www.digitalindia.gov.in/initiative/pm-kisan/"
)

if result is None:
    print("Extraction failed!")
else:
    print("=" * 80)
    print("TITLE:", result["title"])
    print("CONTENT LENGTH:", len(result["content"]))
    print("=" * 80)
    print(result["content"][:4000])   # Print first 4000 characters
    print("=" * 80)