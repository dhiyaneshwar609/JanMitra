import json
import re
from pathlib import Path

RAW_DATA = Path("app/data/raw/scraped_data.json")
OUTPUT_DATA = Path("app/data/cleaned/cleaned_data.json")


REMOVE_PATTERNS = [
    r"skip to main content",
    r"read more",
    r"click here",
    r"view more",
    r"view all",
    r"last updated.*",
    r"follow us.*",
    r"share.*",
    r"facebook",
    r"twitter",
    r"instagram",
    r"linkedin",
    r"youtube",
    r"copyright.*",
    r"all rights reserved.*",
    r"privacy policy",
    r"cookie policy",
    r"terms and conditions",
    r"visitor count.*",
    r"page last updated.*",
]


MIN_WORDS = 40


def normalize_whitespace(text):
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def remove_patterns(text):
    cleaned = text

    for pattern in REMOVE_PATTERNS:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE
        )

    return cleaned


def remove_duplicate_lines(text):

    seen = set()
    output = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        key = line.lower()

        if key in seen:
            continue

        seen.add(key)
        output.append(line)

    return "\n".join(output)


def remove_repeated_sentences(text):

    seen = set()
    sentences = []

    parts = re.split(r'(?<=[.!?])\s+', text)

    for sentence in parts:

        sentence = sentence.strip()

        if len(sentence) < 10:
            continue

        key = sentence.lower()

        if key in seen:
            continue

        seen.add(key)
        sentences.append(sentence)

    return " ".join(sentences)


def clean_content(text):

    if not text:
        return ""

    text = normalize_whitespace(text)
    text = remove_patterns(text)
    text = remove_duplicate_lines(text)
    text = remove_repeated_sentences(text)

    # Preserve paragraph breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def is_good_content(text):

    if not text:
        return False

    if len(text.split()) < MIN_WORDS:
        return False

    if len(text) < 250:
        return False

    return True

def load_data():

    with open(RAW_DATA, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):

    OUTPUT_DATA.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_DATA, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def process_records(records):

    cleaned_records = []

    duplicate_checker = set()

    removed = 0

    for record in records:

        content = record.get("content", "")

        cleaned = clean_content(content)

        if not is_good_content(cleaned):
            removed += 1
            continue

        key = cleaned.lower()

        if key in duplicate_checker:
            removed += 1
            continue

        duplicate_checker.add(key)

        record["content"] = cleaned

        cleaned_records.append(record)

    return cleaned_records, removed


def main():

    print("=" * 60)
    print("CONTENT CLEANER")
    print("=" * 60)

    data = load_data()

    print(f"Input Records : {len(data)}")

    cleaned_data, removed = process_records(data)

    save_data(cleaned_data)

    print(f"Removed Records : {removed}")
    print(f"Saved Records   : {len(cleaned_data)}")
    print(f"Output File     : {OUTPUT_DATA}")

    print("=" * 60)
    print("Cleaning Completed Successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()