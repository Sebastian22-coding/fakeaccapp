#!/usr/bin/env python3
"""
Setup-Skript für FakeAccountScanner
"""

from setuptools import setup, find_packages
from pathlib import Path

# README-Inhalt lesen
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="fake-account-scanner",
    version="1.0.0",
    author="FakeAccountScanner Team",
    author_email="info@fakeaccountscanner.com",
    description="Eine macOS Desktop-App zum Scannen von Social Media Plattformen nach Benutzernamen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fakeaccountscanner/fake-account-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "typing-extensions>=4.8.0",
    ],
    extras_require={
        "dev": [
            "pyinstaller>=5.0",
            "black",
            "flake8",
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "fake-account-scanner=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.rst"],
    },
)