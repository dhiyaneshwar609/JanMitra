import faiss
import numpy as np
import pickle
import re


class VectorStore:

    def __init__(self, dimension=384):

        self.index = faiss.IndexFlatIP(dimension)
        self.documents = []

        self.min_relevance_score = 0.15 
        # -------------------------------------------------
    # Add Documents
    # -------------------------------------------------

    def add_documents(self, documents, embeddings):

        embeddings = np.array(
            embeddings,
            dtype="float32"
        )
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)

        self.documents.extend(documents)

    # -------------------------------------------------
    # Keyword Match
    # -------------------------------------------------



    def keyword_score(self, query, text):

        query_words = set(
            re.findall(r"\w+", query.lower())
        )

        text_words = set(
            re.findall(r"\w+", text.lower())
        )

        if not query_words:
            return 0

        overlap = len(query_words & text_words)

        return overlap / len(query_words)
        # -------------------------------------------------
        # Search
        # -------------------------------------------------

    def search(
        self,
        query_embedding,
        query="",
        k=5
    ):

        query_embedding = np.array(
            [query_embedding],
            dtype="float32"
        )
        faiss.normalize_L2(query_embedding)

        search_k = max(k * 3, 15)

        distances, indices = self.index.search(
            query_embedding,
            search_k
        )
        

        results = []

        for distance, idx in zip(
            distances[0],
            indices[0]
        ):

            if idx == -1:
                continue

            document = self.documents[idx]
            

            semantic_score = float(distance)

            keyword = self.keyword_score(
                query,
                document["content"]
            )

            final_score = (
                semantic_score * 0.90 + keyword * 0.10
            )
            if final_score < self.min_relevance_score:
                continue

            results.append({

                "content":
                    document["content"],

                "title":
                    document.get(
                        "title",
                        "Unknown"
                    ),

                "url":
                    document.get(
                        "url",
                        ""
                    ),

                "distance":
                    float(distance),

                "semantic_score":
                    round(
                        semantic_score,
                        3
                    ),

                "keyword_score":
                    round(
                        keyword,
                        3
                    ),

                "relevance":
                    round(
                        final_score,
                        3
                    )

            })

        results.sort(
            key=lambda x: x["relevance"],
            reverse=True
        )

        unique_results = []
        seen_text = set()

        for result in results:

            text = result["content"].strip()

            if text not in seen_text:
                seen_text.add(text)
                unique_results.append(result)

        return unique_results[:k]

    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    def save(
        self,
        index_path,
        docs_path
    ):

        faiss.write_index(
            self.index,
            index_path
        )

        with open(
            docs_path,
            "wb"
        ) as file:

            pickle.dump(
                self.documents,
                file
            )

    # -------------------------------------------------
    # Load
    # -------------------------------------------------

    def load(
        self,
        index_path,
        docs_path
    ):

        self.index = faiss.read_index(
            index_path
        )

        with open(
            docs_path,
            "rb"
        ) as file:

            self.documents = pickle.load(
                file
            )
