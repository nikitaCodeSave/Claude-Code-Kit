"""web2md fetcher module.

Fetches web pages with retry logic and proper error handling.
"""

import time
from urllib.parse import urlparse

import httpx

from web2md.exceptions import FetchError

DEFAULT_USER_AGENT = "web2md/0.1.0"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 2
RETRY_DELAY = 1


def fetch_page(url: str, timeout: int = DEFAULT_TIMEOUT, user_agent: str | None = None) -> str:
    """Fetch a web page and return its HTML content.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds (default 30).
        user_agent: Custom User-Agent header (default "web2md/0.1.0").

    Returns:
        The HTML content as a string.

    Raises:
        FetchError: If the URL is invalid, connection fails, or HTTP error occurs.
    """
    # Validate URL
    if not url:
        raise FetchError("URL cannot be empty", url=url)

    parsed = urlparse(url)
    if not parsed.scheme:
        raise FetchError("URL must include scheme (http:// or https://)", url=url)
    if parsed.scheme not in ("http", "https"):
        raise FetchError(f"Invalid URL scheme: {parsed.scheme}", url=url)
    if not parsed.netloc:
        raise FetchError("Invalid URL format", url=url)

    # Set headers
    headers = {
        "User-Agent": user_agent if user_agent else DEFAULT_USER_AGENT,
    }

    # Retry loop
    last_exception: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url, headers=headers)

                # Check for HTTP errors
                if response.status_code >= 400:
                    raise FetchError(
                        f"HTTP {response.status_code} error",
                        url=url,
                        status_code=response.status_code,
                    )

                return response.text

        except FetchError:
            # Re-raise FetchError directly (HTTP errors)
            raise
        except httpx.TimeoutException as e:
            raise FetchError(f"Request timeout: {e}", url=url)
        except httpx.ConnectError as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise FetchError(f"Connection failed after {MAX_RETRIES} attempts: {e}", url=url)
        except httpx.HTTPError as e:
            raise FetchError(f"HTTP error: {e}", url=url)

    # Should not reach here, but just in case
    raise FetchError(f"Failed to fetch URL: {last_exception}", url=url)
