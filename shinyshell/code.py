"""Code display methods for Shell."""

import os
import sys
import time
import hashlib


from contextlib import contextmanager
class _CodeMixin:
    """Code display: code, diff, git_log, git_status, stack_trace, process_info, pip_list, filewatch."""

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

    def stack_trace(self, exc_info=None) -> None:
        """Pretty stack trace. sh.stack_trace()"""
        import traceback
        if exc_info is None:
            exc_info = sys.exc_info()
        if exc_info[0]:
            print()
            print(self._style("  Stack Trace:", "bold", color="red"))
            for line in traceback.format_exception(*exc_info):
                for l in line.split("\n"):
                    if l.strip():
                        print(f"  {self._style(l, color='red')}")
            print()

    def process_info(self, pid: int | None = None) -> None:
        """Process info. sh.process_info()"""
        pid = pid or os.getpid()
        try:
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            self.metrics({
                "PID": pid,
                "Memory (MB)": f"{usage.ru_maxrss / 1024:.1f}",
                "User CPU (s)": f"{usage.ru_utime:.2f}",
                "System CPU (s)": f"{usage.ru_stime:.2f}",
            })
        except Exception:
            self.info(f"PID: {pid}")

    def pip_list(self, filter_str: str = "") -> None:
        """Pretty pip list. sh.pip_list('django')"""
        import subprocess
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=columns"],
                                    capture_output=True, text=True, timeout=10)
            print()
            print(self._style("  pip list", "bold", color="cyan"))
            for line in result.stdout.split("\n"):
                if not filter_str or filter_str.lower() in line.lower():
                    if line.strip():
                        print(f"  {line}")
            print()
        except Exception as e:
            self.error(f"pip error: {e}")

    def filewatch(self, path: str, callback=None) -> None:
        """Watch a file/directory for changes. sh.filewatch('app.py', callback=my_handler)"""
        print()
        self.info(f"Watching {path}... (Ctrl+C to stop)")
        try:
            if os.path.isfile(path):
                last_hash = hashlib.md5(open(path, "rb").read()).hexdigest()
                while True:
                    time.sleep(1)
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
                    time.sleep(1)
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
