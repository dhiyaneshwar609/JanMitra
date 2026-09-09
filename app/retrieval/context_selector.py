from collections import OrderedDict


class ContextSelector:
    """
    Select only the best context for the LLM.
    """

    def select(self, documents, top_k=5):

        if not documents:
            return []

        # Remove duplicate URLs
        # Remove duplicate content instead of duplicate URLs
        unique_docs = OrderedDict()

        for doc in documents:

            key = (
                doc.get("title", "") +
                doc.get("content", "")[:200]
            )

            if key not in unique_docs:
                unique_docs[key] = doc

        documents = list(unique_docs.values())
        # Sort by final score
        documents.sort(
            key=lambda x: x.get("final_score", 0),
            reverse=True
        )

        # Dynamic threshold
        best_score = documents[0].get("final_score", 0)

        selected = []

        for doc in documents:

            score = doc.get("final_score", 0)

            if score >= best_score * 0.75:
                selected.append(doc)

            if len(selected) >= top_k:
                break

        return selected