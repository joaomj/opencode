#!/usr/bin/env python3
"""Detect test skipping patterns in test files.

Enforces OC008: Never use # noqa, @pytest.mark.skip, @pytest.mark.xfail in tests.
Fix root cause instead.
"""

from __future__ import annotations

import re
from pathlib import Path


SKIP_PATTERNS = [
    r"#\s*noqa",
    r"@pytest\.mark\.skip",
    r"@pytest\.mark\.xfail",
    r"unittest\.skip",
    r"pytest\.skip\(",
]

SKIP_RE = re.compile("|".join(f"({p})" for p in SKIP_PATTERNS))


def find_test_files() -> list[Path]:
    """Find Python test files in common locations."""
    patterns = [
        "tests/**/*.py",
        "test/**/*.py",
        "**/*_test.py",
        "**/test_*.py",
    ]
    
    files = []
    for pattern in patterns:
        files.extend(Path(".").glob(pattern))
    
    # Filter out __pycache__ and non-files
    return [f for f in files if f.is_file() and "__pycache__" not in str(f)]


def check_file_for_skips(file_path: Path) -> list[tuple[int, str]]:
    """Check a single file for skip patterns. Returns list of (line_number, line_content)."""
    violations = []
    try:
        content = file_path.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if SKIP_RE.search(line):
                violations.append((i, line.strip()))
    except (IOError, UnicodeDecodeError):
        pass
    return violations


def main() -> int:
    test_files = find_test_files()
    all_violations: list[tuple[Path, int, str]] = []
    
    for file_path in test_files:
        for line_num, line_content in check_file_for_skips(file_path):
            all_violations.append((file_path, line_num, line_content))
    
    if all_violations:
        print("OC008: Test skip/noqa violations found:")
        for file_path, line_num, content in all_violations:
            print(f"  {file_path}:{line_num}: {content}")
        print("\nFix: Remove skip/xfail/noqa and fix the root cause.")
        return 1
    
    print("Test skip checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
