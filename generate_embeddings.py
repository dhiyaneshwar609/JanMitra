import json
from pathlib import Path
import numpy as np

from app.ingestion.embedding import generate_embeddings

BASE_DIR = Path(__file__).resolve().parent

# -------------------------------
# Load chunks
# -------------------------------

chunks_file = BASE_DIR / "app" / "data" / "chunks" / "chunks.json"

with open(chunks_file, "r", encoding="utf-8") as f:
    chunks = json.load(f)

# -------------------------------
# Extract text
# -------------------------------

texts = [chunk["content"] for chunk in chunks]

# -------------------------------
# Generate embeddings
# -------------------------------

_, embeddings = generate_embeddings(texts)

# -------------------------------
# Save embeddings
# -------------------------------

output_dir = BASE_DIR / "app" / "data" / "embeddings"
output_dir.mkdir(parents=True, exist_ok=True)

np.save(output_dir / "embeddings.npy", embeddings)

with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print("=" * 50)
print(f"Chunks Loaded      : {len(chunks)}")
print(f"Embedding Shape    : {embeddings.shape}")
print("Embeddings Saved ✔")
print("Metadata Saved ✔")
print("=" * 50)