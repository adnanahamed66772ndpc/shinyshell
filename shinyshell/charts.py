"""Chart methods: pie, bar, line_chart, histogram, scatter, donut, waterfall, bullet_graph, heatmap, sparkline, gauge."""

from collections import Counter
from .icons import _ICONS


class _ChartMixin:
    """All chart and visualization methods."""

    def pie(self, data: dict[str, float], title: str | None = None, size: int = 10) -> None:
        total = sum(data.values())
        if total == 0:
            return
        chars = " ▏▎▍▌▋▊▉█"
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        for label, val in data.items():
            pct = val / total
            bar_len = int(pct * size * 8)
            full = bar_len // 8
            rem = bar_len % 8
            bar_str = "█" * full + (chars[rem] if rem else "")
            print(f"  {self._style(label, color='bright_black'):12s} {self._style(bar_str, color='cyan')} {self._style(f'{pct*100:.0f}%', 'bold')}")
        print()

    def bar(self, data: dict[str, int | float], title: str | None = None, width: int = 40, color: str = "cyan") -> None:
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

    def line_chart(self, data: list[float], title: str | None = None, height: int = 10, width: int = 40) -> None:
        if not data:
            return
        mn, mx = min(data), max(data)
        rng = max(mx - mn, 1)
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        step = max(1, len(data) // width)
        pts = [data[i * step] for i in range(min(width, len(data) // max(step, 1)))]
        for y in range(height, -1, -1):
            line = "  "
            val_at_y = mn + (rng * y / height)
            for i, v in enumerate(pts):
                if abs(v - val_at_y) < rng / height / 2:
                    line += self._style("●", color="cyan")
                elif (v > val_at_y and (i == 0 or pts[i - 1] <= val_at_y < v)) or                      (v < val_at_y and (i == 0 or pts[i - 1] >= val_at_y > v)):
                    line += self._style("│", color="cyan")
                else:
                    line += " "
            print(line)
        print(f"  {self._style(f'{mn} — {mx}', color='bright_black')}")
        print()

    def histogram(self, data: list[float], bins: int = 10, title: str | None = None) -> None:
        if not data:
            return
        mn, mx = min(data), max(data)
        bin_w = max((mx - mn) / bins, 0.01)
        counts = [0] * bins
        for v in data:
            idx = min(int((v - mn) / bin_w), bins - 1)
            counts[idx] += 1
        max_c = max(counts)
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        for i, c in enumerate(counts):
            bar_text = "█" * int(c / max_c * 30) if max_c else ""
            print(f"  {self._style(f'{mn + i*bin_w:.1f}', color='bright_black'):8s} {self._style(bar_text, color='cyan')} {c}")
        print()

    def scatter(self, points: list[tuple], title: str | None = None, h: int = 12, w: int = 40) -> None:
        if not points:
            return
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        xr = max(xs) - min(xs) or 1
        yr = max(ys) - min(ys) or 1
        grid = [[" " for _ in range(w)] for _ in range(h)]
        for x, y in points:
            px = int((x - min(xs)) / xr * (w - 1))
            py = h - 1 - int((y - min(ys)) / yr * (h - 1))
            if 0 <= py < h and 0 <= px < w:
                grid[py][px] = "●"
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        for row in grid:
            print("  " + "".join(row))
        print()

    def donut(self, data: dict[str, float], title: str | None = None) -> None:
        self.pie(data, title=title)

    def waterfall(self, items: list[tuple], title: str | None = None) -> None:
        print()
        if title:
            print(self._style(f"  {title}", "bold"))
        running = 0
        for label, val in items:
            running += val
            bar_len = abs(val) // 2
            bar_text = "█" * min(bar_len, 40)
            color = "green" if val >= 0 else "red"
            print(f"  {self._style(label, color='bright_black'):12s} {self._style(bar_text, color=color)} {val:+d}")
        print(f"  {'─'*20} {running}")

    def bullet_graph(self, label: str, value: float, target: float, max_val: float = 100) -> None:
        bar_list = list(("█" * int(value / max_val * 30)).ljust(30))
        target_pos = int(target / max_val * 30)
        if target_pos < 30:
            bar_list[target_pos] = self._style("┃" if bar_list[target_pos] == " " else "┃", color="red")
        print(f"  {label:12s} {''.join(bar_list)} {value}/{max_val}")

    def heatmap(self, data: list[list[float]], title: str | None = None) -> None:
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

    def sparkline(self, values: list[int | float], title: str | None = None, width: int = 40) -> None:
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

    def gauge(self, value: float, max_val: float = 100, title: str | None = None, width: int = 30, color: str = "green") -> None:
        pct = min(value / max(max_val, 1), 1.0)
        filled = int(pct * width)
        bar_text = "█" * filled + "░" * (width - filled)
        if pct > 0.9:
            color = "red"
        elif pct > 0.7:
            color = "yellow"
        print()
        if title:
            print(f"  {self._style(title, 'bold')}")
        print(f"  {self._style(bar_text, color=color)} {self._style(f'{pct*100:.0f}%', 'bold', color=color)}")
        print()
