"""Test mock abuse policy.

Detects mock-heavy and internal-mocking patterns in tests.
Policy: mock external boundaries only. Prefer fakes and
integration tests for internal collaborators.
"""

import re
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class NoTestMockAbuse(Rule):
    """Mock policy rule: mock external boundaries only.

    Allowed: Mocking external services (HTTP SDKs, cloud clients,
    payment gateways, databases).
    Not allowed by default: Mocking internal domain/services.
    If needed, add marker 'mock-allow-internal: <reason>' and pair
    with an integration test.
    """

    rule_id = "OC-MOCK"
    description = "Mock external boundaries only; avoid internal collaborator mocks"
    severity = "error"
    categories = ["testing", "quality"]

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

    PY_PATCH_TARGET_RE = re.compile(
        r"\bpatch\(\s*['\"](?P<target>[^'\"]+)['\"]"
    )
    PY_PATCH_OBJECT_RE = re.compile(r"\bpatch\.object\(")
    PY_MOCK_CLASS_RE = re.compile(r"\b(?:MagicMock|Mock)\(")
    JS_MOCK_MODULE_RE = re.compile(
        r"\b(?:jest|vi)\.mock\(\s*['\"](?P<module>[^'\"]+)['\"]"
    )
    JS_STUB_RE = re.compile(r"\bsinon\.stub\(")

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        violations = []

        if not self._is_test_file(file_path):
            return violations

        if self.DISABLE_MARKER in content:
            return violations

        lines = content.splitlines()
        external_prefixes = self._get_external_prefixes()

        for index, line in enumerate(lines):
            line_number = index + 1

            for match in self.PY_PATCH_TARGET_RE.finditer(line):
                target = match.group("target")
                if self._is_external(target, external_prefixes):
                    continue
                if self._has_allow_marker(lines, index):
                    continue
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=line_number,
                        column=0,
                        message=(
                            "Internal patch target detected. Prefer real collaborator/fake. "
                            f"If required, add '{self.ALLOW_MARKER}: <reason>' and pair with "
                            "integration coverage."
                        ),
                    )
                )

            if self.PY_PATCH_OBJECT_RE.search(line) and not self._has_allow_marker(lines, index):
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=line_number,
                        column=0,
                        message=(
                            "patch.object() detected. This often mocks internal collaborators. "
                            f"Add '{self.ALLOW_MARKER}: <reason>' only when unavoidable."
                        ),
                    )
                )

            if self.PY_MOCK_CLASS_RE.search(line) and not self._has_allow_marker(lines, index):
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=line_number,
                        column=0,
                        message=(
                            "Mock()/MagicMock() detected. Prefer fakes/in-memory adapters for "
                            "internal code. "
                            f"Use '{self.ALLOW_MARKER}: <reason>' for justified exceptions."
                        ),
                    )
                )

            for match in self.JS_MOCK_MODULE_RE.finditer(line):
                module_name = match.group("module")
                if not self._is_internal_module(module_name):
                    continue
                if self._has_allow_marker(lines, index):
                    continue
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=line_number,
                        column=0,
                        message=(
                            "Local module mock detected (jest/vi). Prefer integration/component "
                            "tests for real behavior. "
                            f"Add '{self.ALLOW_MARKER}: <reason>' if unavoidable."
                        ),
                    )
                )

            if self.JS_STUB_RE.search(line) and not self._has_allow_marker(lines, index):
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=line_number,
                        column=0,
                        message=(
                            "sinon.stub() detected. Validate this is at an external boundary. "
                            f"Add '{self.ALLOW_MARKER}: <reason>' for exceptions."
                        ),
                    )
                )

        return violations

    def _is_test_file(self, path: Path) -> bool:
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

    def _has_allow_marker(self, lines: List[str], index: int) -> bool:
        current = lines[index]
        previous = lines[index - 1] if index > 0 else ""
        return self.ALLOW_MARKER in current or self.ALLOW_MARKER in previous

    def _is_external(self, target: str, external_prefixes: tuple[str, ...]) -> bool:
        target = target.strip()
        return any(
            target == prefix or target.startswith(f"{prefix}.")
            for prefix in external_prefixes
        )

    def _is_internal_module(self, module_name: str) -> bool:
        name = module_name.strip()
        return name.startswith(".") or name.startswith("/") or name.startswith("@/")

    def _get_external_prefixes(self) -> tuple[str, ...]:
        allowlist_path = Path(".test-mock-external-allowlist")
        if allowlist_path.exists():
            raw = allowlist_path.read_text(encoding="utf-8").splitlines()
            cleaned = tuple(
                item.strip()
                for item in raw
                if item.strip() and not item.strip().startswith("#")
            )
            if cleaned:
                return cleaned
        return self.DEFAULT_PY_EXTERNAL_PREFIXES
