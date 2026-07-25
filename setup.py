"""Setup for shinyshell."""
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="shinyshell",
    version="0.4.0",
    author="Adnan Ahamed Himal",
    author_email="hello@adnanahamedhimal.com",
    description="Python library for beautiful terminal output — colored printing, tables, progress bars, syntax highlighting, bar charts, QR codes, and more. Zero dependencies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adnanahamed66772ndpc/shinyshell",
    project_urls={
        "Source": "https://github.com/adnanahamed66772ndpc/shinyshell",
        "Bug Reports": "https://github.com/adnanahamed66772ndpc/shinyshell/issues",
        "Discussions": "https://github.com/adnanahamed66772ndpc/shinyshell/discussions",
        "Documentation": "https://github.com/adnanahamed66772ndpc/shinyshell#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Utilities",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    keywords=[
        "terminal", "cli", "console", "pretty", "beautiful", "output",
        "print", "colors", "ansi", "progress bar", "table", "spinner",
        "syntax highlighting", "diff", "json", "bar chart", "qr code",
        "ascii art", "markdown", "debug", "trace", "logging", "bash",
        "shell", "colored", "formatting", "rich", "colorama", "termcolor",
        "python library", "python package", "python cli", "python terminal",
        "developer tools", "devtools", "zero dependency",
    ],
)
