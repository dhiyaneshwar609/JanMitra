import re


class ConfidenceEngine:
    """
    Production Confidence Engine for Hybrid RAG.

    Confidence Score:
        0.0 → 1.0

    Uses five independent signals:
        1. Semantic Similarity
        2. Keyword Coverage
        3. Retrieval Consistency
        4. Document Coverage
        5. Source Trust
    """

    def __init__(self):

        self.weights = {
            "semantic": 0.40,
            "keyword": 0.20,
            "consistency": 0.15,
            "coverage": 0.15,
            "source": 0.10,
        }

    # -------------------------------------------------
    # Semantic Score
    # -------------------------------------------------

    def semantic_score(self, distances):

        if not distances:
            return 0.0

        avg = sum(distances) / len(distances)

        # Calibrated for FAISS L2 + MiniLM embeddings

        if avg <= 0.50:
            return 1.00

        elif avg <= 1.00:
            return 0.95

        elif avg <= 1.50:
            return 0.90

        elif avg <= 2.00:
            return 0.85

        elif avg <= 2.50:
            return 0.75

        elif avg <= 3.00:
            return 0.65

        elif avg <= 4.00:
            return 0.55

        else:
            return 0.40

    # -------------------------------------------------
    # Keyword Match
    # -------------------------------------------------

    def keyword_score(self, query, docs):

        query_words = set(
            re.findall(r"\w+", query.lower())
        )

        if not query_words:
            return 0.0

        document_words = set()

        for doc in docs:

            document_words.update(
                re.findall(
                    r"\w+",
                    doc["content"].lower()
                )
            )

        overlap = len(
            query_words &
            document_words
        )

        return overlap / len(query_words)

    # -------------------------------------------------
    # Consistency
    # -------------------------------------------------

    def consistency_score(self, distances):

        if len(distances) <= 1:
            return 1.0

        spread = max(distances) - min(distances)

        if spread < 0.05:
            return 1.0

        elif spread < 0.15:
            return 0.95

        elif spread < 0.30:
            return 0.90

        elif spread < 0.50:
            return 0.80

        elif spread < 1.00:
            return 0.70

        return 0.55

    # -------------------------------------------------
    # Coverage
    # -------------------------------------------------

    def coverage_score(self, docs):

        count = len(docs)

        if count >= 5:
            return 1.0

        elif count == 4:
            return 0.95

        elif count == 3:
            return 0.90

        elif count == 2:
            return 0.80

        elif count == 1:
            return 0.70

        return 0.0

    # -------------------------------------------------
    # Source Trust
    # -------------------------------------------------

    def source_score(self, docs):

        if not docs:
            return 0.0

        total = 0

        for doc in docs:

            url = doc.get("url", "").lower()

            if ".gov.in" in url:
                total += 1.0

            elif ".nic.in" in url:
                total += 1.0

            elif ".edu" in url:
                total += 0.95

            elif ".org" in url:
                total += 0.90

            else:
                total += 0.75

        return total / len(docs)

    # -------------------------------------------------
    # Final Confidence
    # -------------------------------------------------

    def calculate(self, query, docs):

        if not docs:
            return 0.0

        distances = [
            doc["distance"]
            for doc in docs
        ]

        semantic = self.semantic_score(distances)

        keyword = self.keyword_score(
            query,
            docs
        )

        consistency = self.consistency_score(
            distances
        )

        coverage = self.coverage_score(
            docs
        )

        source = self.source_score(
            docs
        )

        confidence = (
            semantic * self.weights["semantic"]
            + keyword * self.weights["keyword"]
            + consistency * self.weights["consistency"]
            + coverage * self.weights["coverage"]
            + source * self.weights["source"]
        )

        confidence = min(
            max(confidence, 0.0),
            1.0
        )

        return round(confidence, 3)