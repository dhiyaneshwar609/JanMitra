from pathlib import Path
from collections import OrderedDict

from app.retrieval.vector_store import VectorStore
from app.ingestion.embedding import generate_embeddings

from app.retrieval.query_processor import QueryProcessor
from app.retrieval.keyword_matcher import KeywordMatcher
from app.retrieval.ranker import Ranker
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.hybrid_retriever import HybridRetriever

import numpy as np

class FaissRetriever:

    def __init__(self):

        self.vector_store = VectorStore()

        base_dir = Path(__file__).resolve().parent.parent
        vector_db_dir = base_dir / "data" / "vector_db"

        index_path = vector_db_dir / "vector_index.faiss"
        docs_path = vector_db_dir / "documents.pkl"

        self.vector_store.load(
            str(index_path),
            str(docs_path)
        )
        # Initialize BM25
        self.bm25 = BM25Retriever(self.vector_store.documents)

        # Initialize Hybrid Retriever
        self.hybrid_retriever = HybridRetriever(
            self.vector_store,
            self.bm25
        )

        # ---------------------------------------------
        # Advanced Retrieval Components
        # ---------------------------------------------
        self.query_processor = QueryProcessor()
        self.keyword_matcher = KeywordMatcher()
        self.ranker = Ranker()

        # ---------------------------------------------
        # Retrieval Configuration
        # ---------------------------------------------
        self.initial_k = 20
        self.max_results = 3
    def retrieve(self, query, top_k=None):

        if top_k is None:
            top_k = self.max_results

        # ---------------------------------------------
        # Process Query
        # ---------------------------------------------
        processed = self.query_processor.process(query)

        normalized_query = processed.get("normalized", "")
        keywords = processed.get("keywords", [])
        intent = processed.get("intent", "other")

        # ---------------------------------------------
        # Safe Query Fallback
        # ---------------------------------------------
        # If query processing produces an empty string,
        # use the original user query instead.
        if not normalized_query or not normalized_query.strip():
            normalized_query = query.strip()

        # If the original query is also empty, stop safely.
        if not normalized_query:
            return []

        # ---------------------------------------------
        # Generate Query Embedding
        # ---------------------------------------------
        _, embeddings = generate_embeddings([normalized_query])

        query_embedding = embeddings[0]

        # ---------------------------------------------
        # Retrieve Candidate Documents
        # ---------------------------------------------
        candidates = self.hybrid_retriever.search(
            query=normalized_query,
            query_embedding=query_embedding,
            top_k=self.initial_k
        )

        if not candidates:
            return []

        # ---------------------------------------------
        # Distance Filtering
        # ---------------------------------------------
        filtered = candidates

        # ---------------------------------------------
        # Re-Rank Results
        # ---------------------------------------------
        ranked_results = []

        for doc in filtered:

            print("Extracted Keywords:", keywords)

            keyword_score = self.keyword_matcher.score(
                keywords,
                doc
            )

            title_boost = self.keyword_matcher.title_boost(
                keywords,
                doc.get("title", "")
            )

            section_boost = self.keyword_matcher.section_boost(
                normalized_query,
                doc.get("section", "")
            )

            section_name = (
                doc.get("section_name", "")
                .lower()
            )

            intent_section_map = {
                "overview": "overview",
                "eligibility": "eligibility",
                "benefits": "benefits",
                "documents": "required documents",
                "application": "application process",
                "status": "status"
            }

            intent_boost = 0.0

            expected_section = intent_section_map.get(intent)

            if expected_section and expected_section in section_name:
                intent_boost = 0.30

            print(
                f"Intent={intent}, "
                f"Section={section_name}, "
                f"Boost={intent_boost}"
            )

            # ---------------------------------------------
            # Exact Scheme Match Bonus
            # ---------------------------------------------
            scheme_bonus = 0.0

            query_words = set(
                normalized_query.lower().split()
            )

            title_text = doc.get("title", "").lower()
            content_text = doc.get("content", "").lower()

            title_matches = sum(
                1
                for word in query_words
                if len(word) > 2 and word in title_text
            )

            content_matches = sum(
                1
                for word in query_words
                if len(word) > 2 and word in content_text
            )

            if title_matches >= 2:
                scheme_bonus += 0.30

            if content_matches >= 2:
                scheme_bonus += 0.20

            # ---------------------------------------------
            # Final Score
            # ---------------------------------------------
            final_score = (
                self.ranker.final_score(
                    distance=doc["distance"],
                    keyword_score=keyword_score,
                    title_boost=title_boost,
                    section_boost=section_boost
                )
                + intent_boost
                + scheme_bonus
            )

            print(
                f"Scheme Bonus: {scheme_bonus:.2f} | "
                f"Title: {doc.get('title')}"
            )

            doc["keyword_score"] = keyword_score
            doc["title_boost"] = title_boost
            doc["section_boost"] = section_boost
            doc["final_score"] = final_score

            print("\n------------------------")
            print("Title:", doc.get("title"))
            print("Distance:", doc["distance"])
            print("Keyword:", keyword_score)
            print("Title Boost:", title_boost)
            print("Section Boost:", section_boost)
            print("Final Score:", final_score)
            print("URL:", doc.get("url"))

            ranked_results.append(doc)

        # ---------------------------------------------
        # Sort by Final Score
        # ---------------------------------------------
        ranked_results.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        # ---------------------------------------------
        # Remove Duplicate URLs
        # ---------------------------------------------
        unique_docs = []
        seen_urls = set()

        for doc in ranked_results:

            if doc["url"] in seen_urls:
                continue

            unique_docs.append(doc)
            seen_urls.add(doc["url"])

            if len(unique_docs) >= top_k:
                break

        # ---------------------------------------------
        # Display Retrieved Documents
        # ---------------------------------------------
        print("\n===== RETRIEVED DOCUMENTS =====")

        for i, doc in enumerate(unique_docs[:top_k], 1):

            print(f"\nResult {i}")
            print("Keys:", list(doc.keys()))
            print("Title:", doc.get("title"))
            print("URL:", doc.get("url"))
            print("Final Score:", doc.get("final_score"))

            content = (
                doc.get("text")
                or doc.get("content")
                or doc.get("page_content")
                or ""
            )

            print("Content:", content[:500])

        return unique_docs[:top_k]
            