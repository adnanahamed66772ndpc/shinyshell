# ✨ shinyshell

**Beautiful terminal output for Python. Zero dependencies. One import.**

[![PyPI version](https://img.shields.io/pypi/v/shinyshell.svg)](https://pypi.org/project/shinyshell/)
[![Python](https://img.shields.io/pypi/pyversions/shinyshell.svg)](https://pypi.org/project/shinyshell/)
[![License](https://img.shields.io/github/license/adnanahamed66772ndpc/shinyshell)](LICENSE)

```python
from shinyshell import Shell

sh = Shell()

sh.success("Deployed to production!")
sh.table(users, title="Team Members")
sh.progress("Installing deps...")
sh.header("My CLI App")
sh.code("print('hello')")
sh.countdown(5, "Launching")
```

---

## 📸 Demo

```python
from shinyshell import Shell
sh = Shell()

# Headers & banners
sh.header("DEPLOYMENT REPORT")
sh.banner("SHINY SHELL")

# Success / Warning / Error / Info
sh.success("Database migrated successfully")
sh.warning("Rate limit approaching — 93% used")
sh.error("Connection to API failed after 3 retries")
sh.info("Server running on http://localhost:8000")

# Beautiful tables
sh.table([
    {"Name": "Alice Chen", "Role": "Backend Dev", "Status": "✅ Active"},
    {"Name": "Bob Kumar", "Role": "Frontend", "Status": "✅ Active"},
    {"Name": "Charlie D.", "Role": "Design Lead", "Status": "⏳ On Leave"},
], title="Team Status")

# Progress with spinner
sh.spinner("Compiling assets...")
update = sh.progress("Uploading")
for i in range(100):
    update(i + 1, 100)

# Countdown
sh.countdown(5, "Deploying to production")

# Boxed content
sh.box("API Key: sk-****abcd\nEndpoint: /v1/chat\nModel: gpt-4", title="Configuration")

# Directory tree
sh.tree("./src", max_depth=2)

# Code blocks
sh.code("""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
""")

# Metrics dashboard
sh.metrics({
    "Users": 12483,
    "Active Now": 342,
    "Uptime": "✅ 99.9%",
    "Error Rate": "0.02%",
    "Avg Response": "23ms",
})

# Colored diff
sh.diff("hello world", "hello beautiful world")

# Interactive
if sh.confirm("Deploy to production?"):
    sh.success("Ship it! 🚀")

# Horizontal rule
sh.hr("Section 2")
```

---

## 📦 Install

```bash
pip install shinyshell
```

No dependencies. Uses only Python standard library. Works on **Linux**, **macOS**, and **Windows** (PowerShell, CMD, Windows Terminal).

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| `success()` | ✅ Green success messages |
| `warning()` | ⚠️ Yellow warnings |
| `error()` | ❌ Red errors |
| `info()` | ℹ️ Cyan info |
| `header()` | Styled section headers |
| `banner()` | ASCII art banners |
| `table()` | Beautiful data tables |
| `box()` | Content in styled boxes |
| `code()` | Syntax-highlighted code blocks |
| `diff()` | Colored git diff |
| `tree()` | Directory trees |
| `metrics()` | Key-value dashboards |
| `spinner()` | Animated loading spinner |
| `progress()` | Progress bars |
| `countdown()` | Animated countdown |
| `confirm()` | Interactive y/n prompts |
| `choice()` | Interactive option picker |
| `hr()` | Horizontal rules with labels |

---

## 🤔 Why?

Every Python script prints to the terminal. Most output looks boring. **shinyshell** makes it beautiful — with zero dependencies.

Before:
```
Task completed
Users: 1042
ERROR: Connection failed
```

After:
```
✨ Task completed
📊 Users: 1,042
💥 Connection failed
```

---

## 🔧 Advanced

```python
# Custom width
sh = Shell(width=80)

# Disable color
sh = Shell(color=False)

# Access icons
print(sh.icons["rocket"])  # 🚀

# Chaining
sh.success("Step 1 done").progress("Step 2...")
```

---

## 📄 License

MIT — © 2026 Adnan Ahamed Himal

---

## ⭐ Support

Found this useful? **Star this repo** and share it with your team!

[⬆ Back to top](#-shinyshell)
