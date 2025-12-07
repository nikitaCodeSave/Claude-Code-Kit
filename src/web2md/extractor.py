"""web2md extractor module.

Multi-extractor strategy using trafilatura (primary) and readability (fallback).
"""

from dataclasses import dataclass

from bs4 import BeautifulSoup
import trafilatura
from readability import Document  # type: ignore[import-untyped]

from web2md.exceptions import ExtractionError

MIN_CONTENT_LENGTH = 3  # Minimum text length for final validation
MIN_TRAFILATURA_LENGTH = 100  # Minimum for trafilatura to consider it successful


@dataclass
class ExtractedContent:
    """Extracted content from a web page.

    Attributes:
        title: The article title.
        content: The main content as HTML.
        author: The article author (if available).
        date: The publication date (if available).
        source_url: The source URL.
    """

    title: str
    content: str
    author: str | None
    date: str | None
    source_url: str | None


def preprocess_html(html: str) -> str:
    """Preprocess HTML by removing non-content elements.

    Removes script, style, nav, footer, header, aside tags.

    Args:
        html: Raw HTML string.

    Returns:
        Cleaned HTML string.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove unwanted tags
    for tag_name in ["script", "style", "nav", "footer", "header", "aside", "noscript"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    return str(soup)


def extract_with_trafilatura(html: str, url: str | None = None) -> ExtractedContent | None:
    """Extract content using trafilatura.

    Args:
        html: HTML content to extract from.
        url: Source URL for metadata.

    Returns:
        ExtractedContent if successful, None if extraction fails or content too short.
    """
    # Extract main content
    content = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        output_format="html",
    )

    if not content or len(content.strip()) < MIN_TRAFILATURA_LENGTH:
        return None

    # Extract metadata
    metadata = trafilatura.extract_metadata(html)

    title = ""
    author = None
    date = None

    if metadata:
        title = metadata.title or ""
        author = metadata.author
        date = metadata.date

    # Fallback: extract title from HTML if not in metadata
    if not title:
        soup = BeautifulSoup(html, "lxml")
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        else:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True)

    return ExtractedContent(
        title=title,
        content=content,
        author=author,
        date=date,
        source_url=url,
    )


def extract_with_readability(html: str, url: str | None = None) -> ExtractedContent | None:
    """Extract content using readability-lxml.

    Args:
        html: HTML content to extract from.
        url: Source URL for metadata.

    Returns:
        ExtractedContent if successful, None if extraction fails or content too short.
    """
    try:
        doc = Document(html)
        content = doc.summary()
        title = doc.title()

        # Check if content is meaningful (has any text)
        soup = BeautifulSoup(content, "lxml")
        text_content = soup.get_text(strip=True)

        if not text_content:
            return None

        return ExtractedContent(
            title=title,
            content=content,
            author=None,  # Readability doesn't extract author
            date=None,  # Readability doesn't extract date
            source_url=url,
        )
    except Exception:
        return None


def extract_content(html: str, url: str | None = None) -> ExtractedContent:
    """Extract content using multi-extractor strategy.

    Tries trafilatura first, falls back to readability if trafilatura fails.

    Args:
        html: HTML content to extract from.
        url: Source URL for metadata.

    Returns:
        ExtractedContent with extracted title and content.

    Raises:
        ExtractionError: If both extractors fail or content is invalid.
    """
    # Preprocess HTML
    cleaned_html = preprocess_html(html)

    # Try trafilatura first (primary extractor)
    result = extract_with_trafilatura(cleaned_html, url)

    # Fallback to readability
    if result is None:
        result = extract_with_readability(cleaned_html, url)

    # Both failed
    if result is None:
        raise ExtractionError("Failed to extract content from page", url=url or "")

    # Validate content
    soup = BeautifulSoup(result.content, "lxml")
    text_content = soup.get_text(strip=True)

    if not text_content:
        raise ExtractionError("Extracted content is empty", url=url or "")

    if len(text_content) < MIN_CONTENT_LENGTH:
        raise ExtractionError(
            f"Extracted content too short ({len(text_content)} chars, min {MIN_CONTENT_LENGTH})",
            url=url or "",
        )

    # Ensure source_url is set
    if result.source_url is None:
        result = ExtractedContent(
            title=result.title,
            content=result.content,
            author=result.author,
            date=result.date,
            source_url=url,
        )

    return result
