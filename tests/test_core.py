"""Tests for web2md core module."""

import pytest
from unittest.mock import patch

from web2md.core import url_to_markdown
from web2md.exceptions import FetchError, ExtractionError, ConversionError
from web2md.extractor import ExtractedContent


class TestUrlToMarkdownBasic:
    """Basic tests for url_to_markdown function."""

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_returns_markdown_string(
        self, mock_format, mock_extract, mock_fetch
    ):
        """url_to_markdown returns a markdown string."""
        mock_fetch.return_value = "<html><body>Content</body></html>"
        mock_extract.return_value = ExtractedContent(
            title="Test",
            content="<p>Content</p>",
            author=None,
            date=None,
            source_url="https://example.com",
        )
        mock_format.return_value = "# Test\n\nContent"

        result = url_to_markdown("https://example.com")

        assert isinstance(result, str)
        assert "# Test" in result

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_calls_fetch_with_url(
        self, mock_format, mock_extract, mock_fetch
    ):
        """url_to_markdown calls fetch_page with the URL."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.return_value = "# T\n\nC"

        url_to_markdown("https://example.com/page")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args[0][0] == "https://example.com/page"

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_calls_extract_with_html_and_url(
        self, mock_format, mock_extract, mock_fetch
    ):
        """url_to_markdown calls extract_content with HTML and URL."""
        mock_fetch.return_value = "<html><body>Test</body></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.return_value = "# T"

        url_to_markdown("https://example.com")

        mock_extract.assert_called_once()
        call_args = mock_extract.call_args
        assert "<html>" in call_args[0][0]
        assert call_args[0][1] == "https://example.com"


class TestUrlToMarkdownTimeout:
    """Tests for timeout handling."""

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_uses_default_timeout(
        self, mock_format, mock_extract, mock_fetch
    ):
        """url_to_markdown uses 30 second default timeout."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.return_value = "# T"

        url_to_markdown("https://example.com")

        call_kwargs = mock_fetch.call_args[1]
        assert call_kwargs.get("timeout", 30) == 30

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_accepts_custom_timeout(
        self, mock_format, mock_extract, mock_fetch
    ):
        """url_to_markdown passes custom timeout to fetch_page."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.return_value = "# T"

        url_to_markdown("https://example.com", timeout=60)

        call_kwargs = mock_fetch.call_args[1]
        assert call_kwargs.get("timeout") == 60


class TestUrlToMarkdownMetadata:
    """Tests for metadata handling."""

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_default_no_metadata(
        self, mock_format, mock_extract, mock_fetch
    ):
        """url_to_markdown excludes metadata by default."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.return_value = "# T"

        url_to_markdown("https://example.com")

        call_kwargs = mock_format.call_args[1]
        assert call_kwargs.get("include_metadata", False) is False

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_includes_metadata_when_requested(
        self, mock_format, mock_extract, mock_fetch
    ):
        """url_to_markdown includes metadata when requested."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.return_value = "---\ntitle: T\n---\n# T"

        url_to_markdown("https://example.com", include_metadata=True)

        call_kwargs = mock_format.call_args[1]
        assert call_kwargs.get("include_metadata") is True


class TestUrlToMarkdownFileSave:
    """Tests for file saving functionality."""

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_saves_to_file_when_path_provided(
        self, mock_format, mock_extract, mock_fetch, tmp_path
    ):
        """url_to_markdown saves to file when output_path is provided."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="Test", content="Content", author=None, date=None, source_url=None
        )
        mock_format.return_value = "# Test\n\nContent"

        output_file = tmp_path / "output.md"
        result = url_to_markdown(
            "https://example.com",
            output_path=str(output_file)
        )

        assert output_file.exists()
        assert output_file.read_text() == "# Test\n\nContent"
        assert result == "# Test\n\nContent"

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_accepts_path_object(
        self, mock_format, mock_extract, mock_fetch, tmp_path
    ):
        """url_to_markdown accepts Path object for output_path."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.return_value = "# T"

        output_file = tmp_path / "output.md"
        url_to_markdown("https://example.com", output_path=output_file)

        assert output_file.exists()

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_creates_parent_directories(
        self, mock_format, mock_extract, mock_fetch, tmp_path
    ):
        """url_to_markdown creates parent directories if needed."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.return_value = "# T"

        output_file = tmp_path / "subdir" / "nested" / "output.md"
        url_to_markdown("https://example.com", output_path=str(output_file))

        assert output_file.exists()

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_returns_markdown_even_when_saving(
        self, mock_format, mock_extract, mock_fetch, tmp_path
    ):
        """url_to_markdown returns markdown string even when saving to file."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.return_value = "# T\n\nContent"

        output_file = tmp_path / "output.md"
        result = url_to_markdown(
            "https://example.com",
            output_path=str(output_file)
        )

        assert result == "# T\n\nContent"


class TestUrlToMarkdownErrorPropagation:
    """Tests for error propagation."""

    @patch("web2md.core.fetch_page")
    def test_propagates_fetch_error(self, mock_fetch):
        """url_to_markdown propagates FetchError from fetcher."""
        mock_fetch.side_effect = FetchError(
            "Connection failed",
            url="https://example.com"
        )

        with pytest.raises(FetchError) as exc_info:
            url_to_markdown("https://example.com")

        assert "Connection failed" in str(exc_info.value)

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    def test_propagates_extraction_error(self, mock_extract, mock_fetch):
        """url_to_markdown propagates ExtractionError from extractor."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.side_effect = ExtractionError("No content found")

        with pytest.raises(ExtractionError) as exc_info:
            url_to_markdown("https://example.com")

        assert "No content found" in str(exc_info.value)

    @patch("web2md.core.fetch_page")
    @patch("web2md.core.extract_content")
    @patch("web2md.core.format_document")
    def test_propagates_conversion_error(
        self, mock_format, mock_extract, mock_fetch
    ):
        """url_to_markdown propagates ConversionError from converter."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ExtractedContent(
            title="T", content="C", author=None, date=None, source_url=None
        )
        mock_format.side_effect = ConversionError("Conversion failed")

        with pytest.raises(ConversionError) as exc_info:
            url_to_markdown("https://example.com")

        assert "Conversion failed" in str(exc_info.value)


class TestUrlToMarkdownIntegration:
    """Integration tests with minimal mocking."""

    @patch("web2md.core.fetch_page")
    def test_full_pipeline_with_sample_html(self, mock_fetch, sample_html):
        """url_to_markdown processes sample HTML through full pipeline."""
        mock_fetch.return_value = sample_html

        result = url_to_markdown("https://example.com")

        # Should contain converted content
        assert isinstance(result, str)
        assert len(result) > 0
        # Should have markdown headers
        assert "#" in result

    @patch("web2md.core.fetch_page")
    def test_full_pipeline_with_metadata(self, mock_fetch, sample_html):
        """url_to_markdown generates metadata when requested."""
        mock_fetch.return_value = sample_html

        result = url_to_markdown(
            "https://example.com/article",
            include_metadata=True
        )

        # Should have YAML frontmatter
        assert "---" in result
        assert "source:" in result or "title:" in result
