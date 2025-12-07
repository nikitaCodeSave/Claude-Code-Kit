"""Tests for web2md exceptions module."""

import pytest

from web2md.exceptions import (
    Web2MdError,
    FetchError,
    ExtractionError,
    ConversionError,
)


class TestWeb2MdError:
    """Tests for base Web2MdError exception."""

    def test_is_exception_subclass(self):
        """Web2MdError should inherit from Exception."""
        assert issubclass(Web2MdError, Exception)

    def test_can_be_instantiated_with_message(self):
        """Web2MdError can be created with a message."""
        error = Web2MdError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_can_be_raised_and_caught(self):
        """Web2MdError can be raised and caught."""
        with pytest.raises(Web2MdError) as exc_info:
            raise Web2MdError("test error")
        assert "test error" in str(exc_info.value)


class TestFetchError:
    """Tests for FetchError exception."""

    def test_inherits_from_web2md_error(self):
        """FetchError should inherit from Web2MdError."""
        assert issubclass(FetchError, Web2MdError)

    def test_can_be_instantiated_with_url_and_message(self):
        """FetchError should include URL information."""
        error = FetchError("Connection timeout", url="https://example.com")
        assert "Connection timeout" in str(error)
        assert error.url == "https://example.com"

    def test_can_be_instantiated_with_status_code(self):
        """FetchError can include HTTP status code."""
        error = FetchError(
            "HTTP error",
            url="https://example.com",
            status_code=404
        )
        assert error.status_code == 404
        assert error.url == "https://example.com"

    def test_can_be_caught_as_web2md_error(self):
        """FetchError can be caught as Web2MdError."""
        with pytest.raises(Web2MdError):
            raise FetchError("test", url="https://example.com")


class TestExtractionError:
    """Tests for ExtractionError exception."""

    def test_inherits_from_web2md_error(self):
        """ExtractionError should inherit from Web2MdError."""
        assert issubclass(ExtractionError, Web2MdError)

    def test_can_be_instantiated_with_message(self):
        """ExtractionError can be created with a message."""
        error = ExtractionError("Failed to extract content")
        assert "Failed to extract content" in str(error)

    def test_can_include_url(self):
        """ExtractionError can include source URL."""
        error = ExtractionError(
            "No content found",
            url="https://example.com/page"
        )
        assert error.url == "https://example.com/page"

    def test_can_be_caught_as_web2md_error(self):
        """ExtractionError can be caught as Web2MdError."""
        with pytest.raises(Web2MdError):
            raise ExtractionError("test")


class TestConversionError:
    """Tests for ConversionError exception."""

    def test_inherits_from_web2md_error(self):
        """ConversionError should inherit from Web2MdError."""
        assert issubclass(ConversionError, Web2MdError)

    def test_can_be_instantiated_with_message(self):
        """ConversionError can be created with a message."""
        error = ConversionError("Failed to convert HTML to Markdown")
        assert "Failed to convert HTML to Markdown" in str(error)

    def test_can_be_caught_as_web2md_error(self):
        """ConversionError can be caught as Web2MdError."""
        with pytest.raises(Web2MdError):
            raise ConversionError("test")
