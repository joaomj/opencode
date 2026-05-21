#!/usr/bin/env python3
"""CLI entry point for opencode-lint.

Usage:
    opencode-lint [options] [files...]

Options:
    --fix           Attempt to auto-fix violations where possible
    --pre-commit    Exit with non-zero code on any violation (CI mode)
    --help          Show this help message
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from opencode_lint.runner import LinterRunner
from opencode_lint.violation import Violation


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog='opencode-lint',
        description='Custom linter for AGENTS.md rules (Factory.ai concept)',
    )

    parser.add_argument(
        'files',
        nargs='*',
        help='Files or directories to lint (default: current directory)',
    )

    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to auto-fix violations where possible',
    )

    parser.add_argument(
        '--pre-commit',
        action='store_true',
        help='Exit with non-zero code on any violation (for pre-commit hooks)',
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0',
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
            marker = "✗" if v.severity == 'error' else "⚠"
            print(f"  {marker} Line {v.line_number}:{v.column} - {v.rule_id}")
            print(f"     {v.message}")
            if v.fix:
                print(f"     Fix: {v.fix}")
            print()


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Determine targets
    if args.files:
        targets = [Path(f) for f in args.files]
    else:
        # Default to current directory
        targets = [Path('.')]

    # Validate targets exist
    for target in targets:
        if not target.exists():
            print(f"Error: File not found: {target}", file=sys.stderr)
            return 2

    # Run linter
    runner = LinterRunner()
    violations, exit_code = runner.run(targets, fix=args.fix)

    # Print results
    print_violations(violations)

    # Summary
    error_count = sum(1 for v in violations if v.severity == 'error')
    warning_count = sum(1 for v in violations if v.severity == 'warning')

    print(f"\nSummary: {error_count} error(s), {warning_count} warning(s)")

    # Exit code logic
    if args.pre_commit:
        # Pre-commit mode: exit 1 on any violation
        return 1 if violations else 0
    else:
        # Normal mode: exit 1 only on errors
        return 1 if error_count > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
