from urllib.parse import urlparse

SCHEME_KEYWORDS = [
    "scheme", "schemes", "service", "services",
    "apply", "application", "eligibility",
    "benefits", "documents", "guidelines",
    "faq", "citizen", "registration"
]

NEWS_KEYWORDS = [
    "news", "press", "press-release",
    "event", "events", "gallery",
    "media", "speech", "conference",
    "meeting", "advertisement",
    "announcement"
]

REPORT_KEYWORDS = [
    "annual-report",
    "report",
    "survey",
    "statistics",
    "publication",
    "bulletin"
]

FORM_KEYWORDS = [
    "form",
    "download",
    "pdf",
    "application-form"
]


def classify_document(title="", url=""):
    text = f"{title} {url}".lower()

    if any(k in text for k in NEWS_KEYWORDS):
        return "news"

    if any(k in text for k in REPORT_KEYWORDS):
        return "report"

    if any(k in text for k in FORM_KEYWORDS):
        return "form"

    if any(k in text for k in SCHEME_KEYWORDS):
        return "scheme"

    return "general"