from collections import OrderedDict

from app.retrieval.reranker import Reranker
from app.retrieval.query_understanding import QueryUnderstanding
from app.retrieval.context_selector import ContextSelector


class HybridRetriever:

    def __init__(self, faiss_retriever, bm25_retriever):
        self.faiss = faiss_retriever
        self.bm25 = bm25_retriever
        self.reranker = Reranker()
        self.query_understanding = QueryUnderstanding()
        self.context_selector = ContextSelector()

    def search(self, query, query_embedding, top_k=20):

        analysis = self.query_understanding.process(query)
        
        keywords = analysis["keywords"]
        category = analysis["category"]
        entity = analysis.get("entity")
        
        print("\n===== QUERY UNDERSTANDING =====")
        print("Keywords :", keywords)
        print("Category :", category)

        # Retrieve candidates
        faiss_results = self.faiss.search(
            query_embedding=query_embedding,
            query=query,
            k=top_k
        )

        bm25_results = self.bm25.search(
            query=query,
            top_k=top_k
        )
        

        merged = OrderedDict()

        # Add FAISS results
        for doc in faiss_results:

            key = (
                doc.get("url", "")
                + doc.get("title", "")
                + doc.get("content", "")[:100]
            )

            merged[key] = doc

        # Add BM25 results
        for doc, score in bm25_results:

            key = (
                doc.get("url", "")
                + doc.get("title", "")
                + doc.get("content", "")[:100]
            )

            if key not in merged:
                doc["bm25_score"] = float(score)

                # Default values so downstream ranking works
                doc.setdefault("distance", 0.0)
                doc.setdefault("semantic_score", 0.0)
                doc.setdefault("keyword_score", 0.0)
                doc.setdefault("relevance", 0.0)

                merged[key] = doc

        candidates = list(merged.values())
        # ---------------- Entity Filtering ----------------

        if entity:

            entity_docs = []

            aliases = {
                "pm-kisan": [
                    "pm kisan",
                    "pm-kisan",
                    "pradhan mantri kisan samman nidhi"
                ],
                "ayushman bharat": [
                    "ayushman",
                    "pmjay",
                    "ayushman bharat"
                ],
                "ration card": [
                    "ration",
                    "ration card"
                ]
            }

            entity_words = aliases.get(entity, [entity])

            for doc in candidates:

                text = (
                    doc.get("title", "") + " " +
                    doc.get("content", "")[:1000]
                ).lower()

                if any(word in text for word in entity_words):
                    entity_docs.append(doc)

            # Use filtered docs only if we found matches
            if entity_docs:
                print(f"Entity filter: {len(entity_docs)} / {len(candidates)} kept")
                candidates = entity_docs

        # Rerank candidates
        reranked = self.reranker.rerank(
    query=query,
    documents=candidates,
    keywords=keywords,
    category=category,
    top_k=top_k
)
        selected = self.context_selector.select(
    reranked,
    top_k=min(top_k, 5)
)

        return selected