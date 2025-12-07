"""web2md - Convert web pages to Markdown.

A Python CLI utility for downloading web pages, extracting main content
(without navigation, ads, footers), and converting to clean Markdown.
"""

from web2md.core import url_to_markdown
from web2md.exceptions import (
    Web2MdError,
    FetchError,
    ExtractionError,
    ConversionError,
)
from web2md.extractor import ExtractedContent

__version__ = "0.1.0"

__all__ = [
    "url_to_markdown",
    "Web2MdError",
    "FetchError",
    "ExtractionError",
    "ConversionError",
    "ExtractedContent",
]
