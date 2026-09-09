from urllib.parse import urlparse, urlunparse
import tldextract


class URLFilter:

    ALLOWED_SUFFIXES = {
        "gov.in",
        "nic.in",
        "ac.in"
    }

    SKIP_SCHEMES = {
        "mailto",
        "javascript",
        "tel"
    }

    SKIP_PATTERNS = [
        "login",
        "logout",
        "signin",
        "search",
        "print",
        "feedback",
        "facebook",
        "twitter",
        "instagram",
        "youtube",
        "linkedin",
        "whatsapp",
        "share"
    ]

    def normalize(self, url):

        if not url:
            return None

        url = url.strip()

        parsed = urlparse(url)

        # Skip unsupported schemes
        if parsed.scheme in self.SKIP_SCHEMES:
            return None

        # Force HTTPS
        scheme = "https"

        # Remove fragments (#main)
        fragment = ""

        # Remove duplicate trailing slash
        path = parsed.path.rstrip("/")

        normalized = urlunparse((
            scheme,
            parsed.netloc.lower(),
            path,
            "",
            parsed.query,
            fragment
        ))

        return normalized

    def is_allowed_domain(self, url):

        ext = tldextract.extract(url)

        return ext.suffix in self.ALLOWED_SUFFIXES

    def is_valid(self, url):

        url = self.normalize(url)

        if url is None:
            return False

        if not self.is_allowed_domain(url):
            return False

        lower = url.lower()

        for pattern in self.SKIP_PATTERNS:
            if pattern in lower:
                return False

        return True