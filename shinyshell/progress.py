"""Progress, spinner, timer, benchmark, countdown, live, steps methods."""

import time as _time
import sys as _sys
from contextlib import contextmanager

from .icons import _ICONS


class _ProgressMixin:
    """Progress indicators and timers."""

    def spinner(self, message: str, duration: float = 3.0) -> None:
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        start = _time.time()
        i = 0
        print()
        try:
            while _time.time() - start < duration:
                frame = self._style(frames[i % len(frames)], color="cyan")
                _sys.stdout.write(f"\r  {frame} {message}")
                _sys.stdout.flush()
                _time.sleep(0.08)
                i += 1
            _sys.stdout.write(f"\r  {self._style(_ICONS['check'], color='green')} {message} {self._style('Done!', color='green')}\n")
        except KeyboardInterrupt:
            _sys.stdout.write(f"\r  {self._style(_ICONS['cross'], color='red')} {message} Cancelled\n")

    def progress(self, message: str = "Working"):
        def update(current: int, total: int):
            percent = int((current / max(total, 1)) * 100)
            bar_width = 30
            filled = int(bar_width * current / max(total, 1))
            bar = "█" * filled + "░" * (bar_width - filled)
            pct = f"{percent:3d}%"
            _sys.stdout.write(f"\r  {message} {self._style(bar, color='cyan')} {pct}")
            _sys.stdout.flush()
            if current >= total:
                print()
        return update

    def countdown(self, seconds: int, message: str = "Starting in") -> None:
        for i in range(seconds, 0, -1):
            _sys.stdout.write(f"\r  {self._style(_ICONS['clock'], color='yellow')} {message} {self._style(str(i), 'bold', color='yellow')}...")
            _sys.stdout.flush()
            _time.sleep(1)
        print(f"\r  {self._style(_ICONS['rocket'], color='green')} {self._style('Go!', 'bold', color='green')}      ")

    @contextmanager
    def benchmark(self, label: str = "Operation"):
        start = _time.perf_counter()
        print()
        _sys.stdout.write(f"  {self._style(_ICONS['clock'], color='cyan')} {label} ...")
        _sys.stdout.flush()
        try:
            yield
        finally:
            elapsed = _time.perf_counter() - start
            if elapsed < 0.001:
                t = f"{elapsed*1_000_000:.0f}µs"
            elif elapsed < 1:
                t = f"{elapsed*1000:.0f}ms"
            elif elapsed < 60:
                t = f"{elapsed:.2f}s"
            else:
                m, s = divmod(elapsed, 60)
                t = f"{int(m)}m {s:.1f}s"
            _sys.stdout.write(f"\r  {self._style(_ICONS['check'], color='green')} {label} {self._style(t, 'bold', color='green')}\n")
            _sys.stdout.flush()

    @contextmanager
    def live(self, refresh: float = 0.1):
        lines = [""]

        def update(content: str):
            lines[0] = str(content)
            _sys.stdout.write(f"\r  {self._style(_ICONS['lightning'], color='cyan')} {lines[0]}")
            _sys.stdout.flush()
        print()
        try:
            yield update
        finally:
            _sys.stdout.write(f"\r  {self._style(_ICONS['check'], color='green')} {lines[0]} {' ' * 20}\n")
            _sys.stdout.flush()

    def steps(self, title: str, total: int, current: int = 0):
        print()
        print(self._style(f"  {_ICONS['rocket']} {title}", "bold"))
        steps_done = [current]

        def update(message: str):
            steps_done[0] += 1
            c = steps_done[0]
            for i in range(1, total + 1):
                if i <= c:
                    _sys.stdout.write(f"\r    {self._style(f'[{i}/{total}]', color='green')} {self._style('✓', color='green')} ")
                elif i == c + 1:
                    _sys.stdout.write(f"\r    {self._style(f'[{i}/{total}]', color='cyan')} {self._style('⠋', color='cyan')} {message}")
                else:
                    _sys.stdout.write(f"\r    {self._style(f'[{i}/{total}]', color='bright_black')} · ")
                _sys.stdout.flush()
                _time.sleep(0.03)
            _sys.stdout.write("\r" + " " * 60 + "\r")
            _sys.stdout.flush()
            if c >= total:
                print(f"    {self._style('All steps complete!', color='green')} {_ICONS['party']}\n")
            return update
        return update
