import re
from typing import Dict, List


class QueryUnderstanding:
    """
    Understands the user query before retrieval.
    """

    def __init__(self):

        self.categories = {
            "education": [
                "student",
                "scholarship",
                "college",
                "education",
                "loan",
                "school",
                "vidyalakshmi"
            ],

            "agriculture": [
                "farmer",
                "crop",
                "pm kisan",
                "agriculture",
                "fertilizer",
                "soil"
            ],

            "health": [
                "hospital",
                "health",
                "medical",
                "doctor",
                "ayushman",
                "insurance"
            ],

            "employment": [
                "job",
                "employment",
                "skill",
                "training",
                "internship"
            ],

            "identity": [
                "aadhaar",
                "pan",
                "passport",
                "voter",
                "certificate"
            ],

            "pension": [
                "pension",
                "senior citizen",
                "widow",
                "retirement"
            ]
        }

    def extract_keywords(self, query: str) -> List[str]:

        query = query.lower()
        query = query.replace("-", " ")   # <-- ADD THIS LINE

    # Known scheme/service names

        # Known scheme/service names
        known_entities = [
            "pm kisan",
            "pmay",
            "pm vidyalakshmi",
            "ayushman bharat",
            "aadhaar",
            "digilocker",
            "national scholarship portal",
            "e shram",
            "pm jdy",
            "pm jan dhan"
        ]

        keywords = []

        # Preserve complete scheme names
        for entity in known_entities:
            if entity in query:
                keywords.append(entity)
                query = query.replace(entity, " ")

        words = re.findall(r"\w+", query)

        stop_words = {
            "what",
            "is",
            "the",
            "how",
            "to",
            "for",
            "a",
            "an",
            "of",
            "about",
            "me",
            "tell",
            "please",
            "can",
            "i",
            "apply"
        }

        for word in words:
            if word not in stop_words and len(word) > 2:
                keywords.append(word)

        # Remove duplicates
        return list(dict.fromkeys(keywords))

    def detect_category(self, keywords: List[str]):

        scores = {}

        for category, vocab in self.categories.items():

            score = 0

            for word in keywords:

                if word in vocab:
                    score += 1

            scores[category] = score

        if max(scores.values()) == 0:
            return "general"

        return max(scores, key=scores.get)

    def process(self, query: str) -> Dict:

        print(">>> QueryUnderstanding file:", __file__)

        keywords = self.extract_keywords(query)

        print(">>> Extracted keywords:", keywords)

        category = self.detect_category(keywords)

        return {
            "query": query,
            "keywords": keywords,
            "category": category
    }