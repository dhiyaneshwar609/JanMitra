class Ranker:
    """
    Combines semantic similarity, keyword matching,
    title matching, and section matching into one score.
    """

    def __init__(self):

        # Weight configuration
        self.semantic_weight = 0.60
        self.keyword_weight = 0.20
        self.title_weight = 0.15
        self.section_weight = 0.05

    def semantic_score(self, distance):

        """
        Convert FAISS distance into similarity.
        Lower distance -> Higher similarity.
        """

        similarity = max(0.0, 1.0 - (distance / 2.0))

        return similarity

    def final_score(
        self,
        distance,
        keyword_score,
        title_boost,
        section_boost
    ):

        semantic = self.semantic_score(distance)

        keyword = min(keyword_score / 5.0, 1.0)

        title = min(title_boost / 4.0, 1.0)

        section = min(section_boost / 3.0, 1.0)

        score = (
            semantic * self.semantic_weight
            + keyword * self.keyword_weight
            + title * self.title_weight
            + section * self.section_weight
        )

        return round(score, 4)