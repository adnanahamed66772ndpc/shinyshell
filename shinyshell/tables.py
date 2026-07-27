"""Table, metrics, grid, timeline, columns, and venn methods."""

from .icons import _ICONS, _BORDERS


class _TableMixin:
    """Table, metrics, grid, timeline, columns, and venn."""

    def table(self, data: list[dict], title: str | None = None, style: str = "single") -> None:
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
        top = tl + h * total_width + tr
        print(self._style(f"  {top}", color="bright_black"))
        cells = [self._style(f" {str(k).ljust(col_widths[k])}", "bold") for k in keys]
        print(f"  {v}{v.join(cells)}{v}")
        sep = l + h * total_width + r
        print(self._style(f"  {sep}", color="bright_black"))
        for row in data:
            cells = [f" {str(row.get(k, '')).ljust(col_widths[k])}" for k in keys]
            print(f"  {self._style(v, color='bright_black')}{v.join(cells)}{self._style(v, color='bright_black')}")
        bottom = bl + h * total_width + br
        print(self._style(f"  {bottom}", color="bright_black"))
        print()

    def metrics(self, items: dict[str, str | int | float]) -> None:
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

    def timeline(self, events: list[dict]) -> None:
        if not events:
            return
        print()
        for i, event in enumerate(events):
            is_last = i == len(events) - 1
            date = event.get("date", "")
            title = event.get("title", "")
            desc = event.get("desc", "")
            connector = "└──" if is_last else "├──"
            color = "green" if is_last else "cyan"
            print(f"  {self._style(date, 'bold', color=color)}")
            print(f"  {self._style(connector, color=color)} {self._style(title, 'bold')}")
            if desc:
                print(f"  {self._style('│' if not is_last else ' ', color='bright_black')}   {self._style(desc, color='bright_black')}")
            if not is_last:
                print(f"  {self._style('│', color='bright_black')}")
        print()

    def columns(self, items: list[str], cols: int = 2) -> None:
        if not items:
            return
        print()
        col_width = (self._width - 4) // cols
        for i in range(0, len(items), cols):
            row_items = items[i:i + cols]
            line = "".join(str(item).ljust(col_width)[:col_width] for item in row_items)
            print(f"  {line}")
        print()

    def grid(self, items: list[dict], cols: int = 2) -> None:
        print()
        cell_w = (self._width - 4) // cols - 4
        for i in range(0, len(items), cols):
            row_items = items[i:i + cols]
            cell_lines = []
            for item in row_items:
                lines_out = []
                ttl = item.get("title", "")
                val = str(item.get("value", ""))
                lines_out.append(self._style(f"── {ttl} ", "bold", color="cyan"))
                lines_out.append(f"   {val}")
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

    def venn(self, set_a: set, set_b: set, labels: tuple = ("A", "B"),
             title: str | None = None) -> None:
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
