import re


class EntityExtractor:

    def extract(self, question, previous_entity=None):

        q = question.lower()

        # Known government schemes
        entities = [
            "pm kisan",
            "ayushman bharat",
            "my bharat",
            "pm awas yojana",
            "nsp",
            "e shram",
            "epfo",
            "digilocker",
            "abha",
            "ujjwala",
            "jan dhan"
        ]

        # Check if user explicitly mentioned a scheme
        for entity in entities:

            if entity in q:
                return entity.title()

        # Otherwise continue previous topic
        return previous_entity