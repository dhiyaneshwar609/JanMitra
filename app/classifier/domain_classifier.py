import numpy as np

from app.classifier.domain_embeddings import DomainEmbeddings
from app.ingestion.embedding import encode_text


class DomainClassifier:
    """
    Semantic Domain Classifier

    Uses SentenceTransformer embeddings to classify
    a user query into one of the supported domains.
    """

    def __init__(self, threshold=0.45):
        self.threshold = threshold

        self.domain_data = DomainEmbeddings()

        self.domain_embeddings = self.domain_data.get_embeddings()

    @staticmethod
    def cosine_similarity(vec1, vec2):
        """
        Compute cosine similarity between two normalized vectors.
        """
        return float(np.dot(vec1, vec2))

    def classify(self, query):
        """
        Returns:
        {
            supported: bool,
            best_domain: str,
            confidence: float,
            top_domains: [(domain, score)]
        }
        """

        query_embedding = encode_text(query)

        scores = []

        for domain, embedding in self.domain_embeddings.items():

            similarity = self.cosine_similarity(
                query_embedding,
                embedding
            )

            scores.append((domain, similarity))

        scores.sort(
            key=lambda x: x[1],
            reverse=True
        )

        best_domain, best_score = scores[0]

        return {
            "supported": best_score >= self.threshold,
            "best_domain": best_domain,
            "confidence": round(best_score, 4),
            "top_domains": scores[:3]
        }