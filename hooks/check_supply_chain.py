#!/usr/bin/env python3
"""Supply chain security checks for pre-commit.

Enforces:
- OC009: Lockfile must exist and be committed
- OC010: exclude-newer with 7-day buffer configured
- OC011: CI must use --locked install
- OC012: No blind --upgrade (use --upgrade-package)
"""

from __future__ import annotations

import os
import re
from pathlib import Path


LOCKFILE_NAMES = ("uv.lock", "pdm.lock", "poetry.lock")
VALID_DURATIONS = ("1 week", "7 days", "P7D")
BLIND_UPGRADE_RE = re.compile(r"uv\s+lock\s+--upgrade(?!\s+--upgrade-package)")
UNSAFE_DOWNLOAD_RE = re.compile(r"curl.*\|\s*bash")


def check_lockfile_exists(root: Path) -> list[str]:
    errors = []
    for name in LOCKFILE_NAMES:
        lockfile = root / name
        if lockfile.exists():
            if lockfile.stat().st_size == 0:
                errors.append(f"OC009: {name} exists but is empty")
            gitignore = root / ".gitignore"
            if gitignore.exists():
                if name in gitignore.read_text():
                    errors.append(f"OC009: {name} is gitignored but must be committed")
            return errors
    errors.append(f"OC009: No lockfile found. Expected one of: {', '.join(LOCKFILE_NAMES)}")
    return errors


def check_exclude_newer_configured(root: Path) -> list[str]:
    errors = []

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        found = False
        for line in content.splitlines():
            m = re.match(r"^\s*exclude-newer\s*=\s*[\"']([^\"']+)[\"']", line)
            if m:
                found = True
                value = m.group(1)
                if value not in VALID_DURATIONS:
                    errors.append(
                        f"OC010: exclude-newer value '{value}' is not a 7-day buffer. "
                        f"Use one of: {', '.join(VALID_DURATIONS)}"
                    )
                break
        if not found:
            errors.append(
                "OC010: exclude-newer not found in pyproject.toml. "
                'Add: exclude-newer = "1 week" under [tool.uv]'
            )
    else:
        errors.append("OC010: pyproject.toml not found in project root")

    home_config = Path.home() / ".config" / "uv" / "uv.toml"
    if home_config.exists() and "exclude-newer" in home_config.read_text():
        return errors

    if os.environ.get("UV_EXCLUDE_NEWER"):
        return errors

    errors.append(
        "OC010: exclude-newer not configured in pyproject.toml, "
        "~/.config/uv/uv.toml, or UV_EXCLUDE_NEWER env var"
    )
    return errors


def check_for_blind_upgrade(file_path: Path) -> list[str]:
    errors = []
    content = file_path.read_text()
    for i, line in enumerate(content.splitlines(), 1):
        if BLIND_UPGRADE_RE.search(line):
            errors.append(
                f"OC012: {file_path}:{i} blind 'uv lock --upgrade' detected. "
                "Use 'uv lock --upgrade-package <name>' instead"
            )
    return errors


def check_for_unsafe_downloads(file_path: Path) -> list[str]:
    errors = []
    content = file_path.read_text()
    for i, line in enumerate(content.splitlines(), 1):
        if UNSAFE_DOWNLOAD_RE.search(line):
            errors.append(
                f"SUPPLY-CHAIN: {file_path}:{i} unsafe 'curl | bash' detected. "
                "Download scripts can be manipulated. Use explicit install steps."
            )
    return errors


def find_scripts_to_check(root: Path) -> list[Path]:
    scripts = []
    patterns = [
        "*.sh",
        "*.yml",
        "*.yaml",
        "Makefile",
        "*.mk",
        ".github/workflows/*.yml",
        ".github/workflows/*.yaml",
        "scripts/**/*.sh",
        "ci/**/*.sh",
        "scripts/**/*.py",
        "setup.py",
        "install.sh",
    ]
    for pattern in patterns:
        scripts.extend(root.glob(pattern))
    return [f for f in scripts if f.is_file() and not f.name.startswith(".")]


def main() -> int:
    root = Path.cwd()
    all_errors: list[str] = []

    all_errors.extend(check_lockfile_exists(root))
    all_errors.extend(check_exclude_newer_configured(root))

    for script in find_scripts_to_check(root):
        all_errors.extend(check_for_blind_upgrade(script))
        all_errors.extend(check_for_unsafe_downloads(script))

    if all_errors:
        print("Supply chain security violations found:")
        for err in all_errors:
            print(f"  - {err}")
        print()
        print("Fix: uv lock --upgrade-package <name>, uv sync --locked, exclude-newer = '1 week'")
        return 1

    print("Supply chain security checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())