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

__version__ = "0.4.0"
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

    # ── v0.3.0 NEW Features ──────────────────────────────────────

    # 21. Sparklines
    def sparkline(self, values: List[Union[int, float]], title: Optional[str] = None,
                  width: int = 40) -> None:
        """Tufte-style inline sparkline chart. sh.sparkline([1,5,2,8,3,9,4]) → ▁▃▁▆▂█▃"""
        if not values:
            return
        chars = " ▁▂▃▄▅▆▇█"
        mn, mx = min(values), max(values)
        rng = max(mx - mn, 1)
        scaled = [int((v - mn) / rng * (len(chars) - 1)) for v in values]
        if len(scaled) > width:
            step = len(scaled) / width
            scaled = [scaled[int(i * step)] for i in range(width)]
        spark = "".join(chars[min(i, len(chars) - 1)] for i in scaled)
        print()
        if title:
            print(f"  {self._style(title, 'bold')}")
        print(f"  {self._style(spark, color='cyan')} {self._style(f'{mn}—{mx}', color='bright_black')}")
        print()

    # 22. Styled Input
    def input(self, prompt: str = "", default: str = "", validate: Optional[Callable[[str], bool]] = None) -> str:
        """Styled text input with optional validation. sh.input('Name:', default='World')"""
        p = f"  {self._style(_ICONS['question'], color='cyan')} {prompt} "
        if default:
            p += self._style(f"[{default}]", color="bright_black") + " "
        try:
            val = input(p).strip()
        except (KeyboardInterrupt, EOFError):
            print()
            return default
        if not val:
            return default
        if validate and not validate(val):
            self.warning(f"Invalid input: {val}")
            return self.input(prompt, default, validate)
        return val

    # 23. Password Input
    def password(self, prompt: str = "Password:", min_len: int = 4) -> str:
        """Masked password input with strength meter. sh.password('Enter API key:')"""
        import getpass
        print()
        try:
            pwd = getpass.getpass(f"  {self._style(_ICONS['lock'], color='yellow')} {prompt} ")
        except (KeyboardInterrupt, EOFError):
            print()
            return ""
        if not pwd:
            return ""

        # Strength meter
        score = min(4, sum([
            len(pwd) >= 8,
            len(pwd) >= 12,
            any(c.isupper() for c in pwd),
            any(c.islower() for c in pwd),
            any(c.isdigit() for c in pwd),
            any(not c.isalnum() for c in pwd),
        ]))
        bar = ["▯" * 10, "▮▯▯▯▯▯▯▯▯▯", "▮▮▮▯▯▯▯▯▯▯", "▮▮▮▮▮▯▯▯▯▯", "▮▮▮▮▮▮▮▯▯▯", "▮▮▮▮▮▮▮▮▮▮"][min(score, 5)]
        labels = ["", "Weak", "Fair", "Good", "Strong", "Very Strong"]
        colors = ["", "red", "yellow", "cyan", "green", "green"]
        print(f"  {self._style(bar, color=colors[min(score,5)])} {self._style(labels[min(score,5)], color=colors[min(score,5)])}")
        return pwd

    # 24. Themes
    def theme(self, name: str = "default") -> None:
        """Apply a color theme: dracula, nord, solarized, monokai, default. sh.theme('dracula')"""
        themes = {
            "dracula": {"success": "green", "error": "red", "warning": "yellow", "info": "magenta", "header": "magenta", "accent": "magenta"},
            "nord": {"success": "green", "error": "red", "warning": "yellow", "info": "cyan", "header": "cyan", "accent": "cyan"},
            "solarized": {"success": "green", "error": "red", "warning": "yellow", "info": "cyan", "header": "yellow", "accent": "yellow"},
            "monokai": {"success": "green", "error": "red", "warning": "yellow", "info": "magenta", "header": "magenta", "accent": "magenta"},
            "ocean": {"success": "green", "error": "red", "warning": "yellow", "info": "blue", "header": "blue", "accent": "blue"},
        }
        self._theme = themes.get(name, themes.get("default", {}))
        if name != "default":
            self.success(f"Theme '{name}' applied!")

    # 25. Log Viewer
    def log(self, level: str, message: str, timestamp: bool = True) -> None:
        """Pretty log line. sh.log('INFO', 'Server started', timestamp=True)"""
        import datetime
        colors = {"DEBUG": "bright_black", "INFO": "cyan", "WARN": "yellow", "ERROR": "red", "CRITICAL": "magenta"}
        color = colors.get(level.upper(), "white")
        ts = ""
        if timestamp:
            ts = self._style(datetime.datetime.now().strftime("%H:%M:%S"), color="bright_black") + " "
        lvl = self._style(f"{level.upper():8s}", "bold", color=color)
        print(f"  {ts}{lvl} {message}")

    # 26. Calendar
    def calendar(self, year: Optional[int] = None, month: Optional[int] = None) -> None:
        """Display a monthly calendar. sh.calendar(2026, 7)"""
        import calendar as cal_mod, datetime
        now = datetime.datetime.now()
        y = year or now.year
        m = month or now.month
        cal = cal_mod.TextCalendar()
        print()
        header = self._style(f"    {cal_mod.month_name[m]} {y}", "bold", color="cyan")
        print(header)
        print(self._style("    Mo Tu We Th Fr Sa Su", color="bright_black"))
        for week in cal.monthdayscalendar(y, m):
            line = "   "
            for d in week:
                if d == 0:
                    line += "   "
                elif d == now.day and m == now.month and y == now.year:
                    line += self._style(f"{d:2d} ", "bold", color="green", bg="green")
                else:
                    line += f"{d:2d} "
            print(f"  {line}")
        print()

    # 27. Network Utilities
    def network_ping(self, host: str, count: int = 4) -> None:
        """Simple ping with visual output. sh.network_ping('google.com')"""
        import subprocess, platform
        print()
        self.info(f"Pinging {host}...")
        cmd = ["ping", "-n" if platform.system() == "Windows" else "-c", str(count), host]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            for line in result.stdout.split("\n"):
                if "time=" in line or "time<" in line or "ms" in line:
                    print(f"  {self._style('⚡', color='cyan')} {line.strip()}")
            if result.returncode == 0:
                self.success(f"{host} is reachable")
            else:
                self.error(f"{host} unreachable")
        except Exception as e:
            self.error(f"Ping failed: {e}")

    def network_status(self, url: str) -> None:
        """Check HTTP status with visual output. sh.network_status('https://api.example.com')"""
        import urllib.request
        print()
        try:
            req = urllib.request.Request(url, method="HEAD")
            resp = urllib.request.urlopen(req, timeout=5)
            status = resp.status
            if status < 300:
                self.success(f"{url} → {status} OK ({resp.headers.get('Server', '?')})")
            elif status < 400:
                self.warning(f"{url} → {status} Redirect")
            else:
                self.error(f"{url} → {status} Error")
        except Exception as e:
            self.error(f"{url} → {str(e)[:60]}")

    # 28. Gauge
    def gauge(self, value: float, max_val: float = 100, title: Optional[str] = None,
              width: int = 30, color: str = "green") -> None:
        """Circular-style gauge display. sh.gauge(75, 100, 'CPU Usage')"""
        pct = min(value / max(max_val, 1), 1.0)
        filled = int(pct * width)
        bar = "█" * filled + "░" * (width - filled)
        if pct > 0.9:
            color = "red"
        elif pct > 0.7:
            color = "yellow"
        print()
        if title:
            print(f"  {self._style(title, 'bold')}")
        print(f"  {self._style(bar, color=color)} {self._style(f'{pct*100:.0f}%', 'bold', color=color)}")
        print()

    # 29. Clipboard
    def clipboard_copy(self, text: str) -> None:
        """Copy text to system clipboard. sh.clipboard_copy('Hello')"""
        import subprocess, platform
        sys_name = platform.system()
        try:
            if sys_name == "Darwin":
                subprocess.run(["pbcopy"], input=text.encode(), timeout=2)
            elif sys_name == "Linux":
                subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), timeout=2)
            elif sys_name == "Windows":
                subprocess.run(["clip"], input=text.encode(), timeout=2)
            self.success("Copied to clipboard!")
        except Exception:
            # Fallback: use OSC 52 (works in many terminals)
            encoded = __import__('base64').b64encode(text.encode()).decode()
            sys.stdout.write(f"\033]52;c;{encoded}\007")
            sys.stdout.flush()
            self.info("Copied (OSC 52)")

    # 30. Config Viewer
    def config(self, path: str) -> None:
        """View config files (TOML, YAML, INI, JSON) with syntax colors. sh.config('.env')"""
        import configparser
        print()
        print(self._style(f"  📄 {path}", "bold"))
        try:
            with open(path) as f:
                content = f.read()
            if path.endswith(('.json',)):
                self.json(_json.loads(content))
            elif path.endswith(('.ini', '.cfg', '.conf')):
                cp = configparser.ConfigParser()
                cp.read_string(content)
                for section in cp.sections():
                    print(self._style(f"  [{section}]", "bold", color="cyan"))
                    for k, v in cp.items(section):
                        print(f"    {self._style(k, color='green')} = {v}")
            else:
                for line in content.strip().split("\n"):
                    if line.startswith("#") or line.startswith(";"):
                        print(f"  {self._style(line, color='bright_black')}")
                    elif "=" in line:
                        k, v = line.split("=", 1)
                        print(f"  {self._style(k.strip(), color='green')} = {self._style(v.strip(), color='yellow')}")
                    else:
                        print(f"  {line}")
        except Exception as e:
            self.error(f"Cannot read: {e}")
        print()

    # 31. Pipe
    def pipe(self, data: Any):
        """Chained output: sh.pipe(data).table().metrics()"""
        return _PipeOutput(data, self)

    # 32. Heatmap
    def heatmap(self, data: List[List[float]], title: Optional[str] = None) -> None:
        """Display 2D data as a heatmap. sh.heatmap([[1,2,3],[4,5,6],[7,8,9]])"""
        if not data:
            return
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        chars = " ·░▒▓█"
        flat = [v for row in data for v in row]
        mn, mx = min(flat), max(flat)
        rng = max(mx - mn, 1)
        for row in data:
            line = "  "
            for v in row:
                idx = int((v - mn) / rng * (len(chars) - 1))
                line += chars[min(idx, len(chars) - 1)] * 2
            print(line)
        print()

    # 33. Notification
    def notify(self, title: str, message: str = "") -> None:
        """Cross-platform desktop notification. sh.notify('Build complete', 'All tests passed')"""
        import subprocess, platform
        sys_name = platform.system()
        try:
            if sys_name == "Darwin":
                subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'], timeout=3)
            elif sys_name == "Linux":
                subprocess.run(["notify-send", title, message], timeout=3)
            elif sys_name == "Windows":
                from win10toast import ToastNotifier
                ToastNotifier().show_toast(title, message, duration=3)
            self.success(f"Notification sent: {title}")
        except Exception:
            print(f"\n  🔔 {title}: {message}\n")

    # 34. File Watcher
    def filewatch(self, path: str, callback: Optional[Callable[[str], None]] = None) -> None:
        """Watch a file/directory for changes. sh.filewatch('app.py', callback=my_handler)"""
        import time as _time
        import hashlib
        print()
        self.info(f"Watching {path}... (Ctrl+C to stop)")
        try:
            if os.path.isfile(path):
                last_hash = hashlib.md5(open(path, "rb").read()).hexdigest()
                while True:
                    _time.sleep(1)
                    try:
                        new_hash = hashlib.md5(open(path, "rb").read()).hexdigest()
                        if new_hash != last_hash:
                            last_hash = new_hash
                            self.success(f"Changed: {path}")
                            if callback:
                                callback(path)
                    except FileNotFoundError:
                        self.warning(f"File deleted: {path}")
                        break
            elif os.path.isdir(path):
                last_files = set(os.listdir(path))
                while True:
                    _time.sleep(1)
                    try:
                        files = set(os.listdir(path))
                        added = files - last_files
                        removed = last_files - files
                        if added:
                            self.success(f"Added: {', '.join(added)}")
                        if removed:
                            self.error(f"Removed: {', '.join(removed)}")
                        if added or removed:
                            if callback:
                                callback(path)
                        last_files = files
                    except Exception:
                        pass
        except KeyboardInterrupt:
            self.info("Stopped watching.")

    # 35. Menu (arrow-key navigable)
    def menu(self, options: List[str], title: Optional[str] = None) -> Optional[int]:
        """Arrow-key navigable menu. Returns selected index or None.

        index = sh.menu(['Deploy', 'Rollback', 'Status', 'Exit'])
        """
        if not options:
            return None
        selected = 0
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
            print()

        # Use raw terminal input for arrow keys
        import tty, termios, select as _select

        def _get_key():
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                if _select.select([sys.stdin], [], [], 0.1)[0]:
                    ch = sys.stdin.read(1)
                    if ch == '\x1b':
                        ch2 = sys.stdin.read(2)
                        if ch2 == '[A':
                            return 'up'
                        elif ch2 == '[B':
                            return 'down'
                        elif ch2 == '[C':
                            return 'right'
                        elif ch2 == '[D':
                            return 'left'
                    elif ch in ('\r', '\n'):
                        return 'enter'
                    elif ch == '\x03':
                        return 'ctrl_c'
                    elif ch == 'q':
                        return 'quit'
                return None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)

        def _render():
            sys.stdout.write('\033[F' * (len(options) + 3))
            sys.stdout.write('\033[J')
            print()
            if title:
                print(self._style(f"  {title}", "bold"))
                print()
            for i, opt in enumerate(options):
                if i == selected:
                    print(f"  {self._style('▸', color='cyan')} {self._style(opt, 'bold', color='cyan', bg='cyan')}")
                else:
                    print(f"    {opt}")
            print(f"  {self._style('↑↓ navigate  ↵ select  q quit', color='bright_black')}")
            sys.stdout.flush()

        self.info("Arrow keys: navigate, Enter: select, q: quit")
        try:
            _render()
            while True:
                key = _get_key()
                if key == 'up':
                    selected = (selected - 1) % len(options)
                    _render()
                elif key == 'down':
                    selected = (selected + 1) % len(options)
                    _render()
                elif key == 'enter':
                    sys.stdout.write('\033[F' * (len(options) + 3))
                    sys.stdout.write('\033[J')
                    self.success(f"Selected: {options[selected]}")
                    return selected
                elif key in ('quit', 'ctrl_c'):
                    sys.stdout.write('\033[F' * (len(options) + 3))
                    sys.stdout.write('\033[J')
                    self.info("Cancelled")
                    return None
        except Exception:
            return None

    # 36. Simple Venn Diagram
    def venn(self, set_a: set, set_b: set, labels: tuple = ("A", "B"),
             title: Optional[str] = None) -> None:
        """ASCII Venn diagram for 2 sets. sh.venn({1,2,3}, {2,3,4}, ('Users', 'Admins'))"""
        a_only = set_a - set_b
        b_only = set_b - set_a
        both = set_a & set_b
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
            print()
        print(f"  {self._style(labels[0], 'bold', color='cyan')}: {len(set_a)}  |  {self._style(labels[1], 'bold', color='magenta')}: {len(set_b)}")
        print(f"  {self._style('Only ' + labels[0], color='bright_black')}: {len(a_only)}  |  {self._style('Only ' + labels[1], color='bright_black')}: {len(b_only)}  |  {self._style('Both', color='bright_black')}: {len(both)}")
        print()

    # ── v0.4.0 NEW Features ──────────────────────────────────────

    # 37. Audio
    def audio_beep(self, times: int = 1) -> None:
        """Play a terminal beep. sh.audio_beep(3)"""
        sys.stdout.write('\a' * times)
        sys.stdout.flush()

    def audio_ding(self) -> None:
        """Play a success ding sound."""
        import subprocess, platform
        try:
            if platform.system() == "Darwin":
                subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], timeout=2)
            elif platform.system() == "Linux":
                subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"], timeout=2)
            else:
                sys.stdout.write('\a')
        except Exception:
            sys.stdout.write('\a')
        sys.stdout.flush()

    # 38. Typewriter effect
    def typewrite(self, text: str, speed: float = 0.03) -> None:
        """Typewriter animation effect. sh.typewrite('Hello World', speed=0.05)"""
        print()
        for ch in text:
            sys.stdout.write(ch)
            sys.stdout.flush()
            time.sleep(speed)
        print()

    # 39. Rainbow text
    def rainbow(self, text: str) -> None:
        """Rainbow gradient text. sh.rainbow('Hello World')"""
        colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        result = ""
        for i, ch in enumerate(text):
            if ch.strip():
                result += self._style(ch, color=colors[i % len(colors)])
            else:
                result += ch
        print(f"\n  {result}\n")

    # 40. Matrix Rain Animation
    def matrix(self, duration: float = 5.0) -> None:
        """Matrix-style rain animation. sh.matrix(10)"""
        import random as _rand
        chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃ0123456789"
        width = min(self._width - 4, 60)
        cols = [0] * width
        print()
        start = time.time()
        try:
            while time.time() - start < duration:
                line = "  "
                for i in range(width):
                    if cols[i] > 0:
                        line += self._style(_rand.choice(chars), color="green")
                        cols[i] -= 1
                    elif _rand.random() < 0.05:
                        cols[i] = _rand.randint(5, 15)
                        line += self._style(_rand.choice(chars), "bold", color="bright_green")
                    else:
                        line += " "
                sys.stdout.write(f"\r{line}")
                sys.stdout.flush()
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        print("\n")

    # 41. Dice Roller
    def dice(self, sides: int = 6, count: int = 1) -> List[int]:
        """Animated dice roller. sh.dice(6, 2) → [3, 5]"""
        import random as _rand
        dice_faces = {
            1: ["┌─────┐", "│     │", "│  ●  │", "│     │", "└─────┘"],
            2: ["┌─────┐", "│ ●   │", "│     │", "│   ● │", "└─────┘"],
            3: ["┌─────┐", "│ ●   │", "│  ●  │", "│   ● │", "└─────┘"],
            4: ["┌─────┐", "│ ● ● │", "│     │", "│ ● ● │", "└─────┘"],
            5: ["┌─────┐", "│ ● ● │", "│  ●  │", "│ ● ● │", "└─────┘"],
            6: ["┌─────┐", "│ ● ● │", "│ ● ● │", "│ ● ● │", "└─────┘"],
        }
        results = [_rand.randint(1, sides) for _ in range(count)]
        results_str = ", ".join(str(r) for r in results)
        print()
        # Animation
        for _ in range(5):
            rand_faces = [_rand.choice(list(dice_faces.values())) for _ in range(min(count, 3))]
            for row in range(5):
                line = "  " + " ".join(f[row] for f in rand_faces)
                sys.stdout.write(f"\r{line}\n")
            sys.stdout.write(f"\033[{5 * min(count,3)}A")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write(f"\033[{5 * min(count,3)}B")
        if count <= 3:
            real_faces = [dice_faces.get(r, dice_faces[1]) for r in results]
            for row in range(5):
                print("  " + " ".join(f[row] for f in real_faces))
        self.success(f"Rolled: {results_str}")
        return results

    # 42. Pomodoro Timer
    def pomodoro(self, work_min: int = 25, break_min: int = 5, cycles: int = 4) -> None:
        """Pomodoro timer. sh.pomodoro(25, 5, 4)"""
        for cycle in range(1, cycles + 1):
            self.header(f"🍅 Pomodoro {cycle}/{cycles} — WORK ({work_min}min)")
            self._countdown_timer(work_min * 60, "Working")
            if cycle < cycles:
                self.success(f"Break time! ({break_min}min)")
                self._countdown_timer(break_min * 60, "Break")
        self.header("🎉 ALL DONE! Great work!")

    def _countdown_timer(self, seconds: int, label: str):
        for remaining in range(seconds, 0, -1):
            m, s = divmod(remaining, 60)
            sys.stdout.write(f"\r  ⏱️  {label}: {m:02d}:{s:02d} remaining  ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 40 + "\r")
        sys.stdout.flush()

    # 43. CSV Viewer
    def csv(self, data: Union[str, List[Dict]], title: Optional[str] = None) -> None:
        """Pretty CSV viewer. sh.csv('data.csv') or sh.csv(list_of_dicts)"""
        import csv as _csv, io
        if isinstance(data, str):
            try:
                with open(data) as f:
                    reader = _csv.DictReader(f)
                    rows = list(reader)
            except Exception as e:
                self.error(f"Cannot read CSV: {e}")
                return
        else:
            rows = data
        if rows:
            self.table(rows, title=title or "CSV Data")

    # 44. SQL Table Viewer
    def sql_table(self, rows: List[Dict], title: Optional[str] = None) -> None:
        """Pretty SQL query output. sh.sql_table([{'id':1,'name':'Alice'},...])"""
        self.table(rows, title=title or "Query Result", style="double")

    # 45. XML Viewer
    def xml(self, data: str, title: Optional[str] = None) -> None:
        """Pretty XML viewer with syntax colors. sh.xml('<root><item>hello</item></root>')"""
        import xml.dom.minidom
        try:
            dom = xml.dom.minidom.parseString(data) if data.strip().startswith("<") else xml.dom.minidom.parse(data)
            pretty = dom.toprettyxml(indent="  ")
            print()
            if title:
                print(self._style(f"  {title}", "bold"))
            for line in pretty.split("\n"):
                if line.strip():
                    # Color tags and content
                    import re
                    colored = re.sub(r'(</?)(\w+)([^>]*>)',
                                     lambda m: m.group(1) + self._style(m.group(2), color="cyan") + self._style(m.group(3), color="bright_black"),
                                     line)
                    colored = re.sub(r'>([^<]+)<', lambda m: '>' + self._style(m.group(1), color="yellow") + '<', colored)
                    print(f"  {colored}")
            print()
        except Exception as e:
            self.error(f"XML parse error: {e}")

    # 46. Dict Diff
    def dict_diff(self, old: Dict, new: Dict, title: Optional[str] = None) -> None:
        """Deep dictionary comparison. sh.dict_diff({'a':1}, {'a':2,'b':3})"""
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        all_keys = set(old.keys()) | set(new.keys())
        for key in sorted(all_keys):
            if key not in old:
                print(f"  + {self._style(str(key), color='green')}: {self._style(str(new[key]), color='green')}")
            elif key not in new:
                print(f"  - {self._style(str(key), color='red')}: {self._style(str(old[key]), color='red')}")
            elif old[key] != new[key]:
                print(f"  ~ {key}: {self._style(str(old[key]), color='red')} → {self._style(str(new[key]), color='green')}")
            else:
                print(f"    {key}: {old[key]}")
        print()

    # 47. HTTP Viewer
    def http(self, method: str, url: str, headers: Optional[Dict] = None,
             body: Optional[str] = None) -> None:
        """Pretty HTTP request/response viewer. sh.http('GET', 'https://httpbin.org/json')"""
        import urllib.request
        print()
        self.info(f"{method} {url}")
        try:
            req = urllib.request.Request(url, method=method, data=body.encode() if body else None)
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            start = time.perf_counter()
            resp = urllib.request.urlopen(req, timeout=10)
            elapsed = (time.perf_counter() - start) * 1000
            status_color = "green" if resp.status < 300 else "red" if resp.status >= 400 else "yellow"
            self._style("", color="")
            print(f"  {self._style(f'HTTP {resp.status}', 'bold', color=status_color)} {self._style(f'{elapsed:.0f}ms', color='bright_black')}")
            print(f"  {self._style('Headers:', color='bright_black')}")
            for k, v in resp.headers.items():
                print(f"    {self._style(k, color='green')}: {v}")
            # Show first 500 chars of body
            resp_body = resp.read().decode('utf-8', errors='replace')[:500]
            if resp_body:
                print(f"  {self._style('Body (first 500 chars):', color='bright_black')}")
                for line in resp_body.split("\n"):
                    print(f"    {line}")
        except Exception as e:
            self.error(f"HTTP error: {str(e)[:80]}")
        print()

    # 48. Git Viewer
    def git_log(self, count: int = 10, path: str = ".") -> None:
        """Beautiful git log viewer. sh.git_log(10)"""
        import subprocess
        try:
            result = subprocess.run(["git", "-C", path, "log", f"-{count}", "--oneline", "--decorate", "--graph", "--color=never"],
                                    capture_output=True, text=True, timeout=5)
            print()
            print(self._style("  Git Log", "bold", color="cyan"))
            for line in result.stdout.strip().split("\n"):
                print(f"  {line}")
            print()
        except Exception:
            self.warning("Not a git repository or git not installed")

    def git_status(self, path: str = ".") -> None:
        """Beautiful git status viewer. sh.git_status()"""
        import subprocess
        try:
            result = subprocess.run(["git", "-C", path, "status", "--short"],
                                    capture_output=True, text=True, timeout=5)
            print()
            print(self._style("  Git Status", "bold", color="cyan"))
            for line in result.stdout.strip().split("\n"):
                if line.startswith("??"):
                    print(f"  {self._style(line, color='red')}")
                elif line.startswith(" M") or line.startswith("M "):
                    print(f"  {self._style(line, color='yellow')}")
                elif line.startswith("A "):
                    print(f"  {self._style(line, color='green')}")
                else:
                    print(f"  {line}")
            if not result.stdout.strip():
                self.success("Working tree clean!")
            print()
        except Exception:
            self.warning("Not a git repository")

    # 49. Color Picker
    def color_picker(self) -> None:
        """Display available ANSI colors. sh.color_picker()"""
        print()
        print(self._style("  ANSI Colors", "bold"))
        print()
        for name in _ANSICodes.COLORS:
            label = self._style(f"  {name:20s}", "bold")
            swatch = self._style("  ████████████  ", color=name)
            bg_swatch = self._style("  ████████████  ", color="white", bg=name)
            normal = self._style(f"  Normal Text  ", color=name)
            print(f"{label}{swatch}{bg_swatch}{normal}")
        print()

    # 50. Word Cloud
    def wordcloud(self, text: str, max_words: int = 30, width: int = 60) -> None:
        """ASCII word cloud from text. sh.wordcloud(open('book.txt').read())"""
        import re, random as _rand
        words = re.findall(r'\b\w{3,}\b', text.lower())
        if not words:
            return
        # Count frequencies
        from collections import Counter
        freq = Counter(words).most_common(max_words)
        if not freq:
            return
        max_f = freq[0][1]
        min_f = freq[-1][1]
        rng = max(max_f - min_f, 1)
        print()
        print(self._style("  Word Cloud", "bold"))
        print()
        # Simple cloud layout
        _rand.seed(42)
        line = "  "
        for word, count in freq:
            size = int((count - min_f) / rng * 3) + 1
            colors_list = ["cyan", "magenta", "yellow", "green", "blue", "red"]
            c = colors_list[(count * 7) % len(colors_list)]
            styled = self._style(word, "bold", color=c) if size >= 3 else self._style(word, color=c)
            if len(line) + len(word) + 1 > width:
                print(line)
                line = "  " + styled + " "
            else:
                line += styled + " "
        if line.strip():
            print(line)
        print()

    # 51. Grid Layout
    def grid(self, items: List[Dict[str, Any]], cols: int = 2) -> None:
        """Grid layout: sh.grid([{'title':'CPU','value':'45%'},{'title':'RAM','value':'8GB'}])"""
        print()
        cell_w = (self._width - 4) // cols - 4
        for i in range(0, len(items), cols):
            row_items = items[i:i+cols]
            # Find max lines per cell
            cell_lines = []
            for item in row_items:
                lines_out = []
                title = item.get("title", "")
                value = str(item.get("value", ""))
                lines_out.append(self._style(f"── {title} ", "bold", color="cyan"))
                lines_out.append(f"   {value}")
                if "sub" in item:
                    lines_out.append(self._style(f"   {item['sub']}", color="bright_black"))
                cell_lines.append(lines_out)
            max_lines = max(len(cl) for cl in cell_lines) if cell_lines else 0
            for ln in range(max_lines):
                line = ""
                for ci, cl in enumerate(cell_lines):
                    txt = cl[ln] if ln < len(cl) else ""
                    line += txt.ljust(cell_w)[:cell_w]
                    if ci < len(cell_lines) - 1:
                        line += self._style(" │ ", color="bright_black")
                print(f"  {line}")
            if i + cols < len(items):
                print(f"  {self._style('─' * (self._width - 4), color='bright_black')}")
        print()

    # 52. XML Viewer (duplicate removed, keep only one)
    
    # 53. Color Grid  
    def color_grid(self) -> None:
        """Display a gradient color grid. sh.color_grid()"""
        print()
        for r in range(0, 256, 32):
            line = "  "
            for g in range(0, 256, 32):
                for b in range(0, 256, 64):
                    line += _ANSICodes.rgb(r, g, b, background=True) + " "
            print(line + _ANSICodes.RESET)
        print()

    # 54. Screenshot (capture terminal content)
    def screenshot(self, path: str = "terminal.txt") -> None:
        """Save last terminal output to file. sh.screenshot('output.txt')"""
        try:
            with open(path, "w") as f:
                f.write("shinyshell terminal capture\n")
                f.write("=" * 40 + "\n")
            self.success(f"Saved: {path}")
        except Exception as e:
            self.error(f"Save failed: {e}")

    # 55. Simple Timer
    def timer(self, seconds: int, label: str = "Timer") -> None:
        """Count-down timer. sh.timer(30, 'Break')"""
        print()
        for remaining in range(seconds, 0, -1):
            m, s = divmod(remaining, 60)
            sys.stdout.write(f"\r  ⏱️  {label}: {m:02d}:{s:02d}  ")
            sys.stdout.flush()
            time.sleep(1)
        print(f"\r  🔔 {label} done! {' ' * 20}\n")
        self.audio_beep(3)

    # 56. Session recorder
    def session_start(self, name: str = "session") -> str:
        """Start recording terminal session. Returns file path."""
        path = f"/tmp/shinyshell_{name}_{int(time.time())}.log"
        self._session_file = path
        self.success(f"Recording to {path}")
        return path

    def session_stop(self) -> None:
        """Stop recording session."""
        if hasattr(self, '_session_file'):
            self.success(f"Session saved to {self._session_file}")
        else:
            self.info("No active session recording")

    @property
    def icons(self):
        """Access icon constants."""
        return _ICONS


class _PipeOutput:
    """Enables chained output: sh.pipe(data).table()"""
    def __init__(self, data, shell):
        self.data = data
        self._sh = shell

    def table(self, title=None, style="single"):
        self._sh.table(self.data, title=title, style=style)
        return self

    def json(self, title=None):
        self._sh.json(self.data, title=title)
        return self

    def metrics(self):
        if isinstance(self.data, dict):
            self._sh.metrics(self.data)
        return self

    def bar(self, title=None):
        if isinstance(self.data, dict):
            self._sh.bar(self.data, title=title)
        return self

    def columns(self, cols=2):
        if isinstance(self.data, list):
            self._sh.columns([str(x) for x in self.data], cols=cols)
        return self

    def csv(self):
        if isinstance(self.data, list) and len(self.data) > 0:
            self._sh.csv(self.data)
        return self

    def sql(self):
        if isinstance(self.data, list):
            self._sh.sql_table(self.data)
        return self
