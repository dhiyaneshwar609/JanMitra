from app.ingestion.chunker import split_documents
from app.ingestion.embedding import generate_embeddings

documents = [
    """
    Anna University offers UG and PG courses.
    Admissions are based on TNEA counselling.
    Hostel facilities are available.
    Scholarships are provided for eligible students.
    """
]

chunks = split_documents(documents)

texts, embeddings = generate_embeddings(chunks)

print(f"Total Chunks: {len(texts)}")
print(f"Embedding Shape: {embeddings.shape}")

print("\nFirst Chunk:")
print(texts[0])

print("\nFirst 10 Values of Embedding:")
print(embeddings[0][:10])
