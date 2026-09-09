from app.classifier.domain_embeddings import DomainEmbeddings

emb = DomainEmbeddings()

print("Domains Loaded:\n")

for domain in emb.get_embeddings():
    print(domain)

print("\nTotal Domains:", len(emb.get_embeddings()))