from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self):
        # Load once during application startup
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
    self,
    query,
    documents,
    keywords,
    category,
    top_k=5
):
        """
        Rerank candidate documents using a CrossEncoder.
        """
        print("\n===== RERANK INPUT =====")
        print("Category :", category)
        print("Keywords :", keywords)
        if not documents:
            return []

        pairs = []

        for doc in documents:
            pairs.append([
                query,
                doc.get("content", "")
            ])

        scores = self.model.predict(pairs)
        for doc, score in zip(documents, scores):

            doc["rerank_score"] = float(score)

            semantic = float(doc.get("semantic_score", 0.0))
            bm25 = float(doc.get("bm25_score", 0.0))
            keyword = float(doc.get("keyword_score", 0.0))

            title = doc.get("title", "").lower()
            document_type = doc.get("document_type", "general")

            document_type_boost = {
                "scheme": 1.0,
                "service": 1.0,
                "faq": 0.8,
                "form": 0.6,
                "general": 0.0,
                "report": -0.5,
                "news": -1.0
            }.get(document_type, 0.0)

            title_boost = 0.0
            

            for word in keywords:
                if word.lower() in title:
                    title_boost += 0.2

            doc["final_score"] = (
                0.45 * doc["rerank_score"] +
                0.20 * semantic +
                0.15 * bm25 +
                0.10 * keyword +
                0.10 * title_boost +
                document_type_boost
            )

        print("\n===== FINAL SCORES =====")

        for doc in documents:

            print(
                f'{doc["final_score"]:.3f} | '
                f'{doc.get("title")}'
            )

        documents.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return documents[:top_k]