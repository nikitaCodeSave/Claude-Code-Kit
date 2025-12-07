"""web2md core module.

Main pipeline orchestration: fetch -> extract -> convert -> save.
"""

from pathlib import Path

from web2md.fetcher import fetch_page
from web2md.extractor import extract_content
from web2md.converter import format_document


def url_to_markdown(
    url: str,
    output_path: str | Path | None = None,
    timeout: int = 30,
    include_metadata: bool = False,
) -> str:
    """Convert a web page URL to Markdown.

    Args:
        url: The URL to convert.
        output_path: Optional file path to save the markdown.
        timeout: Request timeout in seconds (default 30).
        include_metadata: Whether to include YAML frontmatter.

    Returns:
        The markdown content as a string.

    Raises:
        FetchError: If the URL cannot be fetched.
        ExtractionError: If content extraction fails.
        ConversionError: If HTML to Markdown conversion fails.
    """
    # Fetch the page
    html = fetch_page(url, timeout=timeout)

    # Extract content
    content = extract_content(html, url)

    # Format as markdown
    markdown = format_document(content, include_metadata=include_metadata)

    # Save to file if path provided
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")

    return markdown
