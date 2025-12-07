"""Tests for web2md CLI module."""

import pytest
import sys
from unittest.mock import patch

from web2md.cli import parse_args, main, run
from web2md.exceptions import FetchError, ExtractionError, ConversionError


class TestParseArgs:
    """Tests for argument parsing."""

    def test_parses_url_argument(self):
        """parse_args parses URL positional argument."""
        args = parse_args(["https://example.com"])

        assert args.url == "https://example.com"

    def test_parses_output_short_flag(self):
        """parse_args parses -o flag for output file."""
        args = parse_args(["https://example.com", "-o", "output.md"])

        assert args.output == "output.md"

    def test_parses_output_long_flag(self):
        """parse_args parses --output flag for output file."""
        args = parse_args(["https://example.com", "--output", "output.md"])

        assert args.output == "output.md"

    def test_parses_timeout_short_flag(self):
        """parse_args parses -t flag for timeout."""
        args = parse_args(["https://example.com", "-t", "60"])

        assert args.timeout == 60

    def test_parses_timeout_long_flag(self):
        """parse_args parses --timeout flag for timeout."""
        args = parse_args(["https://example.com", "--timeout", "45"])

        assert args.timeout == 45

    def test_default_timeout_is_30(self):
        """parse_args defaults timeout to 30 seconds."""
        args = parse_args(["https://example.com"])

        assert args.timeout == 30

    def test_parses_metadata_short_flag(self):
        """parse_args parses -m flag for metadata."""
        args = parse_args(["https://example.com", "-m"])

        assert args.metadata is True

    def test_parses_metadata_long_flag(self):
        """parse_args parses --metadata flag."""
        args = parse_args(["https://example.com", "--metadata"])

        assert args.metadata is True

    def test_default_metadata_is_false(self):
        """parse_args defaults metadata to False."""
        args = parse_args(["https://example.com"])

        assert args.metadata is False

    def test_parses_verbose_short_flag(self):
        """parse_args parses -v flag for verbose mode."""
        args = parse_args(["https://example.com", "-v"])

        assert args.verbose is True

    def test_parses_verbose_long_flag(self):
        """parse_args parses --verbose flag."""
        args = parse_args(["https://example.com", "--verbose"])

        assert args.verbose is True

    def test_default_verbose_is_false(self):
        """parse_args defaults verbose to False."""
        args = parse_args(["https://example.com"])

        assert args.verbose is False

    def test_all_flags_together(self):
        """parse_args handles all flags together."""
        args = parse_args([
            "https://example.com",
            "-o", "out.md",
            "-t", "120",
            "-m",
            "-v"
        ])

        assert args.url == "https://example.com"
        assert args.output == "out.md"
        assert args.timeout == 120
        assert args.metadata is True
        assert args.verbose is True

    def test_requires_url_argument(self):
        """parse_args requires URL argument."""
        with pytest.raises(SystemExit):
            parse_args([])


class TestMainFunction:
    """Tests for main() function exit codes."""

    @patch("web2md.cli.url_to_markdown")
    def test_returns_0_on_success(self, mock_convert):
        """main() returns exit code 0 on success."""
        mock_convert.return_value = "# Title\n\nContent"

        exit_code = main(["https://example.com"])

        assert exit_code == 0

    @patch("web2md.cli.url_to_markdown")
    def test_returns_1_on_fetch_error(self, mock_convert):
        """main() returns exit code 1 on FetchError."""
        mock_convert.side_effect = FetchError(
            "Connection failed",
            url="https://example.com"
        )

        exit_code = main(["https://example.com"])

        assert exit_code == 1

    @patch("web2md.cli.url_to_markdown")
    def test_returns_2_on_extraction_error(self, mock_convert):
        """main() returns exit code 2 on ExtractionError."""
        mock_convert.side_effect = ExtractionError("No content found")

        exit_code = main(["https://example.com"])

        assert exit_code == 2

    @patch("web2md.cli.url_to_markdown")
    def test_returns_3_on_conversion_error(self, mock_convert):
        """main() returns exit code 3 on ConversionError."""
        mock_convert.side_effect = ConversionError("Conversion failed")

        exit_code = main(["https://example.com"])

        assert exit_code == 3


class TestStdoutOutput:
    """Tests for stdout output."""

    @patch("web2md.cli.url_to_markdown")
    def test_prints_to_stdout_without_output_flag(self, mock_convert, capsys):
        """main() prints markdown to stdout when no -o flag."""
        mock_convert.return_value = "# Test Article\n\nContent here."

        main(["https://example.com"])

        captured = capsys.readouterr()
        assert "# Test Article" in captured.out
        assert "Content here." in captured.out

    @patch("web2md.cli.url_to_markdown")
    def test_no_stdout_when_output_flag(self, mock_convert, capsys, tmp_path):
        """main() does not print to stdout when -o flag is used."""
        mock_convert.return_value = "# Title\n\nContent"
        output_file = tmp_path / "output.md"

        main(["https://example.com", "-o", str(output_file)])

        captured = capsys.readouterr()
        # Should not print content to stdout (maybe just success message)
        assert "# Title" not in captured.out or "Content" not in captured.out


class TestFileOutput:
    """Tests for file output."""

    @patch("web2md.cli.url_to_markdown")
    def test_saves_to_file_with_output_flag(self, mock_convert, tmp_path):
        """main() saves markdown to file when -o flag is used."""
        mock_convert.return_value = "# Article\n\nContent"
        output_file = tmp_path / "article.md"

        main(["https://example.com", "-o", str(output_file)])

        assert output_file.exists()
        assert output_file.read_text() == "# Article\n\nContent"

    @patch("web2md.cli.url_to_markdown")
    def test_passes_output_path_to_converter(self, mock_convert, tmp_path):
        """main() passes output_path to url_to_markdown."""
        mock_convert.return_value = "# Title"
        output_file = tmp_path / "out.md"

        main(["https://example.com", "-o", str(output_file)])

        call_kwargs = mock_convert.call_args[1]
        assert str(output_file) in str(call_kwargs.get("output_path", ""))


class TestVerboseMode:
    """Tests for verbose mode."""

    @patch("web2md.cli.url_to_markdown")
    def test_verbose_outputs_progress(self, mock_convert, capsys):
        """main() outputs progress information in verbose mode."""
        mock_convert.return_value = "# Title"

        main(["https://example.com", "-v"])

        captured = capsys.readouterr()
        # Should show some progress/logging info
        assert len(captured.err) > 0 or len(captured.out) > 0

    @patch("web2md.cli.url_to_markdown")
    def test_non_verbose_is_quiet(self, mock_convert, capsys):
        """main() is quiet without verbose flag (except output)."""
        mock_convert.return_value = "# Title"

        main(["https://example.com"])

        out, err = capsys.readouterr()
        # stderr should be empty without verbose
        assert err == ""


class TestMetadataFlag:
    """Tests for metadata flag."""

    @patch("web2md.cli.url_to_markdown")
    def test_passes_metadata_flag_to_converter(self, mock_convert):
        """main() passes include_metadata to url_to_markdown."""
        mock_convert.return_value = "---\ntitle: T\n---\n# T"

        main(["https://example.com", "-m"])

        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs.get("include_metadata") is True

    @patch("web2md.cli.url_to_markdown")
    def test_default_no_metadata(self, mock_convert):
        """main() passes include_metadata=False by default."""
        mock_convert.return_value = "# Title"

        main(["https://example.com"])

        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs.get("include_metadata", False) is False


class TestTimeoutFlag:
    """Tests for timeout flag."""

    @patch("web2md.cli.url_to_markdown")
    def test_passes_timeout_to_converter(self, mock_convert):
        """main() passes timeout to url_to_markdown."""
        mock_convert.return_value = "# Title"

        main(["https://example.com", "-t", "60"])

        call_kwargs = mock_convert.call_args[1]
        assert call_kwargs.get("timeout") == 60


class TestErrorMessages:
    """Tests for error message output."""

    @patch("web2md.cli.url_to_markdown")
    def test_prints_fetch_error_message(self, mock_convert, capsys):
        """main() prints fetch error message to stderr."""
        mock_convert.side_effect = FetchError(
            "Connection timeout",
            url="https://example.com"
        )

        main(["https://example.com"])

        captured = capsys.readouterr()
        assert "error" in captured.err.lower() or "timeout" in captured.err.lower()

    @patch("web2md.cli.url_to_markdown")
    def test_prints_extraction_error_message(self, mock_convert, capsys):
        """main() prints extraction error message to stderr."""
        mock_convert.side_effect = ExtractionError("No content found")

        main(["https://example.com"])

        captured = capsys.readouterr()
        assert "error" in captured.err.lower() or "content" in captured.err.lower()


class TestRunFunction:
    """Tests for run() entry point function."""

    @patch("web2md.cli.main")
    @patch("sys.exit")
    def test_run_calls_main_with_argv(self, mock_exit, mock_main):
        """run() calls main() with sys.argv arguments."""
        mock_main.return_value = 0

        with patch.object(sys, "argv", ["web2md", "https://example.com"]):
            run()

        mock_main.assert_called_once()

    @patch("web2md.cli.main")
    @patch("sys.exit")
    def test_run_exits_with_main_return_code(self, mock_exit, mock_main):
        """run() exits with main()'s return code."""
        mock_main.return_value = 2

        with patch.object(sys, "argv", ["web2md", "https://example.com"]):
            run()

        mock_exit.assert_called_with(2)
