from app.retrieval.faiss_retriever import FaissRetriever

# Load the saved vector database
retriever = FaissRetriever()

# Ask a question
results = retriever.retrieve(
    "How can I get hostel accommodation?"
)

print("\nRetrieved Results:\n")

for result in results:
    print(result)