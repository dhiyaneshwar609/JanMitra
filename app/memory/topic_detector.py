import re


class TopicDetector:

    FOLLOW_UP_WORDS = {
        "it",
        "its",
        "they",
        "them",
        "their",
        "this",
        "that",
        "these",
        "those",
        "more",
        "continue",
        "explain",
        "elaborate",
        "details",
        "why",
        "how",
        "benefits",
        "documents",
        "eligibility",
        "application"
    }

    @staticmethod
    def is_follow_up(question):

        question = question.lower().strip()

        words = re.findall(r"\w+", question)

        if not words:
            return False

        if words[0] in TopicDetector.FOLLOW_UP_WORDS:
            return True

        return False