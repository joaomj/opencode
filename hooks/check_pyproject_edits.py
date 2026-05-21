#!/usr/bin/env python3
"""Detect direct edits to pyproject.toml in staged changes.

Enforces OC013: dependency management must go through uv commands,
not direct edits to pyproject.toml.
"""

from __future__ import annotations

import re
import subprocess


def get_staged_pyproject_changes() -> list[str]:
    """Return list of changed lines in pyproject.toml from staged diff."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--", "pyproject.toml"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    
    added_lines = []
    for line in result.stdout.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added_lines.append(line[1:])
    return added_lines


def is_dependency_section_change(line: str) -> bool:
    """Check if a changed line is in a dependency-related section."""
    # Patterns that indicate dependency changes
    dependency_patterns = [
        r'^\s*dependencies\s*=',
        r'^\s*\[project\.dependencies\]',
        r'^\s*\[tool\.uv\.dev-dependencies\]',
        r'^\s*\[tool\.poetry\.dependencies\]',
        r'^\s*\[tool\.pdm\.dependencies\]',
        r'^\s*requires\s*=\s*\[',  # requirements array
        r'^\s*"[\w-]+[=<>~!@]',  # package spec lines like "requests>=2.0"
    ]
    
    for pattern in dependency_patterns:
        if re.search(pattern, line):
            return True
    return False


def check_pyproject_edits() -> list[str]:
    """Check for direct pyproject.toml dependency edits."""
    errors = []
    changes = get_staged_pyproject_changes()
    
    if not changes:
        return errors
    
    # Check if changes are in dependency sections
    dependency_changes = [line for line in changes if is_dependency_section_change(line)]
    
    if dependency_changes:
        errors.append(
            "OC013: Direct edits to pyproject.toml dependency sections detected. "
            "Use uv commands instead:\n"
            "  - uv add <package>\n"
            "  - uv remove <package>\n"
            "  - uv lock --upgrade-package <package>"
        )
    
    return errors


def main() -> int:
    errors = check_pyproject_edits()
    
    if errors:
        print("pyproject.toml edit violations found:")
        for err in errors:
            print(f"  - {err}")
        return 1
    
    print("pyproject.toml edit checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
