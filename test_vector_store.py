from app.ingestion.chunker import split_documents
from app.ingestion.embedding import generate_embeddings
from app.retrieval.vector_store import VectorStore

documents = [
    """
    Anna University offers UG and PG courses.
    Admissions are based on TNEA counselling.
    Hostel facilities are available.
    Scholarships are provided for eligible students.
    """
]

# Step 1: Chunk
chunks = split_documents(documents)

# Step 2: Embed
texts, embeddings = generate_embeddings(chunks)

# Step 3: Store
vector_store = VectorStore()
vector_store.add_documents(texts, embeddings)

# Step 4: Query
query = ["How can I get hostel accommodation?"]
_, query_embedding = generate_embeddings(split_documents(query))

results = vector_store.search(query_embedding[0])

print("Search Results:\n")

for result in results:
    print(result)