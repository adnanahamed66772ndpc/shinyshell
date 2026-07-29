"""Tests for shinyshell core functionality."""

import pytest
from shinyshell import Shell


@pytest.fixture
def sh():
    """Create a Shell instance with no color for testing."""
    return Shell(color=False)


class TestMessages:
    """Test message/status methods."""

    def test_success(self, sh, capsys):
        sh.success("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.out

    def test_error(self, sh, capsys):
        sh.error("Error message")
        captured = capsys.readouterr()
        assert "Error message" in captured.out

    def test_warning(self, sh, capsys):
        sh.warning("Warning message")
        captured = capsys.readouterr()
        assert "Warning message" in captured.out

    def test_info(self, sh, capsys):
        sh.info("Info message")
        captured = capsys.readouterr()
        assert "Info message" in captured.out


class TestBadgeEmoji:
    """Test badge and emoji methods."""

    def test_badge(self, sh):
        result = sh.badge("test", "green")
        assert "test" in result

    def test_badge_default_color(self, sh):
        result = sh.badge("default")
        assert "default" in result

    def test_emoji_known(self, sh):
        assert sh.emoji("rocket") == "🚀"
        assert sh.emoji("star") == "⭐"

    def test_emoji_unknown(self, sh):
        assert sh.emoji("nonexistent") == "❓"


class TestTables:
    """Test table-related methods."""

    def test_table_empty(self, sh, capsys):
        sh.table([])
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_table_single_row(self, sh, capsys):
        sh.table([{"Name": "Alice", "Role": "Dev"}])
        captured = capsys.readouterr()
        assert "Name" in captured.out
        assert "Role" in captured.out
        assert "Alice" in captured.out

    def test_metrics(self, sh, capsys):
        sh.metrics({"CPU": "45%", "RAM": "8GB"})
        captured = capsys.readouterr()
        assert "CPU" in captured.out
        assert "RAM" in captured.out

    def test_metrics_positive_int(self, sh, capsys):
        sh.metrics({"Users": 1000})
        captured = capsys.readouterr()
        assert "Users" in captured.out
        assert "1,000" in captured.out


class TestCharts:
    """Test chart methods."""

    def test_pie_empty(self, sh, capsys):
        sh.pie({})
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_pie_basic(self, sh, capsys):
        sh.pie({"A": 50, "B": 50})
        captured = capsys.readouterr()
        assert "50%" in captured.out

    def test_bar_empty(self, sh, capsys):
        sh.bar({})
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_bar_basic(self, sh, capsys):
        sh.bar({"A": 85, "B": 62})
        captured = capsys.readouterr()
        assert "A" in captured.out
        assert "B" in captured.out

    def test_sparkline_basic(self, sh, capsys):
        sh.sparkline([1, 5, 2, 8, 3, 9, 4])
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_gauge(self, sh, capsys):
        sh.gauge(75, 100, "CPU")
        captured = capsys.readouterr()
        assert "CPU" in captured.out


class TestUtils:
    """Test utility methods."""

    def test_secret(self, sh):
        result = sh.secret("sk-abc123xyz")
        assert result.startswith("sk-")
        assert "****" in result
        assert result.endswith("xyz")

    def test_secret_short(self, sh):
        result = sh.secret("abc")
        assert result == "***"

    def test_ordinal(self, sh):
        assert sh.ordinal(1) == "1st"
        assert sh.ordinal(2) == "2nd"
        assert sh.ordinal(3) == "3rd"
        assert sh.ordinal(4) == "4th"
        assert sh.ordinal(11) == "11th"
        assert sh.ordinal(21) == "21st"
        assert sh.ordinal(42) == "42nd"

    def test_pluralize(self, sh):
        assert sh.pluralize("file", 0) == "files"
        assert sh.pluralize("file", 1) == "file"
        assert sh.pluralize("file", 2) == "files"

    def test_camel_case(self, sh):
        assert sh.camel_case("hello world") == "helloWorld"
        assert sh.camel_case("hello-world") == "helloWorld"

    def test_snake_case(self, sh):
        assert sh.snake_case("HelloWorld") == "hello_world"

    def test_strip_ansi(self, sh):
        result = sh.strip_ansi("\033[31mred\033[0m")
        assert result == "red"

    def test_truncate_no_truncation(self, sh):
        assert sh.truncate("hello") == "hello"

    def test_truncate_with_truncation(self, sh):
        result = sh.truncate("hello world this is a long text", 20)
        assert len(result) <= 20

    def test_link_no_color(self, sh):
        result = sh.link("GitHub", "https://github.com")
        assert "GitHub" in result
        assert "https://github.com" in result


class TestHighlight:
    """Test highlight method."""

    def test_highlight(self, sh):
        result = sh.highlight("Hello World", "World", "green")
        assert "Hello" in result
        assert "World" in result


class TestIcons:
    """Test icon access."""

    def test_icons_property(self, sh):
        icons = sh.icons
        assert "rocket" in icons
        assert icons["rocket"] == "🚀"


class TestVersion:
    """Test version info."""

    def test_version_attribute(self):
        from shinyshell import __version__
        assert __version__ == "0.6.2"

    def test_version_method(self, sh, capsys):
        sh.version()
        captured = capsys.readouterr()
        assert "Python" in captured.out
        assert "shinyshell" in captured.out


class TestQR:
    """Test QR code generation."""

    def test_qr_basic(self, sh, capsys):
        sh.qr("test")
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestInteractive:
    """Test interactive input methods (non-blocking)."""

    def test_search_filter(self, sh):
        items = ["apple", "banana", "cherry"]
        result = sh.search_filter(items, "a")
        assert "apple" in result
        assert "banana" in result
        assert "cherry" not in result


class TestTextUtils:
    """Test text utilities."""

    def test_wrap_text(self, sh, capsys):
        sh.wrap_text("hello world " * 10, width=30)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_align_text_center(self, sh):
        result = sh.align_text("Hi", 20, "center")
        assert len(result) == 20

    def test_align_text_right(self, sh):
        result = sh.align_text("Hi", 20, "right")
        assert len(result) == 20


class TestDataFormats:
    """Test data format methods."""

    def test_base64_encode_decode(self, sh):
        encoded = sh.base64_encode("hello")
        decoded = sh.base64_decode(encoded)
        assert decoded == "hello"

    def test_uuid_gen(self, sh, capsys):
        result = sh.uuid_gen(3)
        assert len(result) == 3
        for u in result:
            assert len(u) == 36
