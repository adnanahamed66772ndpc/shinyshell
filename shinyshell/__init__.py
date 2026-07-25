"""
shinyshell — Beautiful terminal output for Python. Zero dependencies.
=====================================
One import. All the pretty you need.

    from shinyshell import Shell
    sh = Shell()
    sh.success("Deployed!")
    sh.table(users)
    sh.progress("Loading...")

Pure Python stdlib. Works on Linux, macOS, Windows.
"""

__version__ = "0.1.0"
__all__ = ["Shell"]

import os
import sys
import shutil
import textwrap
import math
from typing import Any, List, Dict, Optional, Union, Callable


# ── ANSI / Color utilities (stdlib only) ───────────────────────

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
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL
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

    def __call__(self, text: str, *styles: str, color: Optional[str] = None,
                 bg: Optional[str] = None) -> str:
        if not self.enabled:
            return str(text)
        codes = _ANSICodes()
        parts = []
        for s in styles:
            code = getattr(codes, s.upper(), None)
            if code:
                parts.append(code)
        if color:
            parts.append(codes.color(color))
        if bg:
            parts.append(codes.color(bg, background=True))
        if not parts:
            return str(text)
        return "".join(parts) + str(text) + codes.RESET


# ── Icons (Unicode, works everywhere) ──────────────────────────
_ICONS = {
    "success": "✨",
    "error": "💥",
    "warning": "⚠️",
    "info": "ℹ️",
    "question": "❓",
    "star": "⭐",
    "heart": "💜",
    "fire": "🔥",
    "rocket": "🚀",
    "check": "✅",
    "cross": "❌",
    "arrow": "→",
    "bullet": "•",
    "diamond": "◆",
    "pointer": "▸",
    "dot": "·",
    "lightning": "⚡",
    "clock": "🕐",
    "lock": "🔒",
    "unlock": "🔓",
    "key": "🔑",
    "gear": "⚙️",
    "package": "📦",
    "link": "🔗",
    "globe": "🌍",
    "mail": "📧",
    "phone": "📞",
    "pin": "📌",
    "bookmark": "🔖",
    "tag": "🏷️",
    "flag": "🚩",
    "target": "🎯",
    "trophy": "🏆",
    "medal": "🥇",
    "gift": "🎁",
    "party": "🎉",
    "sparkles": "✨",
    "magic": "🪄",
    "robot": "🤖",
    "bug": "🐛",
    "eyes": "👀",
    "brain": "🧠",
    "tools": "🛠️",
    "chart": "📊",
    "database": "🗄️",
    "file": "📄",
    "folder": "📁",
    "download": "📥",
    "upload": "📤",
    "save": "💾",
    "print": "🖨️",
    "search": "🔍",
    "shield": "🛡️",
    "money": "💰",
    "credit": "💳",
    "shopping": "🛒",
    "home": "🏠",
    "world": "🌐",
    "mobile": "📱",
    "desktop": "🖥️",
    "server": "🖥",
    "cloud": "☁️",
    "terminal": "💻",
}


# ── Borders / Frames ───────────────────────────────────────────
_BORDERS = {
    "single": "─│┌┐└┘├┤┬┴┼",
    "double": "═║╔╗╚╝╠╣╦╩╬",
    "round": "─│╭╮╰╯├┤┬┴┼",
    "bold": "━┃┏┓┗┛┣┫┳┻╋",
    "dashed": "┄┆┌┐└┘├┤┬┴┼",
    "none": "       ",
}


# ── Shell Class ─────────────────────────────────────────────────

class Shell:
    """Beautiful terminal output for Python scripts and CLIs."""

    def __init__(self, color: bool = True, width: Optional[int] = None):
        self._color_enabled = color and _supports_color()
        self._style = _Style(self._color_enabled)
        self._width = width or min(shutil.get_terminal_size().columns, 120)

    # ── Message Helpers ─────────────────────────────────────────

    def success(self, message: str) -> None:
        """Print a success message with green checkmark."""
        self._log("success", message, "green")

    def error(self, message: str) -> None:
        """Print an error message with red cross."""
        self._log("error", message, "red")

    def warning(self, message: str) -> None:
        """Print a warning with yellow triangle."""
        self._log("warning", message, "yellow")

    def info(self, message: str) -> None:
        """Print an info message with blue circle."""
        self._log("info", message, "cyan")

    def _log(self, level: str, message: str, color: str) -> None:
        icon = _ICONS.get(level, "•")
        prefix = self._style(f" {icon} ", bg=color, color="white")
        text = self._style(f" {message}", color=color)
        print(f"{prefix}{text}")

    # ── Sections & Headers ──────────────────────────────────────

    def header(self, title: str, level: int = 1) -> None:
        """Print a styled header."""
        if level == 1:
            line = "═" * (self._width - 4)
            text = self._style(f" {title} ", "bold")
            print(f"\n{self._style(f'╔{line}╗', color='cyan')}")
            print(f"{self._style('║', color='cyan')}{text.center(self._width - 2)}{self._style('║', color='cyan')}")
            print(f"{self._style(f'╚{line}╝', color='cyan')}")
        else:
            text = self._style(f"── {title} ", "bold", color="cyan")
            rest = "─" * max(0, self._width - len(title) - 10)
            print(f"\n{text}{self._style(rest, color='cyan', dim=True)}")

    def banner(self, text: str, color: str = "cyan") -> None:
        """Display a large ASCII banner."""
        from shinyshell.banner import render
        print(self._style(render(text), color=color))

    # ── Progress ────────────────────────────────────────────────

    def spinner(self, message: str, duration: float = 3.0) -> None:
        """Show a brief spinning animation with message."""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        import time
        start = time.time()
        i = 0
        print()
        try:
            while time.time() - start < duration:
                frame = self._style(frames[i % len(frames)], color="cyan")
                sys.stdout.write(f"\r  {frame} {message}")
                sys.stdout.flush()
                time.sleep(0.08)
                i += 1
            sys.stdout.write(f"\r  {self._style(_ICONS['check'], color='green')} {message} {self._style('Done!', color='green')}\n")
        except KeyboardInterrupt:
            sys.stdout.write(f"\r  {self._style(_ICONS['cross'], color='red')} {message} Cancelled\n")

    def progress(self, message: str = "Working") -> Callable[[int, int], None]:
        """Return a progress updater function. Use as context:

        update = sh.progress("Downloading")
        for i in range(100):
            update(i+1, 100)
        """
        def update(current: int, total: int):
            percent = int((current / max(total, 1)) * 100)
            bar_width = 30
            filled = int(bar_width * current / max(total, 1))
            bar = "█" * filled + "░" * (bar_width - filled)
            pct = f"{percent:3d}%"
            sys.stdout.write(f"\r  {message} {self._style(bar, color='cyan')} {pct}")
            sys.stdout.flush()
            if current >= total:
                print()
        return update

    def countdown(self, seconds: int, message: str = "Starting in") -> None:
        """Show an animated countdown."""
        import time
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r  {self._style(_ICONS['clock'], color='yellow')} {message} {self._style(str(i), 'bold', color='yellow')}...")
            sys.stdout.flush()
            time.sleep(1)
        print(f"\r  {self._style(_ICONS['rocket'], color='green')} {self._style('Go!', 'bold', color='green')}      ")

    # ── Tables ──────────────────────────────────────────────────

    def table(self, data: List[Dict[str, Any]], title: Optional[str] = None,
              style: str = "single") -> None:
        """Display data as a beautiful table.

        data = [
            {"Name": "Alice", "Role": "Developer", "Stars": 42},
            {"Name": "Bob", "Role": "Designer", "Stars": 17},
        ]
        sh.table(data, title="Team Members")
        """
        if not data:
            return

        keys = list(data[0].keys())
        col_widths = {k: max(len(str(k)), max(len(str(row.get(k, ""))) for row in data)) + 2
                      for k in keys}

        if title:
            print()
            print(self._style(f"  {title}", "bold"))

        border = _BORDERS.get(style, _BORDERS["single"])
        h, v, tl, tr, bl, br, l, r, t, b, x = list(border)

        total_width = sum(col_widths.values()) + len(keys) - 1

        # Top border
        top = tl + h * total_width + tr
        print(self._style(f"  {top}", color="bright_black"))

        # Header
        cells = [self._style(f" {str(k).ljust(col_widths[k])}", "bold")
                 for k in keys]
        print(f"  {v}{v.join(cells)}{v}")

        # Separator
        sep = l + h * total_width + r
        print(self._style(f"  {sep}", color="bright_black"))

        # Rows
        for row in data:
            cells = [f" {str(row.get(k, '')).ljust(col_widths[k])}" for k in keys]
            print(f"  {self._style(v, color='bright_black')}{v.join(cells)}{self._style(v, color='bright_black')}")

        # Bottom border
        bottom = bl + h * total_width + br
        print(self._style(f"  {bottom}", color="bright_black"))
        print()

    # ── Code / Syntax ───────────────────────────────────────────

    def code(self, source: str, language: str = "python") -> None:
        """Display syntax-highlighted code block."""
        keywords = {"def", "class", "import", "from", "return", "if", "else",
                    "elif", "for", "while", "try", "except", "finally", "with",
                    "as", "in", "not", "and", "or", "True", "False", "None",
                    "async", "await", "yield", "raise", "pass", "break", "continue"}
        strings_color = "green"
        kw_color = "magenta"
        comment_color = "bright_black"
        num_color = "yellow"
        func_color = "cyan"

        lines = source.strip().split("\n")
        max_num = len(str(len(lines)))
        print()

        for i, line in enumerate(lines):
            num = str(i + 1).rjust(max_num)
            prefix = self._style(f" {num} ", color="bright_black")

            # Basic syntax highlighting
            highlighted = []
            words = line.split(" ")
            for w in words:
                if w in keywords:
                    highlighted.append(self._style(w, color=kw_color))
                elif w.startswith("#"):
                    highlighted.append(self._style(w, color=comment_color))
                elif w.startswith(('"', "'")):
                    highlighted.append(self._style(w, color=strings_color))
                elif w.isdigit():
                    highlighted.append(self._style(w, color=num_color))
                elif w.endswith("(") and not w.startswith(('"', "'")):
                    highlighted.append(self._style(w, color=func_color))
                else:
                    highlighted.append(w)

            print(f"{prefix}{' '.join(highlighted)}")
        print()

    # ── Diff ────────────────────────────────────────────────────

    def diff(self, old: str, new: str, old_label: str = "OLD",
             new_label: str = "NEW") -> None:
        """Show a colored diff between two strings."""
        import difflib
        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)
        differ = difflib.unified_diff(old_lines, new_lines,
                                      fromfile=old_label, tofile=new_label)
        print()
        for line in differ:
            line = line.rstrip("\n")
            if line.startswith("+++"):
                print(self._style(f"  {line}", color="green"))
            elif line.startswith("---"):
                print(self._style(f"  {line}", color="red"))
            elif line.startswith("@@"):
                print(self._style(f"  {line}", color="cyan"))
            elif line.startswith("+"):
                print(self._style(f"  {line}", color="green"))
            elif line.startswith("-"):
                print(self._style(f"  {line}", color="red"))
            else:
                print(f"  {self._style(line, color='bright_black')}")
        print()

    # ── Tree ────────────────────────────────────────────────────

    def tree(self, path: str = ".", max_depth: int = 3,
             exclude: Optional[List[str]] = None) -> None:
        """Display a directory tree."""
        if exclude is None:
            exclude = [".git", "__pycache__", ".DS_Store", "node_modules",
                       ".venv", "venv", ".idea", ".vscode", "*.pyc"]

        print()
        print(self._style(f"  {path}", "bold", color="cyan"))

        def _match_exclude(name: str) -> bool:
            for pat in exclude:
                if pat.startswith("*"):
                    if name.endswith(pat[1:]):
                        return True
                elif name == pat:
                    return True
            return False

        def _walk(current: str, prefix: str = "", depth: int = 0):
            if depth >= max_depth:
                return
            try:
                entries = sorted(os.listdir(current))
            except PermissionError:
                print(f"{prefix}{self._style('└── [denied]', color='red')}")
                return

            entries = [e for e in entries if not _match_exclude(e)]
            for i, entry in enumerate(entries):
                full = os.path.join(current, entry)
                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "
                if os.path.isdir(full):
                    icon = _ICONS["folder"]
                    print(f"{prefix}{connector}{self._style(icon + ' ' + entry, color='cyan')}")
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    _walk(full, next_prefix, depth + 1)
                else:
                    icon = _ICONS["file"]
                    size = ""
                    try:
                        s = os.path.getsize(full)
                        if s > 1024 * 1024:
                            size = f" ({s / 1024 / 1024:.1f}MB)"
                        elif s > 1024:
                            size = f" ({s / 1024:.1f}KB)"
                    except Exception:
                        pass
                    print(f"{prefix}{connector}{self._style(icon, color='bright_black')} {entry}{self._style(size, color='bright_black')}")

        _walk(path)
        print()

    # ── Interactive ─────────────────────────────────────────────

    def confirm(self, question: str, default: bool = True) -> bool:
        """Ask a y/n question and return True/False."""
        hint = "[Y/n]" if default else "[y/N]"
        prompt = f"  {_ICONS['question']} {question} {self._style(hint, color='bright_black')}: "
        try:
            answer = input(prompt).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print()
            return False
        if not answer:
            return default
        return answer in ("y", "yes", "yeah", "yep", "sure")

    def choice(self, question: str, options: List[str]) -> Optional[str]:
        """Ask user to pick from a list of options."""
        print(f"\n  {self._style(_ICONS['question'], color='yellow')} {self._style(question, 'bold')}")
        for i, opt in enumerate(options, 1):
            print(f"    {self._style(str(i), color='cyan')}. {opt}")
        try:
            num = input(f"  {self._style('Enter number:', color='bright_black')} ")
            idx = int(num) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except (ValueError, KeyboardInterrupt, EOFError):
            pass
        return None

    # ── Boxed Content ──────────────────────────────────────────

    def box(self, content: str, title: Optional[str] = None,
            style: str = "round", color: str = "cyan") -> None:
        """Display content inside a styled box."""
        lines = content.strip().split("\n")
        max_len = max(len(l) for l in lines)
        width = min(max_len + 4, self._width - 4)

        border = _BORDERS.get(style, _BORDERS["round"])
        h, v, tl, tr, bl, br, l, r, t, b, x = list(border)

        print()
        if title:
            top = tl + h * 2 + f" {title} " + h * (width - len(title) - 4) + tr
        else:
            top = tl + h * width + tr
        print(self._style(f"  {top}", color=color))

        for line in lines:
            padded = line.ljust(width)
            print(f"  {self._style(v, color=color)} {padded} {self._style(v, color=color)}")

        bottom = bl + h * width + br
        print(self._style(f"  {bottom}", color=color))
        print()

    # ── Metrics / Stats ─────────────────────────────────────────

    def metrics(self, items: Dict[str, Union[str, int, float]]) -> None:
        """Display key-value metrics in a compact format."""
        print()
        max_key = max(len(k) for k in items.keys())
        for key, value in items.items():
            k = self._style(f"  {key.ljust(max_key)}", color="bright_black")
            if isinstance(value, (int, float)) and value > 0:
                v = self._style(f" {value:,}", "bold", color="green")
            elif isinstance(value, str) and value.startswith("✅"):
                v = self._style(f" {value}", "bold", color="green")
            elif isinstance(value, str) and value.startswith("❌"):
                v = self._style(f" {value}", color="red")
            else:
                v = f" {value}"
            print(f"{k} {self._style('→', color='cyan')}{v}")
        print()

    # ── Horizontal Rule ─────────────────────────────────────────

    def hr(self, label: Optional[str] = None) -> None:
        """Print a horizontal rule, optionally with a label."""
        if label:
            left = "─" * 4
            right = "─" * max(0, self._width - len(label) - 12)
            print(f"\n  {self._style(left, color='bright_black')} {self._style(label, 'bold', color='cyan')} {self._style(right, color='bright_black')}")
        else:
            print(f"  {self._style('─' * (self._width - 4), color='bright_black')}")

    @property
    def icons(self):
        """Access icon constants."""
        return _ICONS
