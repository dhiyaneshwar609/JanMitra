import json
import os
import re
import time
import logging
from collections import deque
from urllib.parse import urljoin, urlparse
import traceback

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from playwright.sync_api import sync_playwright
from app.ingestion.state_manager import load_state, save_state


# ==========================================================
# CONFIGURATION
# ==========================================================

from app.core.config import SOURCES_FILE

OUTPUT_FILE = "scraped_data.json"
FAILED_FILE = "failed_urls.json"
CHECKPOINT_FILE = "checkpoint.json"
QUEUE_FILE = "crawl_checkpoint.json"

REQUEST_TIMEOUT = 15
MAX_RETRIES = 2
MAX_PAGES = 100
MAX_LINKS_PER_PAGE = 75

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0 Safari/537.36"
)

# Skip URLs containing these patterns
SKIP_PATTERNS = [
    "news",
    "event",
    "media",
    "press",
    "gallery",
    "advertisement",
    "circular",
    "tender",
    "recruitment",
    "career",
    "vacancy",
    "auction",
    "result",
    "report",
    "reports",
    "dbt",
    "dashboard",
    "statistics",
    "statistic",
    "graph",
    "chart",
    "captcha",
    "validate",
    "login",
    "logout",
    "signin",
    "register",
    "admin",
    "search",
    "print",
    "downloadreport",
    "detailreport",
    "feedback",
    "contact-us-old",
    "site-map",
    "webcast",
    "archive",
    "vetmis",
"login",
"signin",
"admin",
"dashboard",
"captcha",
]

# File extensions to ignore
SKIP_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".ico",
    ".zip",
    ".rar",
    ".mp4",
    ".mp3",
    ".apk",
".exe",
".msi",
".iso",
".dmg",
".bin",
".7z",
)

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ==========================================================
# REQUEST SESSION
# ==========================================================

retry_strategy = Retry(
    total=MAX_RETRIES,
    connect=MAX_RETRIES,
    read=MAX_RETRIES,
    backoff_factor=2,
    status_forcelist=[
        429,
        500,
        502,
        503,
        504
    ],
    allowed_methods=["HEAD", "GET"]
)

adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=20,
    pool_maxsize=20
)

session = requests.Session()

session.mount("http://", adapter)
session.mount("https://", adapter)

session.headers.update({
    "User-Agent": USER_AGENT
})

# ==========================================================
# GLOBAL VARIABLES
# ==========================================================

visited = set()

scraped_data = []

failed_urls = []

crawl_queue = deque()
# ==========================================================
# JSON UTILITIES
# ==========================================================

def load_json(file_path, default):
    """
    Safely load a JSON file.
    Returns the default value if the file doesn't exist
    or cannot be parsed.
    """
    if not os.path.exists(file_path):
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:

        traceback.print_exc()

        logger.warning(f"Could not load {file_path}: {e}")

        return default


def save_json(file_path, data):
    """
    Save JSON with pretty formatting.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )
    except Exception as e:
        logger.error(f"Failed to save {file_path}: {e}")


# ==========================================================
# CHECKPOINT MANAGEMENT
# ==========================================================

def save_checkpoint():
    """
    Save visited URLs.
    """
    save_json(
        CHECKPOINT_FILE,
        sorted(list(visited))
    )


def load_checkpoint():
    """
    Restore visited URLs.
    """
    global visited

    urls = load_json(CHECKPOINT_FILE, [])

    visited = set(urls)

    logger.info(f"Loaded {len(visited)} visited URLs.")

SOURCE_CHECKPOINT_FILE = "source_checkpoint.json"


def save_source_checkpoint(index):
    save_json(
        SOURCE_CHECKPOINT_FILE,
        {"current_source": index}
    )


def load_source_checkpoint():
    data = load_json(
        SOURCE_CHECKPOINT_FILE,
        {"current_source": 0}
    )
    return data.get("current_source", 0)


# ==========================================================
# FAILED URL MANAGEMENT
# ==========================================================

def save_failed_urls():
    """
    Remove duplicate failed URLs before saving.
    """
    unique = {}

    for item in failed_urls:
        url = item.get("url")

        if url:
            unique[url] = item

    save_json(
        FAILED_FILE,
        list(unique.values())
    )


def load_failed_urls():
    """
    Restore failed URLs.
    """
    global failed_urls

    failed_urls = load_json(
        FAILED_FILE,
        []
    )

    logger.info(
        f"Loaded {len(failed_urls)} failed URLs."
    )


# ==========================================================
# CRAWL QUEUE
# ==========================================================

def save_queue():
    """
    Save remaining crawl queue.
    """
    save_json(
        QUEUE_FILE,
        list(crawl_queue)
    )


def load_queue():
    """
    Restore crawl queue.
    """
    global crawl_queue

    queue = load_json(
        QUEUE_FILE,
        []
    )

    crawl_queue = deque(queue)

    logger.info(
        f"Loaded {len(crawl_queue)} queued URLs."
    )


# ==========================================================
# SCRAPED DATA
# ==========================================================

def load_scraped_data():
    """
    Load previously scraped pages.
    """
    global scraped_data

    scraped_data = load_json(
        OUTPUT_FILE,
        []
    )

    logger.info(
        f"Loaded {len(scraped_data)} existing pages."
    )


def save_scraped_data():
    """
    Save all scraped pages.
    """
    save_json(
        OUTPUT_FILE,
        scraped_data
    )


# ==========================================================
# NETWORK REQUEST
# ==========================================================

def fetch_url(url):
    """
    Fetch URL with retry logic and SSL fallback.
    """

    last_error = None

    for attempt in range(MAX_RETRIES):

        try:

            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT,
                verify=True
            )

            response.raise_for_status()

            return response

        except requests.exceptions.SSLError:

            logger.warning(f"SSL failed for {url}, retrying without verification.")

            try:

                response = session.get(
                    url,
                    timeout=REQUEST_TIMEOUT,
                    verify=False
                )

                response.raise_for_status()

                return response

            except Exception as e:
                last_error = e

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout
        ) as e:

            last_error = e

        except Exception as e:

            last_error = e

        wait = 2 ** attempt

        logger.warning(
            f"Retry {attempt + 1}/{MAX_RETRIES} "
            f"for {url} after {wait}s"
        )

        time.sleep(wait)

    raise last_error
# ==========================================================
# URL UTILITIES
# ==========================================================

def normalize_url(url):
    """
    Normalize URLs by removing fragments and trailing slashes.
    """
    if not url:
        return None

    url = url.split("#")[0].strip()

    if url.endswith("/"):
        url = url[:-1]

    return url


def is_pdf(url):
    """
    Check whether a URL points to a PDF.
    """
    return url.lower().endswith(".pdf")


def is_valid_url(url, base_domain):
    """
    Returns True only for useful crawlable URLs.
    """

    if not url:
        return False

    url = normalize_url(url)

    parsed = urlparse(url)

    # Only HTTP / HTTPS
    if parsed.scheme not in ("http", "https"):
        return False

    # Stay inside same domain
    if parsed.netloc != base_domain:
        return False

    lower = url.lower()

    # Skip fragments
    if "#" in url:
        return False

    # Skip mail, phone and javascript links
    if lower.startswith(("mailto:", "tel:", "javascript:")):
        return False

    # Skip unwanted file types
    for ext in SKIP_EXTENSIONS:
        if lower.endswith(ext):
            return False

    # Skip unwanted paths
    for pattern in SKIP_PATTERNS:
        if pattern in lower:
            return False

    # Skip URLs with excessive query parameters
    if len(parsed.query) > 100:
        return False

    return True


# ==========================================================
# TEXT CLEANING
# ==========================================================

def clean_text(text):
    """
    Remove unnecessary whitespace and control characters.
    """

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"\n+", "\n", text)

    text = re.sub(r"\t+", " ", text)

    return text.strip()


# ==========================================================
# PAGE METADATA
# ==========================================================

def extract_metadata(soup, url):
    """
    Extract useful metadata from an HTML page.
    """

    title = ""

    if soup.title:
        title = soup.title.get_text(strip=True)

    description = ""

    desc = soup.find("meta", attrs={"name": "description"})

    if desc:
        description = desc.get("content", "").strip()

    keywords = ""

    key = soup.find("meta", attrs={"name": "keywords"})

    if key:
        keywords = key.get("content", "").strip()

    language = soup.html.get("lang", "") if soup.html else ""

    return {
        "url": url,
        "title": title,
        "description": description,
        "keywords": keywords,
        "language": language
    }


# ==========================================================
# LINK EXTRACTION
# ==========================================================

def extract_links(soup, current_url):
    
    """
    Extract only useful internal links.
    Skip reports, admin pages, duplicate pages and static files.
    """

    links = set()

    base_domain = urlparse(current_url).netloc

    # URLs containing these keywords are not useful for RAG
    skip_keywords = [
        "report",
        "reports",
        "dbt",
        "validate",
        "captcha",
        "login",
        "logout",
        "signin",
        "register",
        "search",
        "print",
        "downloadreport",
        "detailreport",
        "export",
        "statistics",
        "stats",
        "graph",
        "chart",
        "dashboard",
        "admin",
        "upload",
        "attachment"
    ]

    # File types to skip
    skip_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".svg",
        ".zip",
        ".rar",
        ".mp4",
        ".mp3",
        ".xls",
        ".xlsx",
        ".csv"
    )

    for tag in soup.find_all("a", href=True):

        href = tag["href"].strip()

        absolute = urljoin(current_url, href)

        absolute = normalize_url(absolute)

        if not absolute:
            continue

        if not is_valid_url(absolute, base_domain):
            continue

        lower = absolute.lower()

        if any(word in lower for word in skip_keywords):
            continue

        if lower.endswith(skip_extensions):
            continue

        links.add(absolute)

    return sorted(links)[:MAX_LINKS_PER_PAGE]

# ==========================================================
# HTML CONTENT EXTRACTION
# ==========================================================

def extract_html_content(response, url):
    """
    Extract clean content from an HTML page.
    Returns a structured dictionary suitable for RAG.
    """

    soup = BeautifulSoup(response.text, "html.parser")

    # ------------------------------------------------------
    # Remove unwanted elements
    # ------------------------------------------------------

    remove_tags = [
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "iframe",
        "header",
        "footer",
        "nav",
        "aside",
        "form"
    ]

    for tag in remove_tags:
        for element in soup.find_all(tag):
            element.decompose()

    # ------------------------------------------------------
    # Remove common unwanted classes / ids
    # ------------------------------------------------------

    unwanted_keywords = [
        "navbar",
        "breadcrumb",
        "footer",
        "header",
        "sidebar",
        "menu",
        "pagination",
        "social",
        "share",
        "advertisement",
        "ads"
    ]

    for tag in soup.find_all(True):

        classes = " ".join(tag.get("class", []))
        element_id = tag.get("id", "")

        combined = f"{classes} {element_id}".lower()

        if any(word in combined for word in unwanted_keywords):
            tag.decompose()

    # ------------------------------------------------------
    # Metadata
    # ------------------------------------------------------

    metadata = extract_metadata(soup, url)

    # ------------------------------------------------------
    # Prefer <main>
    # ------------------------------------------------------

    main = soup.find("main")

    if not main:
        main = soup.find("article")

    if not main:
        main = soup.find("body")

    if not main:
        main = soup

    # ------------------------------------------------------
    # Structured Sections
    # ------------------------------------------------------

    sections = []

    current_heading = "Introduction"
    current_text = []

    for element in main.find_all([
        "h1",
        "h2",
        "h3",
        "h4",
        "p",
        "li"
    ]):

        if element.name.startswith("h"):

            if current_text:

                sections.append({
                    "heading": current_heading,
                    "content": clean_text(
                        "\n".join(current_text)
                    )
                })

            current_heading = clean_text(
                element.get_text(" ", strip=True)
            )

            current_text = []

        else:

            text = clean_text(
                element.get_text(" ", strip=True)
            )

            if len(text) > 5:
                current_text.append(text)

    if current_text:

        sections.append({
            "heading": current_heading,
            "content": clean_text(
                "\n".join(current_text)
            )
        })

    # ------------------------------------------------------
    # Tables
    # ------------------------------------------------------

    tables = []

    for table in main.find_all("table"):

        rows = []

        for tr in table.find_all("tr"):

            cols = [
                clean_text(td.get_text(" ", strip=True))
                for td in tr.find_all(["th", "td"])
            ]

            if cols:
                rows.append(cols)

        if rows:
            tables.append(rows)

    # ------------------------------------------------------
    # Complete Text
    # ------------------------------------------------------

    full_text = clean_text(
        main.get_text("\n", strip=True)
    )

    return {
        "url": url,
        "title": metadata["title"],
        "description": metadata["description"],
        "keywords": metadata["keywords"],
        "language": metadata["language"],
        "content": full_text,
        "sections": sections,
        "tables": tables,
        "content_type": "html"
    }
# ==========================================================
# PDF CONTENT EXTRACTION
# ==========================================================

def extract_pdf_content(url):
    """
    Download and extract text from a PDF.
    Returns a structured dictionary similar to HTML extraction.
    """

    response = fetch_url(url)

    document = fitz.open(stream=response.content, filetype="pdf")

    metadata = document.metadata or {}

    pages = []
    full_text = []

    for page_number in range(len(document)):

        page = document.load_page(page_number)

        text = page.get_text("text")

        text = clean_text(text)

        if text:

            pages.append({
                "page": page_number + 1,
                "content": text
            })

            full_text.append(text)

    content = "\n\n".join(full_text)

    if not content.strip():

        logger.warning(
            f"Scanned PDF detected (no extractable text): {url}"
        )

    result = {
        "url": url,
        "title": metadata.get("title", ""),
        "author": metadata.get("author", ""),
        "subject": metadata.get("subject", ""),
        "keywords": metadata.get("keywords", ""),
        "creator": metadata.get("creator", ""),
        "producer": metadata.get("producer", ""),
        "page_count": len(document),
        "content": content,
        "pages": pages,
        "content_type": "pdf"
    }

    document.close()

    return result
# ==========================================================
# DOCUMENT PROCESSOR
# ==========================================================

def process_document(url):
    """
    Process either an HTML page or a PDF.
    """

    try:

        if is_pdf(url):

            logger.info(f"PDF : {url}")

            return extract_pdf_content(url)

        response = fetch_url(url)

        content_type = response.headers.get(
            "Content-Type",
            ""
        ).lower()

        if "pdf" in content_type:

            logger.info(f"PDF : {url}")

            return extract_pdf_content(url)

        logger.info(f"HTML : {url}")

        html_result = extract_html_content(
            response,
            url
        )

        # If almost no content was extracted,
        # try Playwright.

        if len(html_result["content"]) < 300:

            logger.info(
                f"Trying Playwright for {url}"
            )

            dynamic = extract_dynamic_html(url)

            if dynamic and len(dynamic["content"]) > len(html_result["content"]):
                return dynamic

        return html_result

    except Exception as e:

        logger.error(f"{url} : {e}")

        failed_urls.append({
            "url": url,
            "reason": str(e)
        })

        return None

# ==========================================================
# PLAYWRIGHT FALLBACK
# ==========================================================

def fetch_dynamic_page(url):
    """
    Render JavaScript-heavy pages using Playwright.
    Returns page HTML or None on failure.
    """

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            page = browser.new_page(
                user_agent=USER_AGENT
            )

            page.goto(
                url,
                wait_until="networkidle",
                timeout=60000
            )

            html = page.content()

            browser.close()

            return html

    except Exception as e:

        logger.error(
            f"Playwright failed for {url}: {e}"
        )

        return None

def extract_dynamic_html(url):
    """
    Extract content from a dynamically rendered page.
    """

    html = fetch_dynamic_page(url)

    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Remove unwanted tags

    for tag in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "header",
        "footer",
        "nav",
        "aside",
        "form"
    ]):
        tag.decompose()

    metadata = extract_metadata(
        soup,
        url
    )

    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find("body")
        or soup
    )

    text = clean_text(
        main.get_text(
            "\n",
            strip=True
        )
    )

    sections = []

    current_heading = "Introduction"
    current_content = []

    for element in main.find_all(
        ["h1", "h2", "h3", "h4", "p", "li"]
    ):

        if element.name.startswith("h"):

            if current_content:

                sections.append({
                    "heading": current_heading,
                    "content": clean_text(
                        "\n".join(current_content)
                    )
                })

            current_heading = clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            current_content = []

        else:

            txt = clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if txt:
                current_content.append(txt)

    if current_content:

        sections.append({
            "heading": current_heading,
            "content": clean_text(
                "\n".join(current_content)
            )
        })

    return {
        "url": url,
        "title": metadata["title"],
        "description": metadata["description"],
        "keywords": metadata["keywords"],
        "language": metadata["language"],
        "content": text,
        "sections": sections,
        "tables": [],
        "content_type": "dynamic_html"
    }

# ==========================================================
# CRAWLER ENGINE
# ==========================================================

# ==========================================================
# DUPLICATE DETECTION
# ==========================================================

def already_scraped(url):
    """
    Check whether a URL already exists in scraped_data.
    """

    for item in scraped_data:
        if item.get("url") == url:
            return True

    return False

def crawl_website(start_url):
    """
    Breadth-first crawler with checkpoint and resume support.
    """

    global crawl_queue

    load_checkpoint()
    load_scraped_data()
    load_failed_urls()

    # Fresh queue for this website
    load_queue()

    if not crawl_queue:
        crawl_queue.append(start_url)

    base_domain = urlparse(start_url).netloc

    pages_crawled = 0

    while crawl_queue:

        if pages_crawled >= MAX_PAGES:
            logger.info("Reached MAX_PAGES limit.")
            break

        current_url = normalize_url(crawl_queue.popleft())

        if not current_url:
            continue

        if current_url in visited:
            continue

        if already_scraped(current_url):
            visited.add(current_url)
            continue

        logger.info(f"Crawling : {current_url}")

        # --------------------------------------------
        # Extract content
        # --------------------------------------------

        result = process_document(current_url)

        if result is None:

            logger.warning(f"Failed : {current_url}")

            save_queue()
            save_checkpoint()
            save_failed_urls()

            continue

        # --------------------------------------------
        # Save result
        # --------------------------------------------

        scraped_data.append(result)

        visited.add(current_url)

        pages_crawled += 1

        logger.info(
            f"Saved ({pages_crawled}) : {current_url}"
        )

        # --------------------------------------------
        # Discover more links (HTML only)
        # --------------------------------------------

        if result["content_type"] != "pdf":

            try:

                response = fetch_url(current_url)

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                links = extract_links(
                    soup,
                    current_url
                )

                for link in links:

                    if not link:
                        continue

                    if link in visited:
                        continue

                    if already_scraped(link):
                        continue

                    if link in crawl_queue:
                        continue

                    crawl_queue.append(link)

            except Exception as e:

                logger.warning(
                    f"Link extraction failed: {e}"
                )

        # --------------------------------------------
        # Save progress every page
        # --------------------------------------------

        save_scraped_data()
        save_checkpoint()
        save_queue()
        save_failed_urls()

        logger.info(
            f"Queue : {len(crawl_queue)} | "
            f"Visited : {len(visited)}"
        )

    # Clear queue only after successful completion
    crawl_queue.clear()
    save_queue()

    logger.info("Crawling completed.")

# ==========================================================
# SOURCE LOADER
# ==========================================================

def load_sources():
    """
    Load every URL from a nested JSON structure.
    """

    if not os.path.exists(SOURCES_FILE):
        raise FileNotFoundError(f"{SOURCES_FILE} not found.")

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    urls = set()

    def extract(obj):

        if isinstance(obj, str):

            if obj.startswith("http"):
                urls.add(obj)

        elif isinstance(obj, list):

            for item in obj:
                extract(item)

        elif isinstance(obj, dict):

            for value in obj.values():
                extract(value)

    extract(data)

    logger.info(f"Loaded {len(urls)} websites.")

    return sorted(urls)


# ==========================================================
# SUMMARY
# ==========================================================

def print_summary():

    logger.info("=" * 60)
    logger.info("CRAWL SUMMARY")
    logger.info("=" * 60)

    logger.info(
        f"Pages scraped : {len(scraped_data)}"
    )

    logger.info(
        f"Visited URLs  : {len(visited)}"
    )

    logger.info(
        f"Failed URLs   : {len(failed_urls)}"
    )

    logger.info(
        f"Remaining Queue : {len(crawl_queue)}"
    )

    logger.info("=" * 60)


# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info("=" * 60)
    logger.info("Government Website Scraper V2")
    logger.info("=" * 60)

    try:

        sources = load_sources()

    except Exception as e:

        logger.error(e)

        return

    logger.info(
        f"Loaded {len(sources)} source websites."
    )

    state = load_state()

    start_index = state["current_source"]

    for index in range(start_index, len(sources)):

        source = sources[index]

        logger.info(
            f"\n[{index + 1}/{len(sources)}] {source}"
        )

        # Save current source before crawling
        state["current_source"] = index
        save_state(state)

        try:

            crawl_website(source)

            # If completed successfully, move to next source
            state["current_source"] = index + 1
            save_state(state)

        except KeyboardInterrupt:

            logger.warning(
                "Interrupted by user."
            )

            save_scraped_data()
            save_checkpoint()
            save_queue()
            save_failed_urls()

            break

        except Exception as e:

            logger.error(
                f"Source failed : {e}"
            )

            continue

    save_scraped_data()
    save_checkpoint()
    save_queue()
    save_failed_urls()

    print_summary()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()