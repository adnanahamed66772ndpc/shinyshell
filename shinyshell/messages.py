"""Message and layout methods for Shell."""

from .icons import _ICONS, _BORDERS


class _MessageMixin:
    """Message helpers: success, error, warning, info."""

    def success(self, message: str) -> None:
        self._log("success", message, "green")

    def error(self, message: str) -> None:
        self._log("error", message, "red")

    def warning(self, message: str) -> None:
        self._log("warning", message, "yellow")

    def info(self, message: str) -> None:
        self._log("info", message, "cyan")

    def _log(self, level: str, message: str, color: str) -> None:
        icon = _ICONS.get(level, "•")
        prefix = self._style(f" {icon} ", bg=color, color="white")
        text = self._style(f" {message}", color=color)
        print(f"{prefix}{text}")

    def badge(self, text: str, color: str = "green") -> str:
        return self._style(f" {text} ", "bold", color="white", bg=color)

    def emoji(self, name: str) -> str:
        return _ICONS.get(name.lower(), "❓")


class _LayoutMixin:
    """Layout methods: header, box, hr, rule, banner."""

    def header(self, title: str, level: int = 1) -> None:
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
        from .banner import render
        print(self._style(render(text), color=color))

    def box(self, content: str, title: str | None = None,
            style: str = "round", color: str = "cyan") -> None:
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
        for line_data in lines:
            padded = line_data.ljust(width)
            print(f"  {self._style(v, color=color)} {padded} {self._style(v, color=color)}")
        bottom = bl + h * width + br
        print(self._style(f"  {bottom}", color=color))
        print()

    def hr(self, label: str | None = None) -> None:
        if label:
            left = "─" * 4
            right = "─" * max(0, self._width - len(label) - 12)
            print(f"\n  {self._style(left, color='bright_black')} {self._style(label, 'bold', color='cyan')} {self._style(right, color='bright_black')}")
        else:
            print(f"  {self._style('─' * (self._width - 4), color='bright_black')}")

    def rule(self, label: str | None = None) -> None:
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
