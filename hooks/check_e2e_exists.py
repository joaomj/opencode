#!/usr/bin/env python3
"""Verify that e2e/integration tests exist for changed behavior.

Enforces OC016: E2E/integration tests are mandatory for user-visible behavior.
This hook checks that test files contain at least one e2e or integration test.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


E2E_INDICATORS = [
    r"def test_.*e2e",
    r"def test_.*integration",
    r"def test_.*end_to_end",
    r"class.*E2E",
    r"class.*Integration",
    r"@pytest\.mark\.e2e",
    r"@pytest\.mark\.integration",
    r"requests\.get\(|requests\.post\(",  # HTTP client calls
    r"playwright",
    r"selenium",
    r"client\.get\(|client\.post\(",  # TestClient (FastAPI/Flask)
]

E2E_RE = re.compile("|".join(f"({p})" for p in E2E_INDICATORS), re.IGNORECASE)


def get_changed_python_files() -> list[Path]:
    """Get Python files changed in the current commit (staged)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    
    files = []
    for line in result.stdout.strip().split("\n"):
        if line.endswith(".py") and not line.startswith("test") and "__pycache__" not in line:
            files.append(Path(line))
    return files


def find_test_file(source_file: Path) -> Path | None:
    """Find the corresponding test file for a source file."""
    # Common conventions
    candidates = [
        Path("tests") / f"test_{source_file.name}",
        Path("test") / f"test_{source_file.name}",
        source_file.parent / f"test_{source_file.name}",
        source_file.with_name(f"test_{source_file.name}"),
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def has_e2e_tests(test_file: Path) -> bool:
    """Check if a test file contains e2e/integration tests."""
    try:
        content = test_file.read_text()
        return bool(E2E_RE.search(content))
    except (IOError, UnicodeDecodeError):
        return False


def main() -> int:
    changed_files = get_changed_python_files()
    
    if not changed_files:
        print("No Python files changed — e2e check skipped")
        return 0
    
    missing_e2e: list[Path] = []
    
    for source_file in changed_files:
        # Skip test files and __init__.py
        if source_file.name.startswith("test_") or source_file.name == "__init__.py":
            continue
        
        test_file = find_test_file(source_file)
        if test_file is None:
            missing_e2e.append(source_file)
            continue
        
        if not has_e2e_tests(test_file):
            missing_e2e.append(source_file)
    
    if missing_e2e:
        print("OC016: E2E/integration test violations found:")
        for source_file in missing_e2e:
            print(f"  - {source_file}: no e2e/integration tests found")
        print("\nFix: Add e2e or integration tests that verify user-visible behavior.")
        print("Unit tests alone are not sufficient.")
        return 1
    
    print("E2E test checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
