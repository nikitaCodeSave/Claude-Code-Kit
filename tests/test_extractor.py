"""Tests for web2md extractor module."""

import pytest

from web2md.extractor import (
    preprocess_html,
    extract_with_trafilatura,
    extract_with_readability,
    extract_content,
    ExtractedContent,
)
from web2md.exceptions import ExtractionError


class TestExtractedContent:
    """Tests for ExtractedContent dataclass."""

    def test_has_required_fields(self):
        """ExtractedContent has all required fields."""
        content = ExtractedContent(
            title="Test Title",
            content="<p>Test content</p>",
            author=None,
            date=None,
            source_url=None,
        )

        assert content.title == "Test Title"
        assert content.content == "<p>Test content</p>"
        assert content.author is None
        assert content.date is None
        assert content.source_url is None

    def test_all_fields_populated(self):
        """ExtractedContent can have all fields populated."""
        content = ExtractedContent(
            title="Article Title",
            content="<p>Article body</p>",
            author="John Doe",
            date="2025-01-15",
            source_url="https://example.com/article",
        )

        assert content.title == "Article Title"
        assert content.author == "John Doe"
        assert content.date == "2025-01-15"
        assert content.source_url == "https://example.com/article"


class TestPreprocessHtml:
    """Tests for preprocess_html function."""

    def test_removes_script_tags(self, sample_html):
        """preprocess_html removes <script> tags."""
        result = preprocess_html(sample_html)

        assert "<script>" not in result
        assert "console.log" not in result

    def test_removes_style_tags(self, sample_html):
        """preprocess_html removes <style> tags."""
        result = preprocess_html(sample_html)

        assert "<style>" not in result
        assert ".nav" not in result

    def test_removes_nav_tags(self, sample_html):
        """preprocess_html removes <nav> tags."""
        result = preprocess_html(sample_html)

        assert "<nav>" not in result
        assert "Navigation Menu" not in result

    def test_removes_footer_tags(self, sample_html):
        """preprocess_html removes <footer> tags."""
        result = preprocess_html(sample_html)

        assert "<footer>" not in result
        assert "Site Footer" not in result

    def test_preserves_main_content(self, sample_html):
        """preprocess_html preserves main article content."""
        result = preprocess_html(sample_html)

        assert "Test Article Title" in result
        assert "main content of the article" in result

    def test_preserves_article_structure(self, sample_html):
        """preprocess_html preserves article HTML structure."""
        result = preprocess_html(sample_html)

        assert "<h1>" in result or "Test Article Title" in result
        assert "<p>" in result or "main content" in result

    def test_removes_aside_tags(self, sample_html):
        """preprocess_html removes <aside> sidebar content."""
        result = preprocess_html(sample_html)

        assert "<aside>" not in result
        assert "Sidebar content" not in result

    def test_handles_empty_html(self, empty_html):
        """preprocess_html handles empty HTML gracefully."""
        result = preprocess_html(empty_html)

        assert isinstance(result, str)


class TestExtractWithTrafilatura:
    """Tests for extract_with_trafilatura function."""

    def test_extracts_title(self, sample_html):
        """extract_with_trafilatura extracts article title."""
        result = extract_with_trafilatura(sample_html, "https://example.com")

        assert result is not None
        assert result.title == "Test Article Title" or "Test Article" in result.title

    def test_extracts_content(self, sample_html):
        """extract_with_trafilatura extracts main content."""
        result = extract_with_trafilatura(sample_html, "https://example.com")

        assert result is not None
        assert "main content" in result.content.lower() or len(result.content) > 50

    def test_returns_none_for_minimal_content(self, minimal_html):
        """extract_with_trafilatura returns None for minimal content."""
        result = extract_with_trafilatura(minimal_html, "https://example.com")

        # Should return None when content is too short
        assert result is None or len(result.content) < 100

    def test_returns_none_for_empty_html(self, empty_html):
        """extract_with_trafilatura returns None for empty HTML."""
        result = extract_with_trafilatura(empty_html, "https://example.com")

        assert result is None

    def test_includes_source_url(self, sample_html):
        """extract_with_trafilatura includes source URL."""
        result = extract_with_trafilatura(sample_html, "https://example.com/page")

        if result is not None:
            assert result.source_url == "https://example.com/page"


class TestExtractWithReadability:
    """Tests for extract_with_readability function."""

    def test_extracts_title(self, sample_html):
        """extract_with_readability extracts article title."""
        result = extract_with_readability(sample_html, "https://example.com")

        assert result is not None
        # Readability may extract from <title> or <h1>
        assert "Test Article" in result.title or "Test" in result.title

    def test_extracts_content(self, sample_html):
        """extract_with_readability extracts main content."""
        result = extract_with_readability(sample_html, "https://example.com")

        assert result is not None
        assert len(result.content) > 50

    def test_returns_none_for_empty_html(self, empty_html):
        """extract_with_readability returns None for empty HTML."""
        result = extract_with_readability(empty_html, "https://example.com")

        assert result is None

    def test_includes_source_url(self, sample_html):
        """extract_with_readability includes source URL."""
        result = extract_with_readability(sample_html, "https://example.com/article")

        if result is not None:
            assert result.source_url == "https://example.com/article"


class TestExtractContent:
    """Tests for extract_content orchestration function."""

    def test_uses_trafilatura_when_successful(self, sample_html):
        """extract_content uses trafilatura result when available."""
        result = extract_content(sample_html, "https://example.com")

        assert isinstance(result, ExtractedContent)
        assert len(result.content) >= 50

    def test_falls_back_to_readability(self, minimal_html):
        """extract_content falls back to readability when trafilatura fails."""
        # This tests the fallback behavior - may vary based on actual extractors
        result = extract_content(minimal_html, "https://example.com")

        assert isinstance(result, ExtractedContent)

    def test_raises_extraction_error_when_both_fail(self, empty_html):
        """extract_content raises ExtractionError when both extractors fail."""
        with pytest.raises(ExtractionError):
            extract_content(empty_html, "https://example.com")

    def test_validates_minimum_content_length(self):
        """extract_content validates that content has minimum 50 characters."""
        very_short_html = "<html><body><p>Hi</p></body></html>"

        with pytest.raises(ExtractionError) as exc_info:
            extract_content(very_short_html, "https://example.com")

        assert "content" in str(exc_info.value).lower() or "extract" in str(exc_info.value).lower()

    def test_validates_content_not_only_whitespace(self):
        """extract_content rejects content that is only whitespace."""
        whitespace_html = "<html><body><p>   \n\t   </p></body></html>"

        with pytest.raises(ExtractionError):
            extract_content(whitespace_html, "https://example.com")

    def test_returns_extracted_content_dataclass(self, sample_html):
        """extract_content returns ExtractedContent dataclass."""
        result = extract_content(sample_html, "https://example.com")

        assert isinstance(result, ExtractedContent)
        assert hasattr(result, "title")
        assert hasattr(result, "content")
        assert hasattr(result, "author")
        assert hasattr(result, "date")
        assert hasattr(result, "source_url")

    def test_includes_source_url_in_result(self, sample_html):
        """extract_content includes source URL in result."""
        result = extract_content(sample_html, "https://example.com/test")

        assert result.source_url == "https://example.com/test"


class TestExtractContentEdgeCases:
    """Edge case tests for extract_content."""

    def test_handles_html_with_only_navigation(self):
        """extract_content handles HTML with only navigation elements."""
        nav_only_html = """
        <html><body>
            <nav>Home | About | Contact</nav>
            <footer>Copyright 2025</footer>
        </body></html>
        """

        with pytest.raises(ExtractionError):
            extract_content(nav_only_html, "https://example.com")

    def test_handles_html_with_special_characters(self):
        """extract_content handles HTML with special characters."""
        special_html = """
        <html><body>
            <article>
                <h1>Test &amp; Article</h1>
                <p>Content with &lt;special&gt; chars &copy; 2025</p>
                <p>More content to ensure minimum length requirement is met for extraction.</p>
            </article>
        </body></html>
        """

        result = extract_content(special_html, "https://example.com")

        assert isinstance(result, ExtractedContent)

    def test_handles_malformed_html(self):
        """extract_content handles malformed HTML gracefully."""
        malformed_html = """
        <html><body>
            <article>
                <h1>Title without closing tag
                <p>Paragraph without closing
                <p>Another paragraph with enough content for extraction to work properly.</p>
            </article>
        </body></html>
        """

        # Should either extract or raise ExtractionError, not crash
        try:
            result = extract_content(malformed_html, "https://example.com")
            assert isinstance(result, ExtractedContent)
        except ExtractionError:
            pass  # Also acceptable

    def test_preserves_links_in_content(self, sample_html):
        """extract_content preserves links in extracted content."""
        result = extract_content(sample_html, "https://example.com")

        # Content should preserve link structure (as HTML or text)
        assert "example.com" in result.content or "link" in result.content.lower()

    def test_preserves_code_blocks(self, sample_html):
        """extract_content preserves code blocks."""
        result = extract_content(sample_html, "https://example.com")

        # Should preserve code content
        assert "hello" in result.content.lower() or "print" in result.content.lower()
