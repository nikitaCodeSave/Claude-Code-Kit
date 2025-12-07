"""web2md CLI module.

Command-line interface for web2md.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Sequence

from web2md.core import url_to_markdown
from web2md.exceptions import FetchError, ExtractionError, ConversionError


# Exit codes
EXIT_SUCCESS = 0
EXIT_FETCH_ERROR = 1
EXIT_EXTRACTION_ERROR = 2
EXIT_CONVERSION_ERROR = 3


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (default: sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="web2md",
        description="Convert web pages to Markdown",
    )

    parser.add_argument(
        "url",
        help="URL of the web page to convert",
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)",
        default=None,
    )

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )

    parser.add_argument(
        "-m", "--metadata",
        action="store_true",
        help="Include YAML frontmatter with metadata",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    return parser.parse_args(args)


def main(args: Sequence[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command-line arguments (default: sys.argv[1:]).

    Returns:
        Exit code (0=success, 1=fetch error, 2=extraction error, 3=conversion error).
    """
    parsed_args = parse_args(args)

    # Configure logging
    if parsed_args.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s: %(message)s",
            stream=sys.stderr,
        )
        logging.info(f"Fetching URL: {parsed_args.url}")

    try:
        markdown = url_to_markdown(
            parsed_args.url,
            output_path=parsed_args.output,
            timeout=parsed_args.timeout,
            include_metadata=parsed_args.metadata,
        )

        if parsed_args.verbose:
            logging.info("Conversion successful")

        # Save to file or output to stdout
        if parsed_args.output:
            # Write file (in case url_to_markdown is mocked in tests)
            output_path = Path(parsed_args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown, encoding="utf-8")
        else:
            print(markdown)

        return EXIT_SUCCESS

    except FetchError as e:
        print(f"Error: Failed to fetch URL - {e}", file=sys.stderr)
        return EXIT_FETCH_ERROR

    except ExtractionError as e:
        print(f"Error: Failed to extract content - {e}", file=sys.stderr)
        return EXIT_EXTRACTION_ERROR

    except ConversionError as e:
        print(f"Error: Failed to convert to Markdown - {e}", file=sys.stderr)
        return EXIT_CONVERSION_ERROR


def run() -> None:
    """Run the CLI with sys.argv arguments.

    This is the main entry point for the console script.
    """
    exit_code = main()
    sys.exit(exit_code)
