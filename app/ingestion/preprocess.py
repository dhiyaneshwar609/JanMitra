import json
import os

from app.utils.text_cleaner import clean_text


RAW_FILE = "app/data/raw/scraped_data.json"
OUTPUT_FILE = "app/data/processed/processed_data.json"
import re

SECTION_HEADINGS = [
    "Overview",
    "Benefits",
    "Eligibility",
    "Required Documents",
    "Application Process",
    "Important Notes",
    "FAQ",
    "FAQs",
    "How to Apply",
    "Documents Required"
]
SCHEME_PATTERN = re.compile(
    r"(Pradhan Mantri\s+[A-Za-z0-9\s\-()]+(?:Yojana|Karyakram|Scheme))",
    re.IGNORECASE
)

def extract_scheme_name(text):
    match = SCHEME_PATTERN.search(text)

    if match:
        return match.group(1).strip()

    return None

GENERIC_TITLES = {
    "pmindia",
    "government of india",
    "home",
    "homepage",
    "index"
}


def get_best_title(page, section):
    """
    Return the most descriptive title possible.
    """

    # 1. Prefer detected scheme name
    scheme = extract_scheme_name(section["content"])
    if scheme:
        return scheme

    title = page.get("title", "").strip()

    # 2. Keep good page titles
    if title and title.lower() not in GENERIC_TITLES:
        return title

    # 3. Use first meaningful sentence
    content = section["content"].strip()

    sentences = re.split(r"[.!?]\s+", content)

    for sentence in sentences:

        sentence = sentence.strip()

        if len(sentence) > 25:
            return sentence[:120]

    # 4. Fallback
    return title if title else "Government Information"


def split_into_sections(text):
    """
    Split page content into logical sections.
    """

    pattern = r"(?=(" + "|".join(map(re.escape, SECTION_HEADINGS)) + r"))"

    parts = re.split(pattern, text)

    sections = []

    current_heading = "General"

    for part in parts:

        part = part.strip()

        if not part:
            continue

        if part in SECTION_HEADINGS:
            current_heading = part
            continue

        sections.append({
            "section": current_heading,
            "content": part
        })

    return sections


def preprocess():

    with open(RAW_FILE, "r", encoding="utf-8") as file:
        pages = json.load(file)

    processed_pages = []

    for page in pages:

        cleaned = clean_text(page["content"])

        sections = split_into_sections(cleaned)

        for section in sections:

         scheme_name = extract_scheme_name(section["content"])

         best_title = get_best_title(page, section)

         processed_pages.append(
         {
            "title": best_title,
            "scheme_name": scheme_name,
            "url": page["url"],
            "category": page.get("category", "General"),
            "page_type": page.get("page_type", "Information"),
            "keywords": page.get("keywords", []),
            "section": section["section"],
            "content": section["content"]
         }
         )

    os.makedirs("app/data/processed", exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            processed_pages,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("=" * 70)
    print("PREPROCESSING COMPLETED")
    print(f"Pages Processed : {len(processed_pages)}")
    print(f"Saved to : {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    preprocess()