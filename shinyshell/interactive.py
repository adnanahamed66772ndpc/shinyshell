"""Interactive input methods for Shell."""

import sys
import os
import tty
import termios
import select as _select

from .icons import _ICONS


from contextlib import contextmanager
class _InteractiveMixin:
    """Interactive input: confirm, choice, input, password, menu, toggle, radio_select, search_filter, form, autocomplete."""

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

    def choice(self, question: str, options: list) -> str | None:
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

    def input(self, prompt: str = "", default: str = "", validate=None) -> str:
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

    def menu(self, options: list, title: str | None = None) -> int | None:
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

    def toggle(self, label: str, default: bool = False) -> bool:
        """Toggle switch. sh.toggle('Dark mode', True)"""
        state = default
        display = {True: self._style(' ● ON ', 'bold', color='white', bg='green'),
                   False: self._style(' ○ OFF ', color='bright_black')}
        print(f"  {label}: {display[state]}")
        return state

    def radio_select(self, options: list, title: str | None = None) -> int | None:
        """Radio button select (same as choice). sh.radio_select(['A','B','C'])"""
        return self.choice(title or "Select:", options)

    def search_filter(self, items: list, query: str) -> list:
        """Filter items. sh.search_filter(['apple','banana','cherry'], 'a')"""
        return [i for i in items if query.lower() in i.lower()]

    def form(self, fields: list, title: str | None = None) -> dict:
        """Multi-field form. sh.form([('Name:',str),('Age:',int)])"""
        results = {}
        if title:
            self.header(title, level=2)
        for label, _type in fields:
            val = self.input(label)
            results[label.strip(':')] = val
        return results

    def autocomplete(self, prompt: str, options: list) -> str | None:
        """Autocomplete input. sh.autocomplete('Search:', ['apple','banana','cherry'])"""
        self.info(f"Options: {', '.join(options[:10])}{'...' if len(options)>10 else ''}")
        query = self.input(prompt)
        matches = [o for o in options if query.lower() in o.lower()] if query else options
        if matches:
            return self.choice("Matches:", matches[:8])
        return None
