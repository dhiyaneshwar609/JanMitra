import json
import os
import re
import time
import fitz

from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from bs4 import BeautifulSoup

from app.core.config import SOURCES_FILE


# =============================================================================
# HTTP SESSION
# =============================================================================

session = requests.Session()

retry_strategy = Retry(
    total=3,
    connect=3,
    read=3,
    backoff_factor=2,
    status_forcelist=[
        429,
        500,
        502,
        503,
        504
    ],
    allowed_methods=["GET", "HEAD"]
)

adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=20,
    pool_maxsize=20
)

session.mount("http://", adapter)
session.mount("https://", adapter)

session.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        ),
        "Accept-Language": "en-IN,en;q=0.9"
    }
)


# =============================================================================
# FILE PATHS
# =============================================================================

CHECKPOINT_FILE = "app/data/raw/checkpoint.json"

CRAWL_CHECKPOINT_FILE = "app/data/raw/crawl_checkpoint.json"

SCRAPED_FILE = "app/data/raw/scraped_data.json"

FAILED_FILE = "app/data/raw/failed_urls.json"


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

MAX_PAGES = 100

REQUEST_TIMEOUT = 25

MAX_RETRIES = 3

failed_urls = []

session.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
        ),
        "Accept-Language": "en-IN,en;q=0.9"
    }
)
# File paths
CHECKPOINT_FILE = "app/data/raw/checkpoint.json"
CRAWL_CHECKPOINT_FILE = "app/data/raw/crawl_checkpoint.json"
SCRAPED_FILE = "app/data/raw/scraped_data.json"
FAILED_FILE = "app/data/raw/failed_urls.json"

# Maximum pages to crawl per website
MAX_PAGES = 100

IMPORTANT_KEYWORDS = [
    "scheme",
    "schemes",
    "pm",
    "kisan",
    "farmer",
    "agriculture",
    "health",
    "education",
    "scholarship",
    "benefits",
    "eligibility",
    "documents",
    "application",
    "services",
    "welfare",
    "citizen",
    "pension",
    "employment"
]

SKIP_KEYWORDS = [
    "login",
    "signin",
    "signup",
    "register",
    "search",
    "contact",
    "privacy",
    "terms",
    "cookies",
    "faq",
    "news",
    "events",
    "media",
    "press",
    "circular",
    "advertisement",
    "tender",
    "notice",
    "gallery"
]

REMOVE_PHRASES = [
    "Loading",
    "Previous",
    "Next",
    "Skip to main content",
    "Cookie",
    "Accept",
    "Reject",
    "View All",
    "Read More",
    "Follow us",
    "Share",
    "Facebook",
    "Twitter",
    "Instagram",
    "LinkedIn"
]
def load_sources():
    with open(SOURCES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed": []}


def save_checkpoint(checkpoint):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, indent=4)

def load_crawl_checkpoint(start_url):

    print("\n========== CHECKPOINT DEBUG ==========")
    print("Start URL:", repr(start_url))

    if not os.path.exists(CRAWL_CHECKPOINT_FILE):
        print("❌ Checkpoint file NOT found")
        return None

    print("✅ Checkpoint file found")

    with open(CRAWL_CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Checkpoint Website:", repr(data.get("website")))
    print("Visited URLs:", len(data.get("visited", [])))
    print("Queue Size:", len(data.get("queue", [])))
    print("Page Count:", data.get("page_count"))

    if data.get("website") == start_url:
        print("✅ CHECKPOINT MATCHED")
        print("=====================================\n")
        return data

    print("❌ CHECKPOINT NOT MATCHED")
    print("=====================================\n")

    return None


def save_crawl_checkpoint(start_url, visited, queue, page_count):

    checkpoint = {
        "website": start_url,
        "visited": visited,
        "queue": queue,
        "page_count": page_count
    }

    with open(CRAWL_CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, indent=4)

    print("Crawl checkpoint saved.")
def delete_crawl_checkpoint():

    if os.path.exists(CRAWL_CHECKPOINT_FILE):
        os.remove(CRAWL_CHECKPOINT_FILE)
def load_scraped_pages():

    if os.path.exists(SCRAPED_FILE):
        with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return []


def save_scraped_pages(data):

    with open(SCRAPED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)




def clean_soup(soup):

    remove_tags = [
        "script", "style", "nav", "footer", "header",
        "noscript", "iframe", "svg", "aside",
        "form", "button", "canvas", "video",
        "audio", "figure", "img", "picture",
        "source", "link", "meta"
    ]

    for tag in soup(remove_tags):
        tag.decompose()

    unwanted = [
        ".navbar", ".navigation", ".breadcrumb",
        ".breadcrumbs", ".sidebar",
        ".left-sidebar", ".right-sidebar",
        ".menu", ".top-menu", ".bottom-menu",
        ".footer", ".header",
        ".social-share", ".share",
        ".comments", ".cookie",
        ".popup", ".modal",
        ".advertisement", ".ads",
        ".related-posts", ".pagination"
    ]

    for selector in unwanted:
        for item in soup.select(selector):
            item.decompose()
def clean_text(text):

    for phrase in REMOVE_PHRASES:
        text = text.replace(phrase, " ")

    text = re.sub(r"\s+", " ", text)

    words = text.split()

    cleaned = []

    previous = None

    for word in words:

        if word != previous:
            cleaned.append(word)

        previous = word

    return " ".join(cleaned).strip()

def extract_pdf_text(pdf_bytes):
    """
    Extract text from PDF bytes using PyMuPDF.
    """

    try:

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        pages = []

        for page in doc:
            text = page.get_text()

            if text:
                pages.append(text)

        doc.close()

        return clean_text("\n".join(pages))

    except Exception as e:

        print("PDF Extraction Error:", e)

        return ""
    
def should_skip(url):

    url = url.lower()

    return any(keyword in url for keyword in SKIP_KEYWORDS)
def is_downloadable_file(url):
    """
    Return True if the file should be skipped.
    Relevant PDFs are NOT skipped.
    """

    url = url.lower()

    # -------- Smart PDF Handling --------
    if url.endswith(".pdf"):

        allow_keywords = [
            "scheme",
            "guideline",
            "guidelines",
            "manual",
            "handbook",
            "faq",
            "citizen",
            "service",
            "application",
            "eligibility",
            "document",
            "brochure"
        ]

        skip_keywords = [
            "tender",
            "annual-report",
            "budget",
            "audit",
            "recruitment",
            "vacancy",
            "gazette",
            "minutes",
            "newsletter",
            "proceedings"
        ]

        if any(word in url for word in skip_keywords):
            return True

        if any(word in url for word in allow_keywords):
            return False

        # Unknown PDF -> skip for now
        return True

    # -------- Other file types --------
    extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".zip",
        ".rar",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".mp4",
        ".mp3",
        ".avi",
        ".mov",
        ".wmv",
        ".apk",
        ".exe",
        ".msi",
        ".dmg",
        ".iso"
    ]

    return any(url.endswith(ext) for ext in extensions)
def is_relevant_url(url):
    """
    Decide whether a URL is worth crawling.
    """

    url = url.lower()

    if should_skip(url):
        return False

    parsed = urlparse(url)
    path = parsed.path.lower()
    # Skip URLs with query parameters
    if parsed.query:
        
        return False

    # Always crawl homepage
    if path in ("", "/"):
        return True

    skip_patterns = [
        "news",
        "event",
        "media",
        "press",
        "gallery",
        "advertisement",
        "circular",
        "notice",
        "tender",
        "archive",
        "updates",
        "latest",
        "/calendar/",
        "/explore-india/",
        "/travel-and-tourism",
        "/culinary-delights",
        "/facts-of-india",
        "/odop",
        "/directory/whos-who",
        "/directory/web-directory",
        "/directory/public-utilities",
        "/talk/",
        "/mann-ki-baat",
        "/campaign",
        "/contest",
        "/quiz",
        "/poll",
        "/photo",
        "/gallery",
        "/event",
        "/media",
        "/blog",
        "/podcast",
        "/video",
        "/webcast",
        "/art-culture",
        "/culture",
        "/task/",
        "/group/",
        "/discussion",
        "/discuss",
        "/reel",
        "/poster",
        "/painting",
        "/essay",
        "/home/talk",
"/home/do",
"/mygov-podcast",
"/group-issue",
"/mygov-survey",
"/read-mkb-more",
    ]

    for pattern in skip_patterns:
        if pattern in path:
            return False

    priority_keywords = [
        "scheme",
        "service",
        "benefit",
        "eligibility",
        "apply",
        "application",
        "register",
        "registration",
        "guideline",
        "document",
        "certificate",
        "faq",
        "how-to-apply",
        "farmer",
        "kisan",
        "health",
        "education",
        "scholarship",
        "employment",
        "pension",
        "insurance",
        "loan"
    ]

    if any(word in path for word in priority_keywords):
        return True

    depth = len([p for p in path.split("/") if p])

    if depth <= 3:
        return True

    return False

def extract_title(soup):
    """
    Extract page title.
    """

    h1 = soup.find("h1")

    if h1 and h1.get_text(strip=True):
        return h1.get_text(strip=True)

    if soup.title and soup.title.string:
        return soup.title.string.strip()

    return "Untitled"
def extract_main_content(soup):
    """
    Extract meaningful content from the webpage.
    """

    selectors = [
        "main",
        "article",
        "[role='main']",
        "#content",
        ".content",
        "#main-content",
        ".main-content",
        ".page-content",
        ".entry-content",
        ".scheme-details",
        ".service-content",
        ".container"
    ]

    longest = ""

    for selector in selectors:

        element = soup.select_one(selector)

        if element:

            text = element.get_text("\n", strip=True)

            if len(text) > len(longest):
                longest = text

    if len(longest) > 300:
        return longest

    paragraphs = []

    for tag in soup.find_all(["p", "li", "h2", "h3", "h4"]):

        txt = tag.get_text(" ", strip=True)

        if len(txt) > 30:
            paragraphs.append(txt)

    return "\n".join(paragraphs)

import re

def is_heading(line):
    """
    Detect whether a line is likely to be a section heading.
    """

    line = line.strip()

    if not line:
        return False

    # Too short or too long
    if len(line) < 3 or len(line) > 100:
        return False

    # Ends like a sentence -> probably not a heading
    if line.endswith("."):
        return False

    # Common section headings
    common = {
        "overview",
        "introduction",
        "benefits",
        "features",
        "eligibility",
        "documents required",
        "required documents",
        "application process",
        "how to apply",
        "procedure",
        "important dates",
        "fees",
        "faq",
        "faqs",
        "contact",
        "helpline"
    }

    if line.lower() in common:
        return True

    # Title Case (e.g. "Pradhan Mantri Vidyalakshmi Karyakram")
    words = line.split()

    if 2 <= len(words) <= 12:
        capitalized = sum(
            1 for w in words
            if w[:1].isupper()
        )

        if capitalized >= len(words) * 0.7:
            return True

    # ALL CAPS headings
    if line.isupper():
        return True

    return False


def extract_sections(text):
    """
    Split page into logical sections using detected headings.
    """

    sections = []

    current_heading = "General"
    current_content = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if is_heading(line):

            if current_content:

                sections.append({
                    "heading": current_heading,
                    "content": "\n".join(current_content)
                })

            current_heading = line
            current_content = []

        else:
            current_content.append(line)

    if current_content:
        sections.append({
            "heading": current_heading,
            "content": "\n".join(current_content)
        })

    return sections

def is_good_content(text):

    if not text:
        return False

    if len(text.split()) < 80:
        return False

    bad = [
        "copyright",
        "privacy",
        "cookie",
        "facebook",
        "twitter",
        "instagram"
    ]

    score = 0

    lower = text.lower()

    for word in bad:

        if word in lower:
            score += 1

    return score <= 2

def extract_metadata(title, url, text):
    """
    Extract metadata for better retrieval.
    """

    metadata = {
        "title": title,
        "url": url,
        "category": "General",
        "page_type": "Information",
        "keywords": [],
        "word_count": len(text.split())
    }

    text_lower = text.lower()

    category_keywords = {
        "Agriculture": ["kisan", "farmer", "agriculture", "crop"],
        "Healthcare": ["health", "hospital", "medical", "ayushman"],
        "Education": ["education", "student", "scholarship", "school", "college"],
        "Employment": ["job", "employment", "career", "skill"],
        "Pension": ["pension", "retirement"],
        "Identity": ["aadhaar", "pan", "passport", "voter"],
        "Finance": ["bank", "loan", "insurance", "financial"]
    }

    for category, words in category_keywords.items():
        if any(word in text_lower for word in words):
            metadata["category"] = category
            break

    if "eligibility" in text_lower:
        metadata["page_type"] = "Eligibility"

    elif "benefit" in text_lower:
        metadata["page_type"] = "Benefits"

    elif "application" in text_lower:
        metadata["page_type"] = "Application"

    elif "document" in text_lower:
        metadata["page_type"] = "Documents"

    elif "faq" in text_lower:
        metadata["page_type"] = "FAQ"

    keywords = []

    for word in IMPORTANT_KEYWORDS:
        if word in text_lower:
            keywords.append(word)

    metadata["keywords"] = sorted(set(keywords))

    return metadata
def calculate_quality_score(text):

    score = 0

    words = len(text.split())

    if words > 150:
        score += 2

    elif words > 80:
        score += 1

    headings = [
        "eligibility",
        "benefit",
        "application",
        "document",
        "faq"
    ]

    lower = text.lower()

    for heading in headings:

        if heading in lower:
            score += 1

    return score

def should_save_page(text, metadata):

    if not text:
        return False

    if metadata["quality_score"] < 1:
        return False

    if len(text.split()) < 60:
        return False

    bad_words = [
        "login",
        "sign in",
        "privacy policy",
        "cookie policy"
    ]

    lower = text.lower()

    for word in bad_words:

        if word in lower:
            return False

    return True

def crawl_website(start_url):
    """
    Crawl one website with page-level checkpoint support.
    """

    checkpoint = load_crawl_checkpoint(start_url)

    if checkpoint:

        print(f"\nResuming crawl: {start_url}")

        visited = set(checkpoint["visited"])
        queue = deque(checkpoint["queue"])
        page_count = checkpoint["page_count"]

    else:

        visited = set()
        queue = deque([start_url])
        page_count = 0

    base_domain = urlparse(start_url).netloc
    scraped_pages = []

    try:

        while queue and page_count < MAX_PAGES:

            current_url = queue.popleft()

            if current_url in visited:
                continue

            if should_skip(current_url):
                continue

            

            print(f"\nScraping : {current_url}")

            try:

                response = session.get(current_url, timeout=20)
                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "").lower()

                # ---------------- PDF ----------------
                if "application/pdf" in content_type:

                    print("Reading PDF...")

                    text = extract_pdf_text(response.content)

                    if len(text.split()) < 60:
                        continue

                    metadata = extract_metadata(
                        current_url.split("/")[-1],
                        current_url,
                        text
                    )

                    metadata["quality_score"] = calculate_quality_score(text)

                    if should_save_page(text, metadata):

                        sections = extract_sections(text)
                        visited.add(current_url)

                        if not sections:

                            scraped_pages.append({
                                **metadata,
                                "content": text
                            })
                            visited.add(current_url)

                        else:

                            for section in sections:

                                scraped_pages.append({
                                    **metadata,
                                    "section_name": section["heading"],
                                    "content": section["content"]
                                })
                            visited.add(current_url)

                        page_count += 1

                    continue

                # ---------------- HTML ----------------
                if "text/html" not in content_type:
                    print(f"Skipping non-HTML content: {current_url}")
                    continue

                soup = BeautifulSoup(response.text, "lxml")

                clean_soup(soup)

                title = extract_title(soup)

                text = extract_main_content(soup)

                text = clean_text(text)

                metadata = extract_metadata(
                    title,
                    current_url,
                    text
                )

                metadata["quality_score"] = calculate_quality_score(text)

                if not should_save_page(text, metadata):
                    continue

                print(f"Title : {title}")
                print(f"URL   : {current_url}")

                print("\nPreview:")
                print(text[:300])

                print("\n" + "-" * 80)

                sections = extract_sections(text)

                if not sections:

                    scraped_pages.append({
                        **metadata,
                        "content": text
                    })

                else:

                    for section in sections:

                        scraped_pages.append({
                            **metadata,
                            "section_name": section["heading"],
                            "content": section["content"]
                        })

                page_count += 1

                for link in soup.find_all("a", href=True):

                    href = link["href"]

                    absolute_url = urljoin(current_url, href)

                    parsed = urlparse(absolute_url)

                    absolute_url = parsed._replace(
                        fragment=""
                    ).geturl()

                    if parsed.netloc == base_domain:

                        if (
                            absolute_url not in visited
                            and absolute_url not in queue
                            and not is_downloadable_file(absolute_url)
                            and is_relevant_url(absolute_url)
                        ):
                            queue.append(absolute_url)

                # Save checkpoint after every successful page
                save_crawl_checkpoint(
                    start_url,
                    list(visited),
                    list(queue),
                    page_count
                )

            except requests.exceptions.RequestException as e:

                print(f"Request failed: {current_url}")
                print(e)

                failed_urls.append({
                    "url": current_url,
                    "error": str(e)
                })

            except Exception as e:

                print(f"Unexpected error: {current_url}")
                print(e)

                failed_urls.append({
                    "url": current_url,
                    "error": str(e)
                })

    except KeyboardInterrupt:

        print("\nInterrupted during crawl.")
        print("Saving crawl checkpoint...")

        save_crawl_checkpoint(
            start_url,
            list(visited),
            list(queue),
            page_count
        )

        print("Checkpoint saved successfully.")

        raise

    # Website finished successfully
    delete_crawl_checkpoint()

    return scraped_pages
if __name__ == "__main__":

    sources = load_sources()

    checkpoint = load_checkpoint()

    completed = set(checkpoint["completed"])

    all_pages = load_scraped_pages()

    def crawl_sources(data, path=""):

        if isinstance(data, dict):

            for key, value in data.items():

                new_path = f"{path} > {key}" if path else key

                crawl_sources(value, new_path)

        elif isinstance(data, list):

            print("\n" + "=" * 80)
            print(f"CATEGORY : {path}")
            print("=" * 80)

            for website in data:

                if website in completed:

                    print(f"Skipping : {website}")

                    continue

                print(f"\nStarting : {website}")

                pages = crawl_website(website)

                if pages:

                    existing = {
                        (item["url"], item.get("section_name", ""))
                        for item in all_pages
                    }

                    for page in pages:

                        key = (
                            page["url"],
                            page.get("section_name", "")
                        )

                        if key not in existing:

                            all_pages.append(page)
                            existing.add(key)

                    save_scraped_pages(all_pages)

                    save_failed_urls()

                    completed.add(website)

                    checkpoint["completed"] = list(completed)

                    save_checkpoint(checkpoint)

                    print(f"Completed : {website}")

                else:

                    print(f"No pages scraped from {website}. It will be retried next time.")

    try:

        crawl_sources(sources)

    except KeyboardInterrupt:

        print("\nInterrupted by user... Saving progress.")

        # Save the current website state if it exists
        

        save_scraped_pages(all_pages)
        save_failed_urls()

        checkpoint["completed"] = list(completed)
        save_checkpoint(checkpoint)

        print("Progress saved successfully.")

        exit()
    save_scraped_pages(all_pages)

    save_failed_urls()

    print("\n" + "=" * 80)
    print("SCRAPING COMPLETED")
    print(f"Total Pages : {len(all_pages)}")
    print(f"Failed URLs : {len(failed_urls)}")
    print("=" * 80)
