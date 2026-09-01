#!/usr/bin/env python3
"""CLI entry point for opencode-lint.

Usage:
    opencode-lint [options] [files...]

Options:
    --profile       Select the fast or coding profile
    --staged        Check staged files from the current Git repository
    --pre-commit    Exit with non-zero code on any violation (CI mode)
    --help          Show this help message
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from opencode_lint.runner import LinterRunner, find_project_root, load_config
from opencode_lint.violation import Violation


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="opencode-lint",
        description="Custom linter for repository policies",
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="Files or directories to lint (default: current directory)",
    )

    parser.add_argument(
        "--pre-commit",
        action="store_true",
        help="Exit with non-zero code on any violation (for pre-commit hooks)",
    )

    parser.add_argument(
        "--profile",
        choices=("fast", "coding"),
        default="coding",
        help="Lint profile to run (default: coding)",
    )

    parser.add_argument(
        "--staged",
        action="store_true",
        help="Check only staged files in the current Git repository",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    return parser


def print_violations(violations: List[Violation]) -> None:
    """Print violations in a readable format."""
    if not violations:
        print("✓ No violations found")
        return

    # Group by file
    by_file: dict[Path, List[Violation]] = {}
    for v in violations:
        by_file.setdefault(v.file_path, []).append(v)

    print(f"\nFound {len(violations)} violation(s):\n")

    for file_path, file_violations in sorted(by_file.items()):
        print(f"{file_path}")
        for v in sorted(file_violations, key=lambda x: x.line_number):
            marker = "✗" if v.severity == "error" else "⚠"
            print(f"  {marker} Line {v.line_number}:{v.column} - {v.rule_id}")
            print(f"     {v.message}")
            if v.fix:
                print(f"     Fix: {v.fix}")
            print()


def _staged_targets() -> List[Path]:
    """Return staged paths or raise when Git cannot provide them."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("--staged requires Git")
    result = subprocess.run(  # noqa: S603
        [git, "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("--staged requires a Git repository")
    return [Path(line) for line in result.stdout.splitlines() if line]


def _targets(args: argparse.Namespace, parser: argparse.ArgumentParser) -> List[Path]:
    """Resolve explicit, staged, or current-directory targets."""
    if args.staged and args.files:
        parser.error("--staged cannot be combined with file targets")
    if args.staged:
        return _staged_targets()
    if args.files:
        return [Path(file_path) for file_path in args.files]
    return [Path(".")]


def _validate_targets(targets: List[Path]) -> str | None:
    """Return the first missing target, if any."""
    missing = next((target for target in targets if not target.exists()), None)
    return str(missing) if missing else None


def _exit_code(violations: List[Violation], pre_commit: bool) -> int:
    """Return the profile-specific process result."""
    if pre_commit:
        return 1 if violations else 0
    return 1 if any(v.severity == "error" for v in violations) else 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        targets = _targets(args, parser)
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    missing = _validate_targets(targets)
    if missing:
        print(f"Error: File not found: {missing}", file=sys.stderr)
        return 2

    project_root = find_project_root(targets)
    try:
        config = load_config(project_root)
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    profile = "fast" if args.pre_commit else args.profile
    runner = LinterRunner(config=config, profile=profile)
    violations, exit_code = runner.run(targets)

    # Print results
    print_violations(violations)

    error_count = sum(1 for v in violations if v.severity == "error")
    warning_count = sum(1 for v in violations if v.severity == "warning")

    print(f"\nSummary: {error_count} error(s), {warning_count} warning(s)")
    return _exit_code(violations, args.pre_commit)


if __name__ == "__main__":
    sys.exit(main())
