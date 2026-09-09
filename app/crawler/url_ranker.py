class URLRanker:

    def __init__(self):

        self.high_priority = [
            "scheme",
            "schemes",
            "initiative",
            "service",
            "services",
            "benefit",
            "welfare",
            "citizen",
            "pm-",
            "pradhan",
            "yojana",
            "application",
            "portal"
        ]

        self.low_priority = [
            "news",
            "gallery",
            "media",
            "press",
            "event",
            "career",
            "recruitment",
            "tender",
            "auction",
            "contact",
            "privacy",
            "terms",
            "feedback"
        ]

    def score(self, url):

        url = url.lower()

        score = 0

        for word in self.high_priority:
            if word in url:
                score += 5

        for word in self.low_priority:
            if word in url:
                score -= 10

        return score