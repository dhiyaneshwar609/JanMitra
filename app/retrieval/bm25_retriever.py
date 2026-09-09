from rank_bm25 import BM25Okapi
import re


class BM25Retriever:

    def __init__(self, documents):
        self.documents = documents

        

        corpus = []

        for doc in documents:

            text = " ".join([
                doc.get("title", ""),
                doc.get("content", ""),
                doc.get("section_name", "")
            ]).lower()

            corpus.append(
                re.findall(r"\w+(?:-\w+)?", text)
            )

        self.bm25 = BM25Okapi(corpus)

    def search(self, query, top_k=20):
       

        tokens = re.findall(r"\w+(?:-\w+)?", query.lower())

        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_k]