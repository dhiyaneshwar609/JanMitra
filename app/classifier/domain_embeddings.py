from sentence_transformers import SentenceTransformer
from app.classifier.domain_config import DOMAINS


class DomainEmbeddings:

    def __init__(self):
        # Use the same embedding model as your RAG
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Store embeddings for each domain
        self.domain_embeddings = {}

        self._generate_embeddings()

    def _generate_embeddings(self):
        """
        Generate embeddings for all domain descriptions.
        This runs only once when the application starts.
        """
        for domain, description in DOMAINS.items():

            embedding = self.model.encode(
                description,
                normalize_embeddings=True
            )

            self.domain_embeddings[domain] = embedding

    def get_embeddings(self):
        return self.domain_embeddings

    def get_model(self):
        return self.model