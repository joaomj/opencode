#!/usr/bin/env python3
"""Detect mock-heavy and internal-mocking patterns in tests.

Policy intent:
- Allow mocking external boundaries when needed.
- Discourage mocking internal collaborators by default.
- Require explicit justification marker for exceptions.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ALLOW_MARKER = "mock-allow-internal"
DISABLE_MARKER = "mock-policy: disable"

DEFAULT_PY_EXTERNAL_PREFIXES = (
    "requests",
    "httpx",
    "aiohttp",
    "urllib3",
    "grpc",
    "boto3",
    "botocore",
    "stripe",
    "openai",
    "google.cloud",
    "psycopg",
    "psycopg2",
    "asyncpg",
    "pymysql",
    "mysql",
    "redis",
    "elasticsearch",
    "kafka",
    "confluent_kafka",
    "pika",
    "pymongo",
    "motor",
    "sqlalchemy",
    "smtplib",
    "socket",
)

PY_PATCH_TARGET_RE = re.compile(r"\bpatch\(\s*['\"](?P<target>[^'\"]+)['\"]")
PY_PATCH_OBJECT_RE = re.compile(r"\bpatch\.object\(")
PY_MOCK_CLASS_RE = re.compile(r"\b(?:MagicMock|Mock)\(")

JS_MOCK_MODULE_RE = re.compile(r"\b(?:jest|vi)\.mock\(\s*['\"](?P<module>[^'\"]+)['\"]")
JS_STUB_RE = re.compile(r"\bsinon\.stub\(")


@dataclass(frozen=True)
class Violation:
    file_path: Path
    line_number: int
    message: str


def _is_test_file(path: Path) -> bool:
    text = str(path).lower()
    if "/tests/" in text or text.startswith("tests/"):
        return True
    if "/test/" in text or text.startswith("test/"):
        return True
    if "/__tests__/" in text or text.startswith("__tests__/"):
        return True
    name = path.name.lower()
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith(".test.py")
        or name.endswith(".test.js")
        or name.endswith(".test.jsx")
        or name.endswith(".test.ts")
        or name.endswith(".test.tsx")
        or name.endswith(".spec.js")
        or name.endswith(".spec.jsx")
        or name.endswith(".spec.ts")
        or name.endswith(".spec.tsx")
    )


def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _has_allow_marker(lines: list[str], index: int) -> bool:
    current = lines[index]
    previous = lines[index - 1] if index > 0 else ""
    return ALLOW_MARKER in current or ALLOW_MARKER in previous


def _python_target_is_external(target: str, external_prefixes: tuple[str, ...]) -> bool:
    target = target.strip()
    return any(target == prefix or target.startswith(f"{prefix}.") for prefix in external_prefixes)


def _javascript_module_is_internal(module_name: str) -> bool:
    name = module_name.strip()
    return name.startswith(".") or name.startswith("/") or name.startswith("@/")


def _external_prefixes_from_env() -> tuple[str, ...]:
    raw = Path(".test-mock-external-allowlist").read_text(encoding="utf-8").splitlines() if Path(
        ".test-mock-external-allowlist"
    ).exists() else []
    cleaned = tuple(item.strip() for item in raw if item.strip() and not item.strip().startswith("#"))
    return cleaned if cleaned else DEFAULT_PY_EXTERNAL_PREFIXES


def _check_file(path: Path, external_prefixes: tuple[str, ...]) -> list[Violation]:
    violations: list[Violation] = []
    try:
        content = _read_file(path)
    except OSError as exc:
        return [Violation(path, 1, f"Could not read file: {exc}")]

    if DISABLE_MARKER in content:
        return violations

    lines = content.splitlines()

    for index, line in enumerate(lines):
        line_number = index + 1

        for match in PY_PATCH_TARGET_RE.finditer(line):
            target = match.group("target")
            if _python_target_is_external(target, external_prefixes):
                continue
            if _has_allow_marker(lines, index):
                continue
            violations.append(
                Violation(
                    path,
                    line_number,
                    (
                        "Internal patch target detected. Prefer real collaborator/fake. "
                        f"If required, add '{ALLOW_MARKER}: <reason>' and pair with integration coverage."
                    ),
                )
            )

        if PY_PATCH_OBJECT_RE.search(line) and not _has_allow_marker(lines, index):
            violations.append(
                Violation(
                    path,
                    line_number,
                    (
                        "patch.object() detected. This often mocks internal collaborators. "
                        f"Add '{ALLOW_MARKER}: <reason>' only when unavoidable."
                    ),
                )
            )

        if PY_MOCK_CLASS_RE.search(line) and not _has_allow_marker(lines, index):
            violations.append(
                Violation(
                    path,
                    line_number,
                    (
                        "Mock()/MagicMock() detected. Prefer fakes/in-memory adapters for internal code. "
                        f"Use '{ALLOW_MARKER}: <reason>' for justified exceptions."
                    ),
                )
            )

        for match in JS_MOCK_MODULE_RE.finditer(line):
            module_name = match.group("module")
            if not _javascript_module_is_internal(module_name):
                continue
            if _has_allow_marker(lines, index):
                continue
            violations.append(
                Violation(
                    path,
                    line_number,
                    (
                        "Local module mock detected (jest/vi). Prefer integration/component tests for real behavior. "
                        f"Add '{ALLOW_MARKER}: <reason>' if unavoidable."
                    ),
                )
            )

        if JS_STUB_RE.search(line) and not _has_allow_marker(lines, index):
            violations.append(
                Violation(
                    path,
                    line_number,
                    (
                        "sinon.stub() detected. Validate this is at an external boundary. "
                        f"Add '{ALLOW_MARKER}: <reason>' for exceptions."
                    ),
                )
            )

    return violations


def main() -> int:
    files = [Path(arg) for arg in sys.argv[1:]]
    external_prefixes = _external_prefixes_from_env()
    violations: list[Violation] = []

    for file_path in files:
        if not _is_test_file(file_path):
            continue
        violations.extend(_check_file(file_path, external_prefixes))

    if not violations:
        return 0

    print("Test mock policy violations found:")
    for violation in violations:
        print(f"- {violation.file_path}:{violation.line_number} {violation.message}")

    print(
        "\nGuidance: Mock external boundaries only. Prefer behavior assertions, fakes, and integration tests."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())