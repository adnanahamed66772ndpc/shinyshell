"""Setup for shinyshell."""
from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="shinyshell",
    version="0.2.1",
    author="Adnan Ahamed Himal",
    description="Beautiful terminal output for Python. Zero dependencies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adnanahamed66772ndpc/shinyshell",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    keywords="terminal, shell, pretty, beautiful, output, cli, print, colors",
)
