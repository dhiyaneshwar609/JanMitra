import json
from pathlib import Path

import numpy as np

from app.retrieval.vector_store import VectorStore


# ============================================
# Paths
# ============================================

EMBEDDINGS_FILE = Path("app/data/embeddings/embeddings.npy")
METADATA_FILE = Path("app/data/embeddings/metadata.json")

VECTOR_DIR = Path("app/data/vector_db")
VECTOR_DIR.mkdir(parents=True, exist_ok=True)


# ============================================
# Load Data
# ============================================

print("Loading embeddings...")

embeddings = np.load(EMBEDDINGS_FILE)

with open(METADATA_FILE, "r", encoding="utf-8") as f:
    documents = json.load(f)

print(f"Documents : {len(documents)}")
print(f"Embeddings: {embeddings.shape}")


# ============================================
# Build Vector Store
# ============================================

print("\nBuilding FAISS Index...")

vector_store = VectorStore()

vector_store.add_documents(
    documents,
    embeddings
)


# ============================================
# Save Index
# ============================================

vector_store.save(
    str(VECTOR_DIR / "vector_index.faiss"),
    str(VECTOR_DIR / "documents.pkl")
)

print("\n======================================")
print("FAISS INDEX CREATED SUCCESSFULLY")
print("======================================")