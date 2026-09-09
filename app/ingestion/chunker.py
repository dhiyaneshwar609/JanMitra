from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from app.ingestion.document_classifier import classify_document

def split_into_sections(text):
    """
    Split a document into sections using headings.
    """

    pattern = (
    r"\n(?=("
    r"[A-Z][A-Za-z0-9 ,&()'/-]{5,100}"
    r"|Pradhan Mantri.*"
    r"|PM .*"
    r"|Chief Minister.*"
    r"|Mukhya Mantri.*"
    r"|Objectives?"
    r"|Benefits?"
    r"|Eligibility"
    r"|Documents?"
    r"|How to Apply"
    r"|Application Process"
    r"))"
)

    sections = re.split(pattern, text)
    merged_sections = []

    buffer = ""

    for section in sections:

        if len(section.split()) < 40:
            buffer += "\n" + section
        else:
            if buffer:
                merged_sections.append(buffer.strip())
                buffer = ""
            merged_sections.append(section)

    if buffer:
        merged_sections.append(buffer.strip())

    sections = merged_sections

    return [s.strip() for s in sections if s.strip()]


def split_documents(documents):
    """
    Split documents into semantic chunks while preserving metadata.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=[
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            "; ",
            ", ",
            " "
        ]
    )

    chunks = []

    for doc in documents:

        sections = split_into_sections(doc.page_content)

        split_docs = []

        for section in sections:

            docs = splitter.create_documents(
                [section],
                metadatas=[doc.metadata]
            )

            split_docs.extend(docs)

        for i, chunk in enumerate(split_docs):

            text = chunk.page_content.strip()

            # Ignore very small chunks
            if len(text.split()) < 30:
                continue

            metadata = dict(chunk.metadata)

            metadata["document_type"] = classify_document(
                metadata.get("title", ""),
                metadata.get("url", "")
            )

            metadata["chunk_id"] = i
            metadata["chunk_length"] = len(text.split())

            if "section_name" not in metadata:
                metadata["section_name"] = "General"

            chunk.metadata = metadata
            chunks.append(chunk)

    return chunks