from pathlib import Path

# App Root (app/)
APP_DIR = Path(__file__).resolve().parent.parent

# Data Folders
DATA_DIR = APP_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTOR_DB_DIR = DATA_DIR / "vector_db"

# Sources File
SOURCES_FILE = DATA_DIR / "raw" / "sources_final_cleaned.json"