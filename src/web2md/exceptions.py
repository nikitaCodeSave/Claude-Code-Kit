"""web2md exceptions module.

Custom exceptions for web2md with meaningful attributes.
"""


class Web2MdError(Exception):
    """Base exception for all web2md errors."""

    pass


class FetchError(Web2MdError):
    """Raised when fetching a web page fails.

    Attributes:
        url: The URL that failed to fetch.
        status_code: HTTP status code if available.
    """

    def __init__(self, message: str, url: str = "", status_code: int | None = None):
        super().__init__(message)
        self.url = url
        self.status_code = status_code


class ExtractionError(Web2MdError):
    """Raised when content extraction fails.

    Attributes:
        url: The source URL.
    """

    def __init__(self, message: str, url: str = ""):
        super().__init__(message)
        self.url = url


class ConversionError(Web2MdError):
    """Raised when HTML to Markdown conversion fails."""

    pass
