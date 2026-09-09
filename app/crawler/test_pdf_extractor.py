from pdf_extractor import PDFExtractor

extractor = PDFExtractor()

result = extractor.extract(
    "https://www.odisha.gov.in/sites/default/files/2026-07/3646.pdf"
)

if result:

    print(result["title"])
    print()
    print(result["content"][:2000])

else:

    print("Extraction failed.")