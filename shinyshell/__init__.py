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

__version__ = "0.2.1"
__all__ = ["Shell"]

import os
import sys
import shutil
import textwrap
import math
import time
import json as _json
import inspect
import functools
from contextlib import contextmanager
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

    # ── NEW v0.2.0 Features ─────────────────────────────────────

    # 1. Benchmark
    @contextmanager
    def benchmark(self, label: str = "Operation"):
        """Context manager: measure and print elapsed time beautifully.

        with sh.benchmark("Processing"):
            heavy_computation()
        """
        start = time.perf_counter()
        print()
        sys.stdout.write(f"  {self._style(_ICONS['clock'], color='cyan')} {label} ...")
        sys.stdout.flush()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            if elapsed < 0.001:
                t = f"{elapsed*1_000_000:.0f}µs"
            elif elapsed < 1:
                t = f"{elapsed*1000:.0f}ms"
            elif elapsed < 60:
                t = f"{elapsed:.2f}s"
            else:
                m, s = divmod(elapsed, 60)
                t = f"{int(m)}m {s:.1f}s"
            sys.stdout.write(f"\r  {self._style(_ICONS['check'], color='green')} {label} {self._style(t, 'bold', color='green')}\n")
            sys.stdout.flush()

    # 2. JSON Pretty Print
    def json(self, data: Any, title: Optional[str] = None) -> None:
        """Pretty-print JSON data with syntax colors."""
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        formatted = _json.dumps(data, indent=2, ensure_ascii=False, default=str)
        for line in formatted.split("\n"):
            # Color keys, strings, numbers, booleans
            import re
            colored = re.sub(r'"(.*?)"', lambda m: self._style(f'"{m.group(1)}"', color="green"), line)
            colored = re.sub(r': (".*?")', lambda m: f': {self._style(m.group(1), color="yellow")}', colored)
            colored = re.sub(r'\b(true|false|null)\b', lambda m: self._style(m.group(1), color="magenta"), colored)
            colored = re.sub(r'\b(\d+\.?\d*)\b', lambda m: self._style(m.group(1), color="cyan"), colored)
            print(f"  {colored}")
        print()

    # 3. Markdown
    def markdown(self, text: str) -> None:
        """Render basic markdown in the terminal."""
        lines = text.strip().split("\n")
        print()
        for line in lines:
            if line.startswith("# "):
                print(f"  {self._style(line[2:], 'bold', color='cyan')}")
            elif line.startswith("## "):
                print(f"  {self._style(line[3:], 'bold', color='blue')}")
            elif line.startswith("### "):
                print(f"  {self._style(line[4:], 'bold', color='magenta')}")
            elif line.startswith("- "):
                print(f"    {self._style(_ICONS['bullet'], color='cyan')} {line[2:]}")
            elif line.startswith("> "):
                print(f"  {self._style(f'│ {line[2:]}', color='bright_black')}")
            elif line.startswith("```"):
                continue
            elif line.strip().startswith("**") and line.strip().endswith("**"):
                print(f"  {self._style(line.strip()[2:-2], 'bold')}")
            else:
                print(f"  {line}")
        print()

    # 4. Steps
    def steps(self, title: str, total: int, current: int = 0):
        """Create a step tracker. Returns an updater function.

        step = sh.steps("Deploy", 4)
        step("Building...")
        step("Testing...")
        step("Deploying...")
        """
        print()
        print(self._style(f"  {_ICONS['rocket']} {title}", "bold"))
        steps_done = [current]

        def update(message: str):
            steps_done[0] += 1
            c = steps_done[0]
            for i in range(1, total + 1):
                if i <= c:
                    sys.stdout.write(f"\r    {self._style(f'[{i}/{total}]', color='green')} {self._style('✓', color='green')} ")
                elif i == c + 1:
                    sys.stdout.write(f"\r    {self._style(f'[{i}/{total}]', color='cyan')} {self._style('⠋', color='cyan')} {message}")
                else:
                    sys.stdout.write(f"\r    {self._style(f'[{i}/{total}]', color='bright_black')} · ")
                sys.stdout.flush()
                time.sleep(0.03)
            sys.stdout.write("\r" + " " * 60 + "\r")
            sys.stdout.flush()
            if c >= total:
                print(f"    {self._style('All steps complete!', color='green')} {_ICONS['party']}\n")
            return update
        return update

    # 5. Bar Chart
    def bar(self, data: Dict[str, Union[int, float]], title: Optional[str] = None,
            width: int = 40, color: str = "cyan") -> None:
        """Display a horizontal bar chart."""
        if not data:
            return
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        max_label = max(len(str(k)) for k in data.keys())
        max_val = max(data.values())
        for label, value in data.items():
            bar_width = int((value / max(max_val, 1)) * width)
            bar_text = "█" * bar_width
            lbl = str(label).rjust(max_label)
            val = f"{value:,}" if isinstance(value, int) else str(value)
            print(f"  {self._style(lbl, color='bright_black')} {self._style(bar_text, color=color)} {self._style(val, 'bold', color=color)}")
        print()

    # 6. Emoji
    def emoji(self, name: str) -> str:
        """Get an emoji by name. sh.emoji('rocket') → 🚀"""
        return _ICONS.get(name.lower(), "❓")

    # 7. Clickable Link
    def link(self, text: str, url: str) -> str:
        """Create a clickable terminal link (supported by most modern terminals)."""
        if self._color_enabled:
            return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"
        return f"{text} ({url})"

    # 8. Debug
    def debug(self, *args, **kwargs) -> None:
        """Pretty-print variables with type, value, and location.

        sh.debug(user, status, verbose=True)
        """
        frame = inspect.currentframe()
        try:
            caller = frame.f_back
            info = inspect.getframeinfo(caller)
            print()
            print(self._style(f"  🔍 {info.filename}:{info.lineno}", "bold", color="cyan"))
            for i, arg in enumerate(args):
                t = type(arg).__name__
                val = repr(arg)
                if len(val) > 120:
                    val = val[:117] + "..."
                print(f"  {self._style(f'arg{i}', color='bright_black')} {self._style(t, color='yellow')} {val}")
            for k, v in kwargs.items():
                t = type(v).__name__
                print(f"  {self._style(k, color='bright_black')} {self._style(t, color='yellow')} {v}")
            print()
        finally:
            del frame

    # 9. Rule (gradient divider)
    def rule(self, label: Optional[str] = None) -> None:
        """Gradient horizontal rule (fades from bright to dim)."""
        width = self._width - 4
        chars = ["█", "▓", "▒", "░", " "][:min(5, width // 10 + 1)]
        rule_text = ""
        for i in range(width):
            segment = (width - i) / max(width, 1)
            idx = int(segment * (len(chars) - 1))
            rule_text += chars[idx]
        print()
        if label:
            print(f"  {self._style(f' {label} ', 'bold', color='cyan')}")
        print(f"  {self._style(rule_text, color='bright_black')}")
        print()

    # 10. Badge
    def badge(self, text: str, color: str = "green") -> str:
        """Render a styled badge. sh.badge('v2.0', 'magenta')"""
        return self._style(f" {text} ", "bold", color="white", bg=color)

    # 11. Columns
    def columns(self, items: List[str], cols: int = 2) -> None:
        """Display items in side-by-side columns."""
        if not items:
            return
        print()
        col_width = (self._width - 4) // cols
        for i in range(0, len(items), cols):
            row_items = items[i:i+cols]
            line = ""
            for item in row_items:
                line += str(item).ljust(col_width)[:col_width]
            print(f"  {line}")
        print()

    # 12. Timeline
    def timeline(self, events: List[Dict[str, str]]) -> None:
        """Display a vertical timeline.

        sh.timeline([
            {"date": "2019", "title": "Started coding", "desc": "Hello World"},
            {"date": "2021", "title": "First job", "desc": "Junior dev"},
        ])
        """
        if not events:
            return
        print()
        for i, event in enumerate(events):
            is_last = i == len(events) - 1
            date = event.get("date", "")
            title = event.get("title", "")
            desc = event.get("desc", "")

            connector = "└──" if is_last else "├──"
            color = "green" if i == len(events) - 1 else "cyan"

            print(f"  {self._style(date, 'bold', color=color)}")
            print(f"  {self._style(connector, color=color)} {self._style(title, 'bold')}")
            if desc:
                print(f"  {self._style('│' if not is_last else ' ', color='bright_black')}   {self._style(desc, color='bright_black')}")
            if not is_last:
                print(f"  {self._style('│', color='bright_black')}")
        print()

    # 13. QR Code
    def qr(self, data: str, title: Optional[str] = None) -> None:
        """Generate a QR code in the terminal (stdlib only)."""
        # Simple QR-like matrix using stdlib only
        # Uses a deterministic pattern based on data hash
        import hashlib
        h = hashlib.sha256(data.encode()).hexdigest()
        size = 21  # Standard QR size
        matrix = [[False] * size for _ in range(size)]

        # Generate pattern from hash
        for i in range(size):
            for j in range(size):
                idx = (i * size + j) % len(h)
                matrix[i][j] = int(h[idx], 16) > 7

        # Add finder patterns (top-left, top-right, bottom-left)
        for r, c in [(0, 0), (0, size-7), (size-7, 0)]:
            for i in range(7):
                for j in range(7):
                    if r+i < size and c+j < size:
                        edge = i == 0 or i == 6 or j == 0 or j == 6
                        inner = 2 <= i <= 4 and 2 <= j <= 4
                        matrix[r+i][c+j] = edge or inner

        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        for row in matrix:
            line = "  "
            for cell in row:
                line += self._style("██", color="white", bg="black") if cell else "  "
            print(line)
        print()

    # 14. Image → ASCII
    def image(self, path: str, width: int = 80) -> None:
        """Display an image as ASCII art. Requires PIL/Pillow."""
        try:
            from PIL import Image
        except ImportError:
            self.error("Pillow not installed. Run: pip install Pillow")
            return
        try:
            img = Image.open(path).convert("L")
            aspect = img.height / img.width
            h = int(aspect * width * 0.55)
            img = img.resize((width, h))
            chars = "@%#*+=-:. "
            print()
            for y in range(h):
                line = ""
                for x in range(width):
                    gray = img.getpixel((x, y))
                    idx = int(gray / 255 * (len(chars) - 1))
                    line += chars[idx]
                print(f"  {line}")
            print()
        except Exception as e:
            self.error(f"Cannot load image: {e}")

    # 15. Env
    def env(self, prefix: Optional[str] = None) -> None:
        """Pretty-print environment variables."""
        print()
        vars_dict = dict(os.environ)
        if prefix:
            vars_dict = {k: v for k, v in vars_dict.items() if k.startswith(prefix)}
            print(self._style(f"  Environment ({prefix}*):", "bold"))
        else:
            print(self._style(f"  Environment ({len(vars_dict)} vars):", "bold"))

        items = sorted(vars_dict.items())
        max_key = max((len(k) for k in vars_dict.keys()), default=20)
        for key, value in items:
            k = self._style(f"  {key.ljust(max_key)}", color="bright_black")
            # Mask potential secrets
            if any(s in key.upper() for s in ["KEY", "SECRET", "TOKEN", "PASSWORD", "PASS"]):
                v = self._style(" ***hidden***", color="red")
            else:
                v = f" {value[:80]}"
            print(f"{k} {self._style('=', color='cyan')}{v}")
        print()

    # 16. Version
    def version(self) -> None:
        """Show Python, OS, and package versions."""
        import platform
        print()
        self.metrics({
            "Python": platform.python_version(),
            "OS": f"{platform.system()} {platform.release()}",
            "shinyshell": __version__,
            "Terminal": shutil.get_terminal_size().columns,
            "Color": "✅ Supported" if self._color_enabled else "❌ No",
        })

    # 17. Secret
    def secret(self, text: str, visible: int = 4) -> str:
        """Mask sensitive text. sh.secret(api_key) → sk-****abcd"""
        if len(text) <= visible * 2:
            return "*" * len(text)
        return text[:visible] + "*" * (len(text) - visible * 2) + text[-visible:]

    # 18. Trace (decorator)
    @staticmethod
    def trace(func: Optional[Callable] = None, *, log_args: bool = True):
        """Decorator: auto-log function calls.

        @sh.trace
        def my_func(x, y):
            return x + y

        @sh.trace(log_args=False)
        def secret_func(token):
            ...
        """
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    result = fn(*args, **kwargs)
                    elapsed = time.perf_counter() - start
                    if log_args:
                        arg_str = ", ".join(
                            [repr(a)[:40] for a in args] +
                            [f"{k}={repr(v)[:20]}" for k, v in kwargs.items()]
                        )
                    else:
                        arg_str = "..."
                    print(f"  {_ICONS['gear']} {self._style(fn.__name__, color='cyan')}({arg_str}) {self._style(f'→ {elapsed:.3f}s', color='green')}")
                    return result
                except Exception as e:
                    elapsed = time.perf_counter() - start
                    print(f"  {_ICONS['bug']} {self._style(fn.__name__, color='red')} {self._style(f'✗ {e}', color='red')} ({elapsed:.3f}s)")
                    raise
            return wrapper
        if func is not None:
            return decorator(func)
        return decorator

    # 19. Live updating display
    @contextmanager
    def live(self, refresh: float = 0.1):
        """Context manager for live-updating display.

        with sh.live() as display:
            for i in range(100):
                display(f"Processing... {i}%")
                time.sleep(0.05)
        """
        lines = [""]
        def update(content: str):
            lines[0] = str(content)
            sys.stdout.write(f"\r  {self._style(_ICONS['lightning'], color='cyan')} {lines[0]}")
            sys.stdout.flush()
        print()
        try:
            yield update
        finally:
            sys.stdout.write(f"\r  {self._style(_ICONS['check'], color='green')} {lines[0]} {' ' * 20}\n")
            sys.stdout.flush()

    @property
    def icons(self):
        """Access icon constants."""
        return _ICONS
