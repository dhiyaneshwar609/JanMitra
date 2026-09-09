from app.ingestion.source_manager import SourceManager

sm = SourceManager()

print("Categories:")
print(sm.get_categories())

print()

print("Total URLs:")
print(len(sm.get_all_urls()))