class PDFFilter:

    def __init__(self):

        self.good_keywords = [
            "guideline",
            "guidelines",
            "scheme",
            "faq",
            "manual",
            "user",
            "citizen",
            "application",
            "form",
            "benefit",
            "eligibility",
            "document",
            "brochure",
            "booklet"
        ]

        self.bad_keywords = [
            "tender",
            "auction",
            "advertisement",
            "notice",
            "recruitment",
            "vacancy",
            "budget",
            "finance",
            "audit",
            "minutes",
            "meeting",
            "procurement",
            "corrigendum"
        ]

    def is_useful(self, url):

        url = url.lower()

        for word in self.bad_keywords:
            if word in url:
                return False

        for word in self.good_keywords:
            if word in url:
                return True

        return True