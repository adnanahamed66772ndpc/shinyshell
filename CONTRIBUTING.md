# Contributing to shinyshell 🚀

Thank you for your interest in contributing to shinyshell!

## Getting Started

```bash
git clone https://github.com/adnanahamed66772ndpc/shinyshell.git
cd shinyshell
pip install -e .
pip install pytest
```

## Running Tests

```bash
pytest -v
```

## Project Structure

```
shinyshell/
├── shinyshell/
│   ├── __init__.py    # Shell class (mixin composition)
│   ├── colors.py      # ANSI color engine
│   ├── icons.py       # Icons and borders
│   ├── messages.py    # success, error, warning, badge, header, box, hr
│   ├── tables.py      # table, metrics, grid, timeline, columns, venn
│   ├── charts.py      # pie, bar, line, histogram, scatter, gauge, sparkline
│   ├── progress.py    # spinner, progress, benchmark, live, steps
│   ├── interactive.py # confirm, choice, input, menu, form, autocomplete
│   ├── code.py        # syntax highlight, diff, git log/status
│   ├── network.py     # http, ping, dns, ip info
│   ├── data.py        # json, yaml, xml, csv, jwt, hexdump, uuid
│   ├── games.py       # slot, dice, matrix, confetti, timer
│   ├── utils.py       # secret, trace, retry, throttle, text utils
│   ├── files.py       # tree, disk_usage, env, clipboard, notify
│   ├── qr.py          # QR codes, ASCII image
│   ├── pipe.py        # _PipeOutput chaining
│   └── banner.py      # ASCII banner renderer
├── tests/
│   └── test_core.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Adding a New Feature

1. Add the method to the appropriate mixin class in the matching module
2. All methods use `self._style()` for colored output and `self._width` for terminal width
3. Add a test in `tests/test_core.py`
4. Run `pytest -v` to verify

## Design Philosophy

- **Zero dependencies** — all features use only Python stdlib
- **Mixin architecture** — features are organized into logical mixin classes
- **Cross-platform** — works on Linux, macOS, and Windows
- **Graceful fallback** — when color/features unavailable, degrade gracefully
