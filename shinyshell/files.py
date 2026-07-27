"""File system and OS methods for Shell."""

import os
import sys
import time
import shutil
import subprocess


from contextlib import contextmanager
class _FilesMixin:
    """File system utilities: tree, disk_usage, file_permissions, checksum, config, env, version, screenshot, session_start, session_stop, clipboard_copy, notify, audio_beep, audio_ding."""

    def tree(self, path: str = ".", max_depth: int = 3,
             exclude: list | None = None) -> None:
        """Display a directory tree."""
        from .icons import _ICONS

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

    def disk_usage(self, path: str = ".") -> None:
        """Disk usage with bar. sh.disk_usage('/')"""
        try:
            usage = shutil.disk_usage(path)
            gb = 1024 ** 3
            print()
            self.gauge(usage.used / gb, usage.total / gb, f"Disk: {path}", 40)
        except Exception as e:
            self.error(f"Error: {e}")

    def file_permissions(self, path: str) -> None:
        """Permission viewer. sh.file_permissions('app.py')"""
        try:
            mode = os.stat(path).st_mode
            perms = ""
            for who in ["USR", "GRP", "OTH"]:
                for perm in ["R", "W", "X"]:
                    bit = {"USR": {"R": 0o400, "W": 0o200, "X": 0o100},
                           "GRP": {"R": 0o040, "W": 0o020, "X": 0o010},
                           "OTH": {"R": 0o004, "W": 0o002, "X": 0o001}}[who][perm]
                    perms += perm.lower() if mode & bit else "-"
            print(f"  {perms} {path}")
        except Exception:
            pass

    def checksum(self, path: str, algo: str = "md5") -> str:
        """File hash with progress. sh.checksum('file.bin', 'sha256')"""
        import hashlib
        h = hashlib.new(algo)
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def config(self, path: str) -> None:
        """View config files (TOML, YAML, INI, JSON) with syntax colors. sh.config('.env')"""
        import configparser
        import json as _json
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

    def env(self, prefix: str | None = None) -> None:
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

    def version(self) -> None:
        """Show Python, OS, and package versions."""
        import platform
        from . import __version__
        print()
        self.metrics({
            "Python": platform.python_version(),
            "OS": f"{platform.system()} {platform.release()}",
            "shinyshell": __version__,
            "Terminal": shutil.get_terminal_size().columns,
            "Color": "✅ Supported" if self._color_enabled else "❌ No",
        })

    def screenshot(self, path: str = "terminal.txt") -> None:
        """Save last terminal output to file. sh.screenshot('output.txt')"""
        try:
            with open(path, "w") as f:
                f.write("shinyshell terminal capture\n")
                f.write("=" * 40 + "\n")
            self.success(f"Saved: {path}")
        except Exception as e:
            self.error(f"Save failed: {e}")

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

    def clipboard_copy(self, text: str) -> None:
        """Copy text to system clipboard. sh.clipboard_copy('Hello')"""
        import platform
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

    def notify(self, title: str, message: str = "") -> None:
        """Cross-platform desktop notification. sh.notify('Build complete', 'All tests passed')"""
        import platform
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

    def audio_beep(self, times: int = 1) -> None:
        """Play a terminal beep. sh.audio_beep(3)"""
        sys.stdout.write('\a' * times)
        sys.stdout.flush()

    def audio_ding(self) -> None:
        """Play a success ding sound."""
        import platform
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
