"""OC014: No hardcoded configurable values.

Quality & security rule to prevent magic numbers, inline URLs,
hardcoded ports, timeouts, thresholds, and other config values
from being buried in source code.

Enforces: All configurable values must live in centralized config modules.
"""

import ast
import re
from pathlib import Path
from typing import List, Set

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class NoHardcodedConfig(Rule):
    """Rule OC014: No hardcoded configurable values.

    Prevents:
    - Inline URLs (http://, https://, ws://, wss://)
    - Hardcoded ports (5432, 8080, :5432)
    - Magic numbers used as thresholds/timeouts
    - Hardcoded filesystem paths
    - Suspicious float values (tax rates, multipliers)

    Allows:
    - Well-known constants (0, 1, -1, True, False, None, empty collections)
    - Well-known HTTP status codes, mathematical constants
    - Values assigned to named constants (variables)
    - Values in config files, tests, or fixture definitions
    """

    rule_id = "OC014"
    description = "No hardcoded configurable values (magic numbers, inline URLs, etc.)"
    severity = "warning"
    categories = ["config", "quality", "security"]

    URL_PATTERN = re.compile(r'https?://[^\s\'"]+|wss?://[^\s\'"]+')

    SUSPICIOUS_PORTS: Set[int] = {
        80, 443, 3000, 5000, 8000, 8080, 8443,
        5432, 3306, 6379, 27017,
    }

    THRESHOLD_MIN = 2
    THRESHOLD_MAX = 3600

    SKIP_PATTERNS: Set[str] = {
        "conftest", "config", "settings", ".env",
        "pyproject.toml", "requirements", "constraints",
    }

    SUSPICIOUS_FLOATS: Set[float] = {
        0.19, 0.21, 0.23, 0.25, 0.27,
        1.19, 1.21, 1.23, 1.25,
    }

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        if self._should_skip_file(file_path):
            return []

        violations = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, bool):
                    continue
                if isinstance(node.value, str):
                    violation = self._check_string(node, tree, file_path)
                    if violation:
                        violations.append(violation)
                elif isinstance(node.value, (int, float)):
                    violation = self._check_number(node, tree, file_path)
                    if violation:
                        violations.append(violation)

        return violations

    def _should_skip_file(self, file_path: Path) -> bool:
        path_str = str(file_path)
        for pattern in self.SKIP_PATTERNS:
            if pattern.lower() in path_str.lower():
                return True
        if "test" in path_str.lower():
            return True
        return False

    def _check_string(self, node: ast.Constant, tree: ast.AST, file_path: Path) -> Violation | None:
        value = node.value
        if not value:
            return None

        if self._is_safe_string_context(node, tree):
            return None

        if self.URL_PATTERN.search(value):
            return self._make_violation(node, file_path,
                f"Inline URL: '{value[:80]}' — move to config module",
                "Add to AppConfig in config/settings.py")

        if self._looks_like_port_value(value):
            return self._make_violation(node, file_path,
                f"Hardcoded port/address: '{value[:80]}' — move to config module",
                "Add to AppConfig and reference by attribute")

        if value.startswith('/') and not value.startswith(('/dev/', '/proc/')):
            return self._make_violation(node, file_path,
                f"Hardcoded path: '{value[:80]}' — move to config module",
                "Add to AppConfig and reference by attribute")

        return None

    def _check_number(self, node: ast.Constant, tree: ast.AST, file_path: Path) -> Violation | None:
        value = node.value

        if value in (0, 1, -1):
            return None

        if self._is_safe_numeric_context(node, tree):
            return None

        if isinstance(value, int):
            if value in self.SUSPICIOUS_PORTS:
                return self._make_violation(node, file_path,
                    f"Suspicious numeric value {value} (looks like a port) — move to config",
                    "Add to AppConfig and reference by attribute")

            if self.THRESHOLD_MIN < value < self.THRESHOLD_MAX and not self._is_well_known(value):
                return self._make_violation(node, file_path,
                    f"Potential magic number {value} — thresholds, timeouts, retries should be in config",  # noqa: E501
                    "Extract to a named constant in config module")

        elif isinstance(value, float):
            if any(abs(value - f) < 0.001 for f in self.SUSPICIOUS_FLOATS):
                return self._make_violation(node, file_path,
                    f"Suspicious float {value} (tax rate, multiplier?) — move to config",
                    "Add AppConfig field and reference by attribute")

        return None

    def _is_well_known(self, value: int) -> bool:
        return value in {
            2, 4, 8, 10, 16, 24, 32, 64, 100, 128, 256,
            200, 201, 204, 301, 302, 400, 401, 403, 404, 408,
            429, 500, 502, 503,
            60, 3600, 86400,
        }

    def _looks_like_port_value(self, value: str) -> bool:
        if re.search(r':\d{4,5}$', value):
            return True
        if value.isdigit() and len(value) >= 4 and len(value) <= 5:
            return False
        return False

    def _is_safe_string_context(self, node: ast.Constant, tree: ast.AST) -> bool:
        parent = self._get_parent(tree, node)
        if parent is None:
            return True

        if isinstance(parent, (ast.Import, ast.ImportFrom, ast.Module)):
            return True

        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return True

        if isinstance(parent, ast.AnnAssign):
            return True

        if isinstance(parent, ast.Assign):
            if self._is_module_level_constant(parent):
                return True
            return False

        if isinstance(parent, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
            return True

        if isinstance(parent, ast.Attribute):
            return True

        return False

    def _is_safe_numeric_context(self, node: ast.Constant, tree: ast.AST) -> bool:
        parent = self._get_parent(tree, node)
        if parent is None:
            return True

        if isinstance(parent, ast.Assign):
            return True

        if isinstance(parent, (ast.Subscript, ast.Slice)):
            return True

        if isinstance(parent, ast.keyword):
            return True

        if isinstance(parent, ast.AnnAssign):
            return True

        if isinstance(parent, (ast.arguments, ast.arg)):
            return True

        if isinstance(parent, ast.FunctionDef):
            return True

        if isinstance(parent, ast.AugAssign):
            return True

        if isinstance(parent, ast.Raise):
            return True

        return False

    def _get_parent(self, tree: ast.AST, target: ast.AST) -> ast.AST | None:
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child is target:
                    return node
        return None

    def _is_module_level_constant(self, node: ast.Assign) -> bool:
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id.isupper() and '_' in target.id:
                    return True
                if target.id.isupper() and len(target.id) > 1:
                    return True
        return False

    def _make_violation(
        self, node: ast.Constant, file_path: Path, message: str, fix: str
    ) -> Violation:
        return self._create_violation(
            file_path=file_path,
            line_number=getattr(node, 'lineno', 1),
            column=getattr(node, 'col_offset', 0),
            message=message + " (OC014 / Hardcoding Avoidance)",
            fix=fix,
        )
