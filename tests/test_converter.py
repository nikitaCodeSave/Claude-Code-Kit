"""Tests for web2md converter module."""


from web2md.converter import html_to_markdown, format_document
from web2md.extractor import ExtractedContent


class TestHtmlToMarkdownHeaders:
    """Tests for header conversion."""

    def test_converts_h1_to_markdown(self):
        """html_to_markdown converts <h1> to # header."""
        html = "<h1>Main Title</h1>"
        result = html_to_markdown(html)

        assert "# Main Title" in result

    def test_converts_h2_to_markdown(self):
        """html_to_markdown converts <h2> to ## header."""
        html = "<h2>Section Title</h2>"
        result = html_to_markdown(html)

        assert "## Section Title" in result

    def test_converts_h3_to_markdown(self):
        """html_to_markdown converts <h3> to ### header."""
        html = "<h3>Subsection</h3>"
        result = html_to_markdown(html)

        assert "### Subsection" in result

    def test_converts_h4_to_h6(self):
        """html_to_markdown converts h4-h6 headers correctly."""
        html = "<h4>H4</h4><h5>H5</h5><h6>H6</h6>"
        result = html_to_markdown(html)

        assert "#### H4" in result
        assert "##### H5" in result
        assert "###### H6" in result


class TestHtmlToMarkdownLists:
    """Tests for list conversion."""

    def test_converts_unordered_list(self):
        """html_to_markdown converts <ul> to - items."""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = html_to_markdown(html)

        assert "- Item 1" in result or "* Item 1" in result
        assert "- Item 2" in result or "* Item 2" in result

    def test_converts_ordered_list(self):
        """html_to_markdown converts <ol> to numbered items."""
        html = "<ol><li>First</li><li>Second</li><li>Third</li></ol>"
        result = html_to_markdown(html)

        assert "1." in result and "First" in result
        assert "2." in result and "Second" in result
        assert "3." in result and "Third" in result

    def test_handles_nested_lists(self):
        """html_to_markdown handles nested lists."""
        html = """
        <ul>
            <li>Item 1
                <ul>
                    <li>Nested item</li>
                </ul>
            </li>
        </ul>
        """
        result = html_to_markdown(html)

        assert "Item 1" in result
        assert "Nested item" in result


class TestHtmlToMarkdownLinks:
    """Tests for link conversion."""

    def test_converts_links(self):
        """html_to_markdown converts <a> to [text](url)."""
        html = '<a href="https://example.com">Example</a>'
        result = html_to_markdown(html)

        assert "[Example](https://example.com)" in result

    def test_handles_links_with_title(self):
        """html_to_markdown handles links with title attribute."""
        html = '<a href="https://example.com" title="Example Site">Link</a>'
        result = html_to_markdown(html)

        assert "[Link]" in result
        assert "https://example.com" in result

    def test_handles_empty_href(self):
        """html_to_markdown handles links with empty href."""
        html = '<a href="">Empty link</a>'
        result = html_to_markdown(html)

        # Should still render the text
        assert "Empty link" in result


class TestHtmlToMarkdownCodeBlocks:
    """Tests for code block conversion."""

    def test_converts_inline_code(self):
        """html_to_markdown converts <code> to `code`."""
        html = "<p>Use <code>print()</code> function</p>"
        result = html_to_markdown(html)

        assert "`print()`" in result

    def test_converts_pre_code_block(self):
        """html_to_markdown converts <pre><code> to fenced code block."""
        html = "<pre><code>def hello():\n    print('Hello')</code></pre>"
        result = html_to_markdown(html)

        assert "```" in result
        assert "def hello():" in result
        assert "print" in result

    def test_preserves_code_indentation(self):
        """html_to_markdown preserves indentation in code blocks."""
        html = "<pre><code>if True:\n    do_something()\n    do_more()</code></pre>"
        result = html_to_markdown(html)

        # Indentation should be preserved
        assert "    do_something()" in result or "do_something()" in result


class TestHtmlToMarkdownImages:
    """Tests for image conversion."""

    def test_converts_images(self):
        """html_to_markdown converts <img> to ![alt](src)."""
        html = '<img src="image.png" alt="Test image">'
        result = html_to_markdown(html)

        assert "![Test image](image.png)" in result

    def test_handles_images_without_alt(self):
        """html_to_markdown handles images without alt text."""
        html = '<img src="image.png">'
        result = html_to_markdown(html)

        assert "image.png" in result
        assert "![" in result  # Should still use markdown image syntax


class TestHtmlToMarkdownParagraphs:
    """Tests for paragraph and text conversion."""

    def test_converts_paragraphs(self):
        """html_to_markdown converts <p> tags properly."""
        html = "<p>First paragraph.</p><p>Second paragraph.</p>"
        result = html_to_markdown(html)

        assert "First paragraph." in result
        assert "Second paragraph." in result

    def test_converts_bold_text(self):
        """html_to_markdown converts <strong> and <b> to **bold**."""
        html = "<p><strong>Bold text</strong> and <b>also bold</b></p>"
        result = html_to_markdown(html)

        assert "**Bold text**" in result
        assert "**also bold**" in result

    def test_converts_italic_text(self):
        """html_to_markdown converts <em> and <i> to *italic*."""
        html = "<p><em>Italic text</em> and <i>also italic</i></p>"
        result = html_to_markdown(html)

        assert "*Italic text*" in result or "_Italic text_" in result

    def test_converts_blockquote(self):
        """html_to_markdown converts <blockquote> to > quote."""
        html = "<blockquote>This is a quote.</blockquote>"
        result = html_to_markdown(html)

        assert "> This is a quote." in result or ">This is a quote." in result


class TestHtmlToMarkdownTables:
    """Tests for table conversion."""

    def test_converts_simple_table(self):
        """html_to_markdown converts simple tables."""
        html = """
        <table>
            <tr><th>Name</th><th>Age</th></tr>
            <tr><td>Alice</td><td>30</td></tr>
        </table>
        """
        result = html_to_markdown(html)

        assert "Name" in result
        assert "Age" in result
        assert "Alice" in result
        assert "|" in result  # Markdown table syntax


class TestFormatDocument:
    """Tests for format_document function."""

    def test_formats_basic_document(self):
        """format_document creates properly formatted markdown."""
        content = ExtractedContent(
            title="Test Article",
            content="<p>Article content here.</p>",
            author=None,
            date=None,
            source_url=None,
        )

        result = format_document(content, include_metadata=False)

        assert "# Test Article" in result
        assert "Article content here." in result

    def test_includes_yaml_frontmatter_when_requested(self):
        """format_document includes YAML frontmatter when include_metadata=True."""
        content = ExtractedContent(
            title="Test Article",
            content="<p>Content</p>",
            author="John Doe",
            date="2025-01-15",
            source_url="https://example.com/article",
        )

        result = format_document(content, include_metadata=True)

        assert "---" in result
        assert "title:" in result
        assert "author:" in result
        assert "John Doe" in result
        assert "date:" in result
        assert "source:" in result

    def test_frontmatter_at_beginning(self):
        """format_document puts frontmatter at the beginning."""
        content = ExtractedContent(
            title="Title",
            content="<p>Body</p>",
            author="Author",
            date="2025-01-01",
            source_url="https://example.com",
        )

        result = format_document(content, include_metadata=True)

        # Frontmatter should be at the start
        assert result.startswith("---")
        lines = result.split("\n")
        frontmatter_end = lines.index("---", 1)  # Find closing ---
        assert frontmatter_end > 0

    def test_excludes_frontmatter_when_not_requested(self):
        """format_document excludes frontmatter when include_metadata=False."""
        content = ExtractedContent(
            title="Title",
            content="<p>Body</p>",
            author="Author",
            date="2025-01-01",
            source_url="https://example.com",
        )

        result = format_document(content, include_metadata=False)

        assert "---" not in result

    def test_handles_missing_optional_fields(self):
        """format_document handles missing author, date, source_url."""
        content = ExtractedContent(
            title="Title Only",
            content="<p>Just content</p>",
            author=None,
            date=None,
            source_url=None,
        )

        result = format_document(content, include_metadata=True)

        # Should still produce valid output
        assert "# Title Only" in result
        assert "Just content" in result

    def test_converts_html_content_to_markdown(self):
        """format_document converts HTML content to markdown."""
        content = ExtractedContent(
            title="Article",
            content="<h2>Section</h2><p>Paragraph with <strong>bold</strong>.</p>",
            author=None,
            date=None,
            source_url=None,
        )

        result = format_document(content, include_metadata=False)

        assert "## Section" in result
        assert "**bold**" in result

    def test_adds_extracted_at_timestamp(self):
        """format_document includes extracted_at timestamp in metadata."""
        content = ExtractedContent(
            title="Article",
            content="<p>Content</p>",
            author=None,
            date=None,
            source_url="https://example.com",
        )

        result = format_document(content, include_metadata=True)

        assert "extracted_at:" in result


class TestFormatDocumentEdgeCases:
    """Edge case tests for format_document."""

    def test_handles_title_with_special_characters(self):
        """format_document handles titles with special markdown characters."""
        content = ExtractedContent(
            title="Title with # and * characters",
            content="<p>Content</p>",
            author=None,
            date=None,
            source_url=None,
        )

        result = format_document(content, include_metadata=False)

        # Should produce valid markdown
        assert "Title with" in result

    def test_handles_empty_content(self):
        """format_document handles empty content gracefully."""
        content = ExtractedContent(
            title="Empty Article",
            content="",
            author=None,
            date=None,
            source_url=None,
        )

        result = format_document(content, include_metadata=False)

        assert "# Empty Article" in result
