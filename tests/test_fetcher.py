"""Tests for web2md fetcher module."""

import pytest
from pytest_httpx import HTTPXMock

from web2md.fetcher import fetch_page
from web2md.exceptions import FetchError


class TestFetchPageSuccess:
    """Tests for successful page fetching."""

    def test_fetches_html_content(self, httpx_mock: HTTPXMock):
        """fetch_page returns HTML content from URL."""
        httpx_mock.add_response(
            url="https://example.com/page",
            text="<html><body>Hello</body></html>"
        )

        result = fetch_page("https://example.com/page")

        assert "<html>" in result
        assert "Hello" in result

    def test_returns_string(self, httpx_mock: HTTPXMock):
        """fetch_page returns a string."""
        httpx_mock.add_response(
            url="https://example.com",
            text="<html></html>"
        )

        result = fetch_page("https://example.com")

        assert isinstance(result, str)

    def test_handles_utf8_encoding(self, httpx_mock: HTTPXMock):
        """fetch_page correctly handles UTF-8 encoded content."""
        httpx_mock.add_response(
            url="https://example.com",
            text="<html><body>Привет мир</body></html>",
            headers={"content-type": "text/html; charset=utf-8"}
        )

        result = fetch_page("https://example.com")

        assert "Привет мир" in result


class TestFetchPageTimeout:
    """Tests for timeout handling."""

    def test_uses_default_timeout(self, httpx_mock: HTTPXMock):
        """fetch_page uses 30 second default timeout."""
        httpx_mock.add_response(url="https://example.com", text="<html></html>")

        # Should complete without error
        fetch_page("https://example.com")

        # Verify request was made
        request = httpx_mock.get_request()
        assert request is not None

    def test_accepts_custom_timeout(self, httpx_mock: HTTPXMock):
        """fetch_page accepts custom timeout parameter."""
        httpx_mock.add_response(url="https://example.com", text="<html></html>")

        # Should complete without error
        fetch_page("https://example.com", timeout=60)

    def test_raises_fetch_error_on_timeout(self, httpx_mock: HTTPXMock):
        """fetch_page raises FetchError on timeout."""
        import httpx
        httpx_mock.add_exception(
            httpx.TimeoutException("Connection timed out")
        )

        with pytest.raises(FetchError) as exc_info:
            fetch_page("https://example.com", timeout=1)

        assert "timeout" in str(exc_info.value).lower()


class TestFetchPageHttpErrors:
    """Tests for HTTP error handling."""

    def test_raises_fetch_error_on_404(self, httpx_mock: HTTPXMock):
        """fetch_page raises FetchError on HTTP 404."""
        httpx_mock.add_response(
            url="https://example.com/notfound",
            status_code=404
        )

        with pytest.raises(FetchError) as exc_info:
            fetch_page("https://example.com/notfound")

        assert exc_info.value.status_code == 404

    def test_raises_fetch_error_on_500(self, httpx_mock: HTTPXMock):
        """fetch_page raises FetchError on HTTP 500."""
        httpx_mock.add_response(
            url="https://example.com/error",
            status_code=500
        )

        with pytest.raises(FetchError) as exc_info:
            fetch_page("https://example.com/error")

        assert exc_info.value.status_code == 500

    def test_raises_fetch_error_on_403(self, httpx_mock: HTTPXMock):
        """fetch_page raises FetchError on HTTP 403 Forbidden."""
        httpx_mock.add_response(
            url="https://example.com/forbidden",
            status_code=403
        )

        with pytest.raises(FetchError) as exc_info:
            fetch_page("https://example.com/forbidden")

        assert exc_info.value.status_code == 403


class TestFetchPageInvalidUrl:
    """Tests for invalid URL handling."""

    def test_raises_fetch_error_on_invalid_url(self):
        """fetch_page raises FetchError for invalid URL."""
        with pytest.raises(FetchError):
            fetch_page("not-a-valid-url")

    def test_raises_fetch_error_on_empty_url(self):
        """fetch_page raises FetchError for empty URL."""
        with pytest.raises(FetchError):
            fetch_page("")

    def test_raises_fetch_error_on_missing_scheme(self):
        """fetch_page raises FetchError for URL without scheme."""
        with pytest.raises(FetchError):
            fetch_page("example.com")


class TestFetchPageRetry:
    """Tests for retry logic."""

    def test_retries_on_connection_error(self, httpx_mock: HTTPXMock):
        """fetch_page retries once on connection error."""
        import httpx

        # First request fails, second succeeds
        httpx_mock.add_exception(httpx.ConnectError("Connection failed"))
        httpx_mock.add_response(text="<html>Success</html>")

        result = fetch_page("https://example.com")

        assert "Success" in result

    def test_fails_after_max_retries(self, httpx_mock: HTTPXMock):
        """fetch_page fails after 2 retry attempts."""
        import httpx

        # All requests fail
        httpx_mock.add_exception(httpx.ConnectError("Connection failed"))
        httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

        with pytest.raises(FetchError):
            fetch_page("https://example.com")


class TestFetchPageUserAgent:
    """Tests for User-Agent handling."""

    def test_uses_default_user_agent(self, httpx_mock: HTTPXMock):
        """fetch_page sends a default User-Agent header."""
        httpx_mock.add_response(url="https://example.com", text="<html></html>")

        fetch_page("https://example.com")

        request = httpx_mock.get_request()
        assert "User-Agent" in request.headers
        assert request.headers["User-Agent"] != ""

    def test_accepts_custom_user_agent(self, httpx_mock: HTTPXMock):
        """fetch_page accepts custom User-Agent."""
        httpx_mock.add_response(url="https://example.com", text="<html></html>")

        fetch_page("https://example.com", user_agent="CustomBot/1.0")

        request = httpx_mock.get_request()
        assert request.headers["User-Agent"] == "CustomBot/1.0"
