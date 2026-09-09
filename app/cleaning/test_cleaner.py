from pathlib import Path
from app.cleaning.cleaner import DataCleaner

cleaner = DataCleaner()

BASE_DIR = Path(__file__).resolve().parent.parent

cleaner.clean_file(
    BASE_DIR / "data" / "raw_documents.json",
    BASE_DIR / "data" / "cleaned" / "cleaned_data.json"
)