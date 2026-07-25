# ✨ shinyshell — Beautiful Terminal Output Library for Python

<p align="center">
  <b>Python library for beautiful CLI output, colored terminal printing, progress bars,<br>
  tables, syntax highlighting, ASCII art, and interactive prompts — all with zero dependencies.</b><br>
  <i>One import. 38 features. Pure Python stdlib. No pip install headaches.</i>
</p>

<p align="center">
  <a href="https://pypi.org/project/shinyshell/"><img src="https://img.shields.io/pypi/v/shinyshell?color=green&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/shinyshell/"><img src="https://img.shields.io/pypi/pyversions/shinyshell" alt="Python Versions"></a>
  <a href="https://github.com/adnanahamed66772ndpc/shinyshell/blob/main/LICENSE"><img src="https://img.shields.io/github/license/adnanahamed66772ndpc/shinyshell" alt="MIT License"></a>
  <a href="https://pypi.org/project/shinyshell/"><img src="https://img.shields.io/pypi/dm/shinyshell" alt="Downloads"></a>
  <a href="https://github.com/adnanahamed66772ndpc/shinyshell"><img src="https://img.shields.io/github/stars/adnanahamed66772ndpc/shinyshell?style=social" alt="GitHub Stars"></a>
</p>

---

## 📦 Why shinyshell?

- **Zero dependencies** — uses only Python standard library (`os`, `sys`, `shutil`)
- **38 built-in features** — tables, progress bars, code highlighting, diff viewer, JSON formatter, bar charts, QR codes, ASCII art, and more
- **Cross-platform** — Linux, macOS, Windows Terminal, PowerShell, CMD, VS Code, PyCharm
- **Beginner-friendly** — one import, intuitive API, no configuration needed
- **Production-ready** — works in scripts, CLIs, CI/CD pipelines, Docker containers
- **Lightweight** — ~950 lines of code, installs in seconds

### Use Cases

| Use Case | Features You'll Use |
|----------|-------------------|
| **CLI tool developer** | progress bars, spinners, headers, tables, confirm dialogs |
| **Data scientist** | tables, bar charts, metrics dashboard, JSON viewer |
| **DevOps engineer** | colored messages, benchmarks, env viewer, code blocks |
| **Backend developer** | debug(), trace(), diff viewer, secret masking |
| **Student/learner** | markdown renderer, ASCII art, QR codes, emoji helper |

### vs Alternatives

| | shinyshell | rich | colorama | termcolor |
|---|-----------|------|----------|-----------|
| Dependencies | **0** | 10+ | 0 | 0 |
| Features | **38** | 50+ | 3 | 5 |
| Install size | **~25KB** | ~50MB | ~20KB | ~15KB |
| Tables | ✅ | ✅ | ❌ | ❌ |
| Progress bars | ✅ | ✅ | ❌ | ❌ |
| Code highlight | ✅ | ✅ | ❌ | ❌ |
| Bar charts | ✅ | ❌ | ❌ | ❌ |
| Timeline | ✅ | ❌ | ❌ | ❌ |
| QR codes | ✅ | ❌ | ❌ | ❌ |
| Debug/trace | ✅ | ❌ | ❌ | ❌ |
| Interactive | ✅ | ✅ | ❌ | ❌ |

> **shinyshell** is the sweet spot: ***rich's feature set with colorama's simplicity***.

---

## 📦 Install

```bash
pip install shinyshell
```

That's it. No dependencies. Works everywhere: **Linux, macOS, Windows (PowerShell/CMD/Terminal)**.

---

## 🚀 Quick Start

```python
from shinyshell import Shell

sh = Shell()

# Basic messages
sh.success("Database migrated!")
sh.error("Connection failed")
sh.warning("Disk usage at 92%")
sh.info("Server running on port 8000")
```

**Output:**
```
 ✨ Database migrated!
 💥 Connection failed
 ⚠️ Disk usage at 92%
 ℹ️ Server running on port 8000
```

---

## 📚 Complete Feature Reference

### 1. Headers & Banners

```python
# Level 1 header (boxed)
sh.header("DEPLOYMENT REPORT")

# Level 2 header (simple)
sh.header("Configuration", level=2)

# ASCII banner
sh.banner("SHINY")
sh.banner("HELLO", color="magenta")
```

### 2. Status Messages

```python
sh.success("Build completed!")     # Green, checkmark
sh.error("API returned 500")       # Red, cross
sh.warning("Memory at 85%")        # Yellow, triangle
sh.info("Listening on :8000")      # Cyan, info circle
```

### 3. Horizontal Rules

```python
# Simple divider
sh.hr()

# Labeled divider
sh.hr("Section 2")
```

### 4. Tables

```python
users = [
    {"Name": "Alice Chen", "Role": "Backend", "Status": "Active"},
    {"Name": "Bob Kumar", "Role": "Frontend", "Status": "On Leave"},
    {"Name": "Carol Diaz", "Role": "DevOps", "Status": "Active"},
]

sh.table(users, title="Team Members")

# Border styles: single, double, round, bold, dashed
sh.table(data, style="round")
```

### 5. Metrics Dashboard

```python
sh.metrics({
    "Users": 12483,
    "Active Now": 342,
    "Uptime": "✅ 99.9%",
    "Error Rate": "0.02%",
    "Avg Response": "23ms",
})
```

### 6. Boxed Content

```python
sh.box(
    "API Key: sk-****abcd\nEndpoint: /v1/chat\nModel: deepseek-v4",
    title="Configuration"
)
```

### 7. Code Blocks

```python
sh.code("""
def fibonacci(n):
    # Base case
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""")

# Supports Python keywords, strings, numbers, comments
```

### 8. Colored Diff

```python
old_code = "def greet(name):\n    return 'Hello'"
new_code = "def greet(name, title=''):\n    return f'Hello {title} {name}'"

sh.diff(old_code, new_code, old_label="v1.py", new_label="v2.py")
```

### 9. Directory Tree

```python
sh.tree("./myproject")
sh.tree("./src", max_depth=2)
sh.tree(".", exclude=["node_modules", ".git", "__pycache__"])
```

### 10. JSON Pretty Print

```python
sh.json({
    "user": {"name": "Alice", "age": 30, "active": True},
    "stats": {"posts": 142, "followers": 1200},
})
# Syntax-colored output: green keys, yellow strings, cyan numbers, magenta booleans
```

### 11. Markdown Rendering

```python
sh.markdown("""
# Main Title
## Subtitle
### Section

- Bullet point one
- Bullet point two

> This is a blockquote

**Bold text**
""")
```

### 12. Bar Charts

```python
sh.bar({
    "Python": 85,
    "JavaScript": 62,
    "Go": 45,
    "Rust": 38,
    "Ruby": 22,
}, title="Language Usage", color="magenta")
```

### 13. Timeline

```python
sh.timeline([
    {"date": "Jan 2024", "title": "v1.0 Released", "desc": "Initial launch with 17 features"},
    {"date": "Mar 2024", "title": "v1.5 Update", "desc": "Added tables and metrics"},
    {"date": "Jun 2024", "title": "v2.0 Major", "desc": "19 new features added"},
])
```

### 14. Columns

```python
features = ["success()", "error()", "table()", "code()", "tree()",
            "diff()", "json()", "bar()", "qr()", "live()"]

sh.columns(features, cols=3)
```

### 15. Badges

```python
print(sh.badge("v2.0", "green"))
print(sh.badge("BETA", "yellow"))
print(sh.badge("ERROR", "red"))
print(sh.badge("INFO", "cyan"))
```

### 16. QR Codes

```python
sh.qr("https://github.com/adnanahamed66772ndpc/shinyshell", title="Scan to visit repo")
sh.qr("Hello World")
```

### 17. Clickable Links

```python
print(sh.link("Visit GitHub", "https://github.com/adnanahamed66772ndpc/shinyshell"))
print(sh.link("Documentation", "https://pypi.org/project/shinyshell/"))
```

### 18. Secret Masking

```python
print(sh.secret("sk-abc123def456ghi789"))  # Output: sk-a****i789
print(sh.secret("my-password-here", visible=2))  # Output: my********re
```

### 19. Emoji Lookup

```python
print(sh.emoji("rocket"))     # 🚀
print(sh.emoji("fire"))       # 🔥
print(sh.emoji("star"))       # ⭐
print(sh.emoji("party"))      # 🎉
```

### 20. Environment Variables

```python
# Show all env vars
sh.env()

# Filter by prefix
sh.env("PYTHON")
sh.env("AWS_")

# Security: KEY, SECRET, TOKEN, PASSWORD values are auto-masked
```

### 21. Version Info

```python
sh.version()
# Output: Python, OS, shinyshell version, terminal size, color support
```

### 22. Debug

```python
user = {"name": "Alice", "age": 30}
status = "active"

sh.debug(user, status)

# Output:
# 🔍 app.py:42
#  arg0 dict {'name': 'Alice', 'age': 30}
#  arg1 str 'active'
```

---

### 23. Benchmark

```python
with sh.benchmark("Processing data"):
    # Your heavy computation here
    data = [i**2 for i in range(1000000)]

# Output:
# ⏱️  Processing data ........ 0.12s
```

### 24. Progress Bar

```python
update = sh.progress("Uploading files")
for i in range(100):
    time.sleep(0.02)
    update(i + 1, 100)
```

### 25. Steps Tracker

```python
step = sh.steps("Deploy to Production", total=5)

step("Building Docker image...")
step("Running tests...")
step("Pushing to registry...")
step("Updating service...")
step("Health check...")
```

### 26. Animated Spinner

```python
sh.spinner("Installing dependencies...", duration=2.0)
```

### 27. Countdown

```python
sh.countdown(5, "Launching rocket")
```

### 28. Live Display

```python
with sh.live() as display:
    for i in range(100):
        display(f"Processing... {i+1}%")
        time.sleep(0.03)
```

### 29. Confirm (Yes/No)

```python
if sh.confirm("Deploy to production?"):
    sh.success("Deploying...")
else:
    sh.info("Deployment cancelled")
```

### 30. Choice (Pick from options)

```python
env = sh.choice("Select environment:", ["Development", "Staging", "Production"])
sh.info(f"Selected: {env}")
```

### 31. Function Trace Decorator

```python
@sh.trace
def process_data(items):
    return len(items) * 2

result = process_data([1, 2, 3, 4, 5])

# Output:
# ⚙️ process_data([1, 2, 3, 4, 5]) → 0.001s

# Disable argument logging for sensitive functions:
@sh.trace(log_args=False)
def login(username, password):
    return True
```

### 32. Image to ASCII Art

```python
sh.image("screenshot.png", width=80)
sh.image("logo.jpg", width=60)

# Requires: pip install Pillow (optional)
```

### 33. Gradient Ruler

```python
sh.rule()
sh.rule("API Response")
```

---

## 🔧 Configuration

```python
sh = Shell(
    color=True,   # Enable/disable ANSI colors
    width=100,    # Custom terminal width
)
```

---

## 📊 Feature Summary

| Category | Features |
|----------|----------|
| Messages | `success`, `error`, `warning`, `info` |
| Layout | `header`, `banner`, `hr`, `rule`, `box` |
| Data Display | `table`, `metrics`, `json`, `bar`, `timeline`, `columns` |
| Code | `code`, `diff`, `markdown` |
| Progress | `spinner`, `progress`, `steps`, `countdown`, `benchmark`, `live` |
| Interactive | `confirm`, `choice` |
| Debug | `debug`, `trace`, `version`, `env` |
| Files | `tree`, `image` |
| Utilities | `badge`, `secret`, `link`, `emoji`, `qr` |
| **Total** | **38 features, 0 dependencies, ~950 lines** |

---

## 🌍 Platform Support

| Platform | Status |
|----------|--------|
| Linux (GNOME/KDE/tmux) | ✅ Full |
| macOS (Terminal/iTerm2) | ✅ Full |
| Windows Terminal | ✅ Full |
| Windows PowerShell | ✅ Full |
| Windows CMD | ✅ Full (Win 10+) |
| VS Code Terminal | ✅ Full |
| JetBrains Terminal | ✅ Full |
| CI/CD (GitHub Actions) | ✅ Full |

---

## 🤝 Contributing

```bash
git clone https://github.com/adnanahamed66772ndpc/shinyshell.git
cd shinyshell
pip install -e .
```

Pull requests welcome! Check [issues](https://github.com/adnanahamed66772ndpc/shinyshell/issues) for ideas.

---

## 📄 License

MIT — © 2026 [Adnan Ahamed Himal](https://adnanahamedhimal.com)

---

## ⭐ Support

If this library saved you time, **give it a star** on GitHub. It helps others find it too!

<p align="center">
  <a href="https://github.com/adnanahamed66772ndpc/shinyshell">⭐ Star on GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://pypi.org/project/shinyshell/">📦 View on PyPI</a>
</p>
