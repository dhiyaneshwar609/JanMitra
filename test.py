from app.ingestion.embedding import generate_embeddings

texts, embeddings = generate_embeddings(["Hello World"])

print("SUCCESS")
print(texts)
print(embeddings.shape)