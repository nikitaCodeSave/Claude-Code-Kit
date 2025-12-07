"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_html() -> str:
    """Sample HTML page with article content."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Article</title>
        <meta name="author" content="John Doe">
        <script>console.log('test');</script>
        <style>.nav { color: red; }</style>
    </head>
    <body>
        <nav>Navigation Menu</nav>
        <header>Site Header</header>
        <main>
            <article>
                <h1>Test Article Title</h1>
                <p>This is the main content of the article.</p>
                <p>It has multiple paragraphs with <a href="https://example.com">links</a>.</p>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
                <pre><code>def hello():
    print("Hello, World!")</code></pre>
            </article>
        </main>
        <aside>Sidebar content</aside>
        <footer>Site Footer</footer>
    </body>
    </html>
    """


@pytest.fixture
def minimal_html() -> str:
    """Minimal HTML with very little content."""
    return "<html><body><p>Short</p></body></html>"


@pytest.fixture
def empty_html() -> str:
    """Empty HTML page."""
    return "<html><body></body></html>"
