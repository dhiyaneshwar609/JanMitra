import re


# Common boilerplate phrases found across government websites
REMOVE_PATTERNS = [
    r"home",
    r"calendar",
    r"cpgrams",
    r"skip to content",
    r"could not find what you were looking for\??",
    r"explore\s*:?",
    r"quick links",
    r"feedback",
    r"copyright.*",
    r"all rights reserved.*",
    r"privacy policy",
    r"terms\s*&?\s*conditions",
    r"accessibility statement",
    r"screen reader",
    r"contact us",
    r"follow us",
    r"powered by.*",
    r"back to top",
    r"select a holiday",
    r"help us improve.*",
    r"suggest / report a service",
    r"source:.*",
]


def remove_boilerplate(text: str) -> str:

    cleaned_lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        skip = False

        lower = line.lower()

        for pattern in REMOVE_PATTERNS:
            if re.search(pattern, lower):
                skip = True
                break

        if not skip:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def remove_duplicate_lines(text: str) -> str:

    seen = set()
    output = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line in seen:
            continue

        seen.add(line)
        output.append(line)

    return "\n".join(output)


def clean_text(text):

    if not text:
        return ""

    # Remove HTML entities
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)

    # Remove URLs
    text = re.sub(r"https?://\S+", " ", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove unwanted symbols
    text = re.sub(r"[^\w\s.,!?():;/@%-]", " ", text)

    # Remove repeated spaces
    text = re.sub(r"\s+", " ", text)

    # Remove boilerplate
    text = remove_boilerplate(text)

    # Remove duplicate lines
    text = remove_duplicate_lines(text)

    # Final cleanup
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()