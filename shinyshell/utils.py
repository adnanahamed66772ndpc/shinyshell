"""Utility methods for Shell."""

import sys
import time
import functools
import re
import inspect

from .colors import _ANSICodes
from .icons import _ICONS


from contextlib import contextmanager
class _UtilsMixin:
    """Utility methods: secret, trace, retry, throttle, batch, background, link, ordinal, pluralize, camel_case, snake_case, strip_ansi, wrap_text, truncate, align_text, highlight, neon, gradient_text, sleep, color_picker, color_grid."""

    def secret(self, text: str, visible: int = 4) -> str:
        """Mask sensitive text. sh.secret(api_key) → sk-****abcd"""
        if len(text) <= visible * 2:
            return "*" * len(text)
        return text[:visible] + "*" * (len(text) - visible * 2) + text[-visible:]

    @staticmethod
    def trace(func=None, *, log_args: bool = True):
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

    def retry(self, max_attempts: int = 3, delay: float = 1.0):
        """Retry decorator. @sh.retry(3)"""
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*a, **kw):
                last_err = None
                for attempt in range(max_attempts):
                    try:
                        return fn(*a, **kw)
                    except Exception as e:
                        last_err = e
                        if attempt < max_attempts - 1:
                            time.sleep(delay * (attempt + 1))
                raise last_err
            return wrapper
        return decorator

    def throttle(self, seconds: float):
        """Rate limit decorator. @sh.throttle(1.0)"""
        last_call = [0.0]

        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*a, **kw):
                elapsed = time.time() - last_call[0]
                if elapsed < seconds:
                    time.sleep(seconds - elapsed)
                last_call[0] = time.time()
                return fn(*a, **kw)
            return wrapper
        return decorator

    def batch(self, items: list, batch_size: int = 10, callback=None) -> list:
        """Batch processor. sh.batch(items, 10, callback=process)"""
        results = []
        total = len(items)
        for i in range(0, total, batch_size):
            batch_items = items[i:i + batch_size]
            update = self.progress(f"Batch {i // batch_size + 1}/{(total - 1) // batch_size + 1}")
            if callback:
                results.extend(callback(batch_items))
            update(1, 1)
        return results

    def background(self, func):
        """Run in background thread. @sh.background"""
        import threading

        def wrapper(*a, **kw):
            t = threading.Thread(target=func, args=a, kwargs=kw, daemon=True)
            t.start()
            return t
        return wrapper

    def link(self, text: str, url: str) -> str:
        """Create a clickable terminal link (supported by most modern terminals)."""
        if self._color_enabled:
            return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"
        return f"{text} ({url})"

    def ordinal(self, n: int) -> str:
        """Ordinal suffix. sh.ordinal(42) → '42nd'"""
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10 if n % 100 not in [11, 12, 13] else 0, "th")
        return f"{n}{suffix}"

    def pluralize(self, word: str, count: int) -> str:
        """Smart plural. sh.pluralize('file', 3) → 'files'"""
        return word + ("s" if count != 1 else "")

    def camel_case(self, text: str) -> str:
        """Convert to camelCase. sh.camel_case('hello world')"""
        words = text.replace('-', ' ').replace('_', ' ').split()
        return words[0].lower() + ''.join(w.capitalize() for w in words[1:]) if words else ""

    def snake_case(self, text: str) -> str:
        """Convert to snake_case"""
        return re.sub(r'(?<!^)(?=[A-Z])', '_', text).replace(' ', '_').replace('-', '_').lower()

    def strip_ansi(self, text: str) -> str:
        """Remove ANSI codes. sh.strip_ansi('\\033[31mred')"""
        return re.sub(r'\033\[[0-9;]*m', '', text)

    def wrap_text(self, text: str, width: int = 60) -> None:
        """Word wrap. sh.wrap_text(long_text, width=50)"""
        import textwrap as _tw
        print()
        for line in _tw.wrap(text, width=width - 4):
            print(f"  {line}")
        print()

    def truncate(self, text: str, max_len: int = 80, suffix: str = "...") -> str:
        """Smart truncate. sh.truncate(text, 50)"""
        return text[:max_len - len(suffix)] + suffix if len(text) > max_len else text

    def align_text(self, text: str, width: int = 60, direction: str = "center") -> str:
        """Text alignment. sh.align_text('Hello', 40, 'center')"""
        if direction == "center":
            return text.center(width)
        elif direction == "right":
            return text.rjust(width)
        return text.ljust(width)

    def highlight(self, text: str, word: str, color: str = "yellow") -> str:
        """Keyword highlight. sh.highlight('Hello World', 'World', 'green')"""
        return text.replace(word, self._style(word, "bold", color=color, bg=color))

    def neon(self, text: str, color: str = "magenta") -> str:
        """Neon glow text. sh.neon('Hello')"""
        return self._style(f" {text} ", "bold", color=color, bg=color)

    def gradient_text(self, text: str) -> None:
        """Gradient colored text. sh.gradient_text('Hello World')"""
        colors_list = ["red", "yellow", "green", "cyan", "blue", "magenta"]
        result = ""
        for i, ch in enumerate(text):
            result += self._style(ch, color=colors_list[i % len(colors_list)])
        print(f"\n  {result}\n")

    def sleep(self, seconds: float, message: str = "Waiting") -> None:
        """Pretty sleep. sh.sleep(5, 'Cooling down')"""
        for i in range(int(seconds * 10)):
            sys.stdout.write(f"\r  💤 {message}... {i / 10:.1f}s  ")
            sys.stdout.flush()
            time.sleep(0.1)
        print()

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
