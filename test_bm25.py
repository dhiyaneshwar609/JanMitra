from app.retrieval.vector_store import VectorStore
from app.retrieval.bm25_retriever import BM25Retriever

store = VectorStore()

store.load(
    "app/data/vector_db/vector_index.faiss",
    "app/data/vector_db/documents.pkl"
)

bm25 = BM25Retriever(store.documents)

results = bm25.search("pm kisan", top_k=5)

for doc, score in results:
    print(f"{score:.2f} | {doc['title']}")