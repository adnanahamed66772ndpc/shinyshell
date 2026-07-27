"""ANSI color utilities and style engine. Pure stdlib, zero dependencies."""

import os
import sys


def _supports_color() -> bool:
    """Check if the terminal supports color output."""
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            mode = ctypes.c_uint32()
            handle = kernel32.GetStdHandle(-11)
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            return True
        except Exception:
            return False
    term = os.environ.get("TERM", "")
    if term == "dumb":
        return False
    if "NO_COLOR" in os.environ:
        return False
    return True


class _ANSICodes:
    """ANSI escape codes for colors and styles."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    STRIKE = "\033[9m"

    COLORS = {
        "black": 30, "red": 31, "green": 32, "yellow": 33,
        "blue": 34, "magenta": 35, "cyan": 36, "white": 37,
        "bright_black": 90, "bright_red": 91, "bright_green": 92,
        "bright_yellow": 93, "bright_blue": 94, "bright_magenta": 95,
        "bright_cyan": 96, "bright_white": 97,
    }

    BG_COLORS = {
        "black": 40, "red": 41, "green": 42, "yellow": 43,
        "blue": 44, "magenta": 45, "cyan": 46, "white": 47,
    }

    @classmethod
    def color(cls, name: str, background: bool = False) -> str:
        if background:
            return f"\033[{cls.BG_COLORS.get(name, 40)}m"
        return f"\033[{cls.COLORS.get(name, 37)}m"

    @classmethod
    def rgb(cls, r: int, g: int, b: int, background: bool = False) -> str:
        base = 48 if background else 38
        return f"\033[{base};2;{r};{g};{b}m"


class _Style:
    """Applies styles to text only if color is supported."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def __call__(self, text: str, *styles: str, color: str | None = None,
                 bg: str | None = None, dim: bool = False) -> str:
        if not self.enabled:
            return str(text)
        codes = _ANSICodes()
        parts = []
        for s in styles:
            code = getattr(codes, s.upper(), None)
            if code:
                parts.append(code)
        if dim:
            parts.append(codes.DIM)
        if color:
            parts.append(codes.color(color))
        if bg:
            parts.append(codes.color(bg, background=True))
        if not parts:
            return str(text)
        return "".join(parts) + str(text) + codes.RESET
