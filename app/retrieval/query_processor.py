import re
from typing import List


class QueryProcessor:
    """
    Cleans the user query and extracts important keywords
    for hybrid retrieval.
    """

    def __init__(self):

        self.stop_words = {
                # English
                "the", "is", "are", "was", "were", "a", "an",
                "of", "to", "for", "in", "on", "at", "and",
                "or", "with", "about", "from", "by", "into",
                "what", "which", "who", "when", "where",
                "how", "can", "could", "should", "would",
                "please", 
                "tell", 
                "me",
                "scheme", 
                "schemes",
                "yojana",
                "government",
                "govt",

                "india",
                "indian",
                "program",
                "programme",
                "service",
                 "services",
                 "portal",
                 "official",
                 "pm","scheme",
                 "government",
                 "india","portal",
                 "service"

                # Hindi
                "क्या", "कैसे", "कौन", "कहाँ", "और",

                # Tamil
                "என்ன", "எப்படி", "எங்கு", "மற்றும்"
            }

        self.scheme_aliases = {

            "pm kisan": "pm-kisan",
            "pm-kisan": "pm-kisan",
            "kisan samman nidhi": "pm-kisan",

            "ayushman": "ayushman bharat",
            "pmjay": "ayushman bharat",

            "ration": "ration card",
            "aadhaar": "aadhaar",
            "aadhar": "aadhaar",

            "pan": "pan card",
            "eshram": "e-shram",
            "e shram": "e-shram"
        }
        self.intent_patterns = {
                "definition": [
                    "what is",
                    "define",
                    "explain",
                    "about"
                ],

                "eligibility": [
                    "eligible",
                    "eligibility",
                    "qualify"
                ],

                "application": [
                    "apply",
                    "application",
                    "register"
                ],

                "documents": [
                    "document",
                    "documents",
                    "certificate",
                    "proof"
                ],

                "benefits": [
                    "benefit",
                    "benefits",
                    "amount"
                ],

                "status": [
                    "status",
                    "track"
                ],

                "login": [
                    "login",
                    "sign in"
                ],

                "contact": [
                    "contact",
                    "helpline"
                ]
            }

    def detect_information_need(self, query: str):

        for intent, patterns in self.intent_patterns.items():

            for pattern in patterns:

                if pattern in query:
                    return intent

        return "general"

    def detect_entity(self, query: str):

        # Check official scheme names first
        for official in set(self.scheme_aliases.values()):
            if official in query:
                return official

        # Check aliases
        for alias, official in self.scheme_aliases.items():
            if alias in query:
                return official

        return None

    def clean(self, query: str) -> str:

        query = query.lower()

        query = re.sub(r"[^a-z0-9\s\-]", " ", query)

        query = re.sub(r"\s+", " ", query)

        return query.strip()

    def normalize_scheme_names(self, query: str) -> str:

        normalized = query

        for alias, official in self.scheme_aliases.items():
            normalized = normalized.replace(alias, official)

        return normalized

    def extract_keywords(self, query: str):

            keywords = []

            # Keep complete normalized scheme name
            if "-" in query:
                keywords.append(query)

            words = query.split()

            for word in words:

                if len(word) < 2:
                    continue

                if word in self.stop_words:
                    continue

                keywords.append(word)

            # Remove duplicates while preserving order
            keywords = list(dict.fromkeys(keywords))

            return keywords

    def process(self, query: str):

        cleaned = self.clean(query)
        print("After clean:", cleaned)

        normalized = self.normalize_scheme_names(cleaned)
        print("After normalize:", normalized)

        keywords = self.extract_keywords(normalized)
        print("After extract_keywords:", keywords)

        information_need = self.detect_information_need(cleaned)
        entity = self.detect_entity(normalized)

        return {
            "original": query,
            "cleaned": cleaned,
            "normalized": normalized,
            "entity": entity,
            "keywords": keywords
        }