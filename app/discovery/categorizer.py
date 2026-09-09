"""
categorizer.py

Categorizes discovered government URLs into domains.
"""

from urllib.parse import urlparse


class Categorizer:

    def __init__(self):

        self.categories = {
            "Agriculture": [
                "agri",
                "agriculture",
                "farmer",
                "crop",
                "pmkisan",
                "krishi",
                "soil",
                "fertilizer",
                "seed",
                "farming"
            ],

            "Health": [
                "health",
                "hospital",
                "medical",
                "ayush",
                "pmjay",
                "covid",
                "medicine",
                "doctor",
                "wellness"
            ],

            "Education": [
                "education",
                "school",
                "college",
                "student",
                "scholarship",
                "exam",
                "university",
                "ugc",
                "cbse",
                "ncert"
            ],

            "Employment": [
                "employment",
                "labour",
                "labourer",
                "epfo",
                "eshram",
                "skill",
                "job",
                "career",
                "apprentice"
            ],

            "Citizen Services": [
                "uidai",
                "passport",
                "digilocker",
                "service",
                "certificate",
                "identity",
                "aadhaar",
                "ration"
            ],

            "Finance": [
                "income-tax",
                "gst",
                "bank",
                "finance",
                "loan",
                "tax",
                "insurance"
            ],

            "Transport": [
                "transport",
                "road",
                "driving",
                "license",
                "vehicle",
                "rail",
                "metro"
            ],

            "Housing": [
                "housing",
                "awas",
                "home",
                "urban",
                "rural"
            ],

            "Legal": [
                "court",
                "law",
                "justice",
                "grievance",
                "police"
            ]
        }

    def detect_category(self, url):

        text = url.lower()

        for category, keywords in self.categories.items():

            for keyword in keywords:

                if keyword in text:
                    return category

        return "Others"

    def get_name(self, url):

        domain = urlparse(url).netloc

        domain = domain.replace("www.", "")

        return domain

    def categorize(self, urls):

        output = {}

        for url in urls:

            category = self.detect_category(url)

            if category not in output:
                output[category] = []

            output[category].append({

                "name": self.get_name(url),

                "url": url

            })

        return output