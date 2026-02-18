#!/usr/bin/env python3
#
# File Name: header.py
# Author: Alexandre Kévin DE FREITAS MARTINS
# Creation Date: 18/2/2026
# Description: Header Generator Script
#              Reads configuration from .env and header.json to generate
#              license headers with dynamic file names and descriptions.
# Copyright (c) 2026 Alexandre Kévin DE FREITAS MARTINS
# Version: 1.0.0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import re
import sys
import json
from datetime import datetime
from pathlib import Path


# ─── .env Loader ───────────────────────────────────────────────────────────────

def load_env(env_path: str) -> dict:
    """Parse a .env file and return a dict of key=value pairs."""
    env_vars = {}
    if not os.path.isfile(env_path):
        print(f"Warning: .env file not found at {env_path}")
        print("Copy .env.example to .env and fill in your values.")
        sys.exit(1)
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


# ─── Description Generator ─────────────────────────────────────────────────────

# Maps common filename patterns / directory hints to human-readable descriptions
DESCRIPTION_RULES: list[tuple[str, str]] = [
    # Vue components
    (r"views?[/\\]", "Vue view component for the {name} page."),
    (r"layouts?[/\\]", "Vue layout component for {name}."),
    (r"components?[/\\]", "Vue component for {name}."),
    (r"pages?[/\\]", "Page component for {name}."),
    (r"composables?[/\\]", "Vue composable providing {name} logic."),
    # State / store
    (r"stores?[/\\]", "Pinia/Vuex store module for {name}."),
    # Routing
    (r"router", "Application routing configuration."),
    # Services / API
    (r"services?[/\\]", "Service layer handling {name} operations."),
    (r"api[/\\]", "API client for {name} endpoints."),
    # Utils / helpers
    (r"utils?[/\\]", "Utility functions for {name}."),
    (r"helpers?[/\\]", "Helper functions for {name}."),
    # Types / interfaces
    (r"types?[/\\]", "TypeScript type definitions for {name}."),
    (r"interfaces?[/\\]", "TypeScript interfaces for {name}."),
    (r"models?[/\\]", "Data model definitions for {name}."),
    # Middleware
    (r"middlewares?[/\\]", "Middleware for {name}."),
    # Plugins
    (r"plugins?[/\\]", "Plugin configuration for {name}."),
    # Config
    (r"config", "Configuration file for {name}."),
    # Tests
    (r"(__tests__|tests?|spec)[/\\]", "Test suite for {name}."),
]


def generate_description(file_path: str) -> str:
    """Generate a human-readable description based on filename and path."""
    basename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(basename)[0]

    # Convert camelCase / PascalCase / kebab-case / snake_case to readable words
    readable = re.sub(r"[-_]", " ", name_without_ext)
    readable = re.sub(r"([a-z])([A-Z])", r"\1 \2", readable)
    readable = readable.strip()

    # Special filenames
    lower = basename.lower()
    if lower in ("index.ts", "index.vue", "index.js"):
        parent = os.path.basename(os.path.dirname(file_path))
        readable = re.sub(r"[-_]", " ", parent)
        readable = re.sub(r"([a-z])([A-Z])", r"\1 \2", readable).strip()
        return f"Entry point for the {readable} module."
    if lower.startswith("main.") or lower.startswith("app."):
        return "Application entry point."

    # Try to match a directory-based rule
    normalised = file_path.replace("\\", "/")
    for pattern, template in DESCRIPTION_RULES:
        if re.search(pattern, normalised, re.IGNORECASE):
            return template.format(name=readable)

    # Fallback: generic but still uses the readable name
    ext = os.path.splitext(basename)[1]
    if ext == ".vue":
        return f"Vue component for {readable}."
    if ext in (".ts", ".tsx"):
        return f"TypeScript module for {readable}."
    if ext in (".js", ".jsx"):
        return f"JavaScript module for {readable}."
    return f"Source file for {readable}."


# ─── Header Loader ─────────────────────────────────────────────────────────────

class HeaderManager:
    """Loads header templates from JSON and resolves placeholders per file."""

    def __init__(self, json_path: str, env_vars: dict):
        with open(json_path, "r", encoding="utf-8") as f:
            self.templates = json.load(f)
        self.author = env_vars.get("HEADER_AUTHOR", "")
        self.company = env_vars.get("HEADER_COMPANY", "")
        self.year = env_vars.get("HEADER_YEAR", "") or str(datetime.now().year)
        self.extensions = [
            e.strip() for e in env_vars.get("HEADER_EXTENSIONS", ".ts,.vue").split(",")
        ]
        self.exclude_dirs = [
            d.strip()
            for d in env_vars.get("HEADER_EXCLUDE_DIRS", "node_modules,.git").split(",")
        ]

    # ── placeholder resolution ──────────────────────────────────────────────

    def _resolve(self, lines: list[str], file_path: str) -> str:
        """Replace {{PLACEHOLDERS}} in a list of header lines and return a string."""
        filename = os.path.basename(file_path)
        description = generate_description(file_path)
        text = "\n".join(lines) + "\n"
        text = text.replace("{{FILE_NAME}}", filename)
        text = text.replace("{{AUTHOR}}", self.author)
        text = text.replace("{{YEAR}}", self.year)
        text = text.replace("{{COMPANY}}", self.company)
        text = text.replace("{{DESCRIPTION}}", description)
        return text

    def get_header(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1]
        key = "vueHeader" if ext == ".vue" else "header"
        return self._resolve(self.templates[key], file_path)

    def get_is_header(self, file_path: str) -> str:
        """Return the check-prefix used to detect an existing header."""
        ext = os.path.splitext(file_path)[1]
        key = "isVueHeader" if ext == ".vue" else "isHeader"
        return self._resolve(self.templates[key], file_path)

    # ── file processing ─────────────────────────────────────────────────────

    def _already_has_header(self, content: str, file_path: str) -> bool:
        """Check if the file already starts with a header comment block."""
        is_header = self.get_is_header(file_path)
        if content.startswith(is_header):
            return True
        # Also match existing headers with different metadata (e.g. old author)
        ext = os.path.splitext(file_path)[1]
        if ext == ".vue":
            return content.startswith("<!--\n/**\nFile Name:")
        return content.startswith("/*\nFile Name:")

    def add_header(self, file_path: str) -> None:
        """Add a header to a file if it doesn't already have one."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if self._already_has_header(content, file_path):
            print(f"  [skip] {file_path}")
            return
        header = self.get_header(file_path)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header)
            f.write(content)
        print(f"  [added] {file_path}")

    # ── directory walking ───────────────────────────────────────────────────

    def should_exclude(self, dirpath: str) -> bool:
        parts = Path(dirpath).parts
        return any(excl in parts for excl in self.exclude_dirs)

    def collect_files(self, path: str) -> list[str]:
        """Collect all target files under *path* respecting extension and exclude filters."""
        if os.path.isfile(path):
            ext = os.path.splitext(path)[1]
            return [path] if ext in self.extensions else []
        files: list[str] = []
        for dirpath, dirnames, filenames in os.walk(path):
            if self.should_exclude(dirpath):
                dirnames.clear()  # prune walk
                continue
            for fname in filenames:
                if os.path.splitext(fname)[1] in self.extensions:
                    files.append(os.path.join(dirpath, fname))
        return sorted(files)


# ─── CLI ────────────────────────────────────────────────────────────────────────

def print_help():
    print("USAGE")
    print("    ./header.py <path>")
    print()
    print("DESCRIPTION")
    print("    path    A file or directory to add headers to.")
    print()
    print("OPTIONS")
    print("    -h      Show this help message.")
    print()
    print("CONFIGURATION")
    print("    Place a .env file next to header.py with the following variables:")
    print("      HEADER_AUTHOR         Author name for the header")
    print("      HEADER_COMPANY        Company name for copyright")
    print("      HEADER_YEAR           Copyright year (default: current year)")
    print("      HEADER_EXTENSIONS     Comma-separated extensions (default: .ts,.vue)")
    print("      HEADER_EXCLUDE_DIRS   Comma-separated dirs to skip (default: node_modules,.git)")


def main():
    if len(sys.argv) != 2 or sys.argv[1] == "-h":
        print_help()
        sys.exit(0 if (len(sys.argv) == 2 and sys.argv[1] == "-h") else 84)

    target_path = sys.argv[1]
    if not os.path.isfile(target_path) and not os.path.isdir(target_path):
        print(f"Error: '{target_path}' is not a valid file or directory.")
        print("Use -h for help.")
        sys.exit(84)

    # Resolve paths relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env")
    json_path = os.path.join(script_dir, "header.json")

    # Load configuration
    env_vars = load_env(env_path)
    manager = HeaderManager(json_path, env_vars)

    print(f"Author:     {manager.author}")
    print(f"Company:    {manager.company}")
    print(f"Year:       {manager.year}")
    print(f"Extensions: {', '.join(manager.extensions)}")
    print(f"Excluding:  {', '.join(manager.exclude_dirs)}")
    print()

    # Process files
    files = manager.collect_files(target_path)
    if not files:
        print("No matching files found.")
        sys.exit(0)

    print(f"Processing {len(files)} file(s)...\n")
    for file_path in files:
        manager.add_header(file_path)

    print(f"\nDone. Processed {len(files)} file(s).")


if __name__ == "__main__":
    main()
