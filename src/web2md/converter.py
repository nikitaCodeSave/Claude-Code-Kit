"""web2md converter module.

Converts HTML to Markdown and formats documents with optional metadata.
"""

from datetime import datetime, timezone

import markdownify

from web2md.extractor import ExtractedContent


def html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown.

    Args:
        html: HTML content to convert.

    Returns:
        Markdown string.
    """
    markdown = markdownify.markdownify(
        html,
        heading_style="ATX",
        bullets="-",
        code_language="",
    )

    # Clean up extra whitespace
    lines = markdown.split("\n")
    cleaned_lines = []
    prev_empty = False

    for line in lines:
        stripped = line.rstrip()
        is_empty = not stripped

        # Skip consecutive empty lines
        if is_empty and prev_empty:
            continue

        cleaned_lines.append(stripped)
        prev_empty = is_empty

    result = "\n".join(cleaned_lines).strip()
    return result


def format_document(content: ExtractedContent, include_metadata: bool = False) -> str:
    """Format extracted content as a Markdown document.

    Args:
        content: ExtractedContent with title and content.
        include_metadata: Whether to include YAML frontmatter.

    Returns:
        Formatted Markdown document.
    """
    parts = []

    # YAML frontmatter
    if include_metadata:
        frontmatter_lines = ["---"]
        frontmatter_lines.append(f'title: "{content.title}"')

        if content.author:
            frontmatter_lines.append(f'author: "{content.author}"')

        if content.date:
            frontmatter_lines.append(f'date: "{content.date}"')

        if content.source_url:
            frontmatter_lines.append(f'source: "{content.source_url}"')

        # Add extraction timestamp
        extracted_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        frontmatter_lines.append(f'extracted_at: "{extracted_at}"')

        frontmatter_lines.append("---")
        parts.append("\n".join(frontmatter_lines))

    # Title
    parts.append(f"# {content.title}")

    # Convert content to markdown
    if content.content:
        markdown_content = html_to_markdown(content.content)
        if markdown_content:
            parts.append(markdown_content)

    return "\n\n".join(parts)
