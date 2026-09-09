import json
from pathlib import Path

from langchain_core.documents import Document
from app.ingestion.chunker import split_documents

BASE_DIR = Path(__file__).resolve().parent

# Read cleaned documents
with open(BASE_DIR / "app" / "data" / "processed" / "processed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert JSON to LangChain Documents
documents = []

for doc in data:
    documents.append(
        Document(
            page_content=doc["content"],
            metadata={
    "url": doc["url"],
    "title": doc["title"],
    "category": doc.get("category", "General"),
    "page_type": doc.get("page_type", "Information"),
    "section_name": doc.get("section", "General"),
    "keywords": doc.get("keywords", []),
},
        )
    )

# Split into chunks
chunks = split_documents(documents)

# Save chunks
output = []

for chunk in chunks:
    output.append({
        "content": chunk.page_content,
        **chunk.metadata
    })

output_dir = BASE_DIR / "app" / "data" / "chunks"
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "chunks.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Generated {len(chunks)} chunks")