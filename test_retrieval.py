from app.retrieval.faiss_retriever import FaissRetriever

retriever = FaissRetriever()

results = retriever.retrieve("What is PM Kisan?")

for i, result in enumerate(results, 1):
    print("=" * 80)
    print(f"Result {i}")
    print("Title:", result.get("title"))
    print("URL:", result.get("url"))
    print("Score:", result.get("final_score"))
    print(result.get("content", "")[:800])