from collections import Counter


class KeywordMatcher:
    """
    Computes keyword overlap between the user query
    and retrieved document.
    """

    def __init__(self):
        pass

    def score(self, keywords, document):

        if not keywords:
            return 0.0

        text = (
            document.get("content", "") + " " +
            document.get("title", "") + " " +
            document.get("section_name", "")
        ).lower()
        print("\nTEXT BEING MATCHED:")
        print(text[:300])
        print("Keywords:", keywords)

        words = Counter(text.split())

        score = 0.0

        for keyword in keywords:

            normalized_text = text.replace("-", " ")

            keyword_phrase = keyword.replace("-", " ")

            # Strong bonus for full phrase match
            if keyword_phrase in normalized_text:
                score += 5.0

            # Otherwise check individual words
            else:
                for part in keyword_phrase.split():

                    if len(part) <= 2:
                        continue

                    if part in words:
                        score += 1.0
                        score += min(words[part], 5) * 0.20
        print("Keyword Score:", score)
        return score

    def title_boost(self, keywords, title):

        if not title:
            return 0.0

        title = title.lower()

        boost = 0.0

        for keyword in keywords:

            keyword_phrase = keyword.replace("-", " ")

            # Strong boost for exact scheme name
            if keyword_phrase in title:
                boost += 5.0

            # Fallback for individual important words
            else:
                for part in keyword_phrase.split():

                    if len(part) <= 2:
                        continue

                    if part in title:
                        boost += 1.0

        return boost

    def section_boost(self, question, section):

        if not section:
            return 0.0

        section = section.lower()
        question = question.lower()

        mapping = {
            "benefit": "benefits",
            "eligible": "eligibility",
            "document": "required documents",
            "apply": "application process",
            "registration": "application process",
            "faq": "faq"
        }

        boost = 0.0

        for trigger, sec in mapping.items():

            if trigger in question and sec in section:
                boost += 1.5

        return boost