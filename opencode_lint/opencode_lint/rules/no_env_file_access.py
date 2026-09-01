"""OC002: Never view .env content.

Security rule to prevent agents from reading .env files directly.
Enforces: Use proper env access via os.getenv() or pydantic-settings.
"""

import ast
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class NoEnvFileAccess(Rule):
    """Rule OC002: Never view .env content.

    Prevents:
    - open(".env").read()
    - Path(".env").read_text()
    - with open(".env") as f: ...
    - etc.

    Allows:
    - load_dotenv() from python-dotenv
    - os.getenv("KEY")
    - pydantic-settings BaseSettings
    """

    rule_id = "OC002"
    description = "Never view .env content directly"
    severity = "error"
    categories = ["security"]

    # Patterns that indicate direct .env access
    VIOLATION_PATTERNS = [
        ".env",
        ".env.local",
        ".env.production",
        ".env.development",
        ".env.test",
    ]

    # Safe patterns that are allowed
    SAFE_FUNCTIONS = [
        "load_dotenv",
        "dotenv_values",
        "find_dotenv",
    ]
    PATH_SEPARATOR = "/"

    def should_check_file(self, file_path: Path) -> bool:
        """Only parse Python source files with the AST-based rule."""
        return super().should_check_file(file_path) and file_path.suffix.lower() == ".py"

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        """Check file for .env access violations."""
        tree = ast.parse(content)
        violations: List[Violation] = []
        for node in ast.walk(tree):
            violations.extend(self._check_call(node, tree, file_path))
            violation = self._check_constant(node, tree, file_path)
            if violation:
                violations.append(violation)

        return violations

    def _check_call(self, node: ast.AST, tree: ast.AST, file_path: Path) -> List[Violation]:
        """Check calls that can read environment files."""
        if not isinstance(node, ast.Call):
            return []
        violations = [self._check_open_call(node, file_path)]
        violations.append(self._check_path_methods(node, tree, file_path))
        return [violation for violation in violations if violation]

    def _check_constant(self, node: ast.AST, tree: ast.AST, file_path: Path) -> Violation | None:
        """Check string literals used as direct environment-file paths."""
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            return None
        if not self._is_env_file_path(node.value):
            return None
        parent = self._get_parent_context(tree, node)
        if not parent or not self._is_suspicious_context(parent):
            return None
        return self._create_violation(
            file_path=file_path,
            line_number=getattr(node, "lineno", 1),
            column=getattr(node, "col_offset", 0),
            message=(
                f"Direct .env file reference detected: '{node.value}'. "
                f"Use os.getenv() or pydantic-settings instead. "
                "Project policy: never view .env content directly."
            ),
            fix="Use os.getenv('KEY') or BaseSettings from pydantic-settings",
        )

    def _check_open_call(self, node: ast.Call, file_path: Path) -> Violation | None:
        """Check for open(".env", ...) calls."""
        if not isinstance(node.func, ast.Name) or node.func.id != "open":
            return None

        if not node.args:
            return None

        first_arg = node.args[0]
        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
            if self._is_env_file_path(first_arg.value):
                line_num = getattr(node, "lineno", 1)
                col = getattr(node, "col_offset", 0)
                return self._create_violation(
                    file_path=file_path,
                    line_number=line_num,
                    column=col,
                    message=(
                        f"Direct .env file access with open(): '{first_arg.value}'. "
                        f"Use os.getenv() or pydantic-settings instead. "
                        "Project policy: never view .env content directly."
                    ),
                    fix="Use os.getenv('KEY') or BaseSettings from pydantic-settings",
                )

        return None

    def _check_path_methods(
        self, node: ast.Call, tree: ast.AST, file_path: Path
    ) -> Violation | None:
        """Check for Path(".env").read_text() or similar."""
        if not isinstance(node.func, ast.Attribute):
            return None

        method_name = node.func.attr
        if method_name not in ["read_text", "read_bytes", "open"]:
            return None

        # Check if parent is Path(".env")
        parent_node = self._get_parent_context(tree, node)
        if isinstance(parent_node, ast.Call):
            if isinstance(parent_node.func, ast.Name) and parent_node.func.id == "Path":
                if parent_node.args and isinstance(parent_node.args[0], ast.Constant):
                    path_value = parent_node.args[0].value
                    if isinstance(path_value, str) and self._is_env_file_path(path_value):
                        line_num = getattr(node, "lineno", 1)
                        col = getattr(node, "col_offset", 0)
                        return self._create_violation(
                            file_path=file_path,
                            line_number=line_num,
                            column=col,
                            message=(
                                f"Direct .env file access via Path: '{path_value}'. "
                                f"Use os.getenv() or pydantic-settings instead. "
                                "Project policy: never view .env content directly."
                            ),
                            fix="Use os.getenv('KEY') or BaseSettings from pydantic-settings",
                        )

        return None

    def _is_env_file_path(self, path: str | None) -> bool:
        """Check if path is a .env file."""
        if not isinstance(path, str):
            return False
        path_lower = path.lower()
        return any(
            path_lower == pattern or path_lower.endswith(f"{self.PATH_SEPARATOR}{pattern}")
            for pattern in self.VIOLATION_PATTERNS
        )

    def _is_suspicious_context(self, parent: ast.AST) -> bool:
        """Check if parent context is suspicious (e.g., not load_dotenv, not a list)."""
        # Skip if in a list/tuple definition (likely just data patterns like VIOLATION_PATTERNS)
        if isinstance(parent, (ast.List, ast.Tuple, ast.Set)):
            return False

        # Skip if in a dict key/value (likely just data)
        if isinstance(parent, ast.Dict):
            return False

        # Skip if it's an assignment target (like VIOLATION_PATTERNS = [...])
        if isinstance(parent, ast.Assign):
            return False

        # Skip if calling a safe function
        if isinstance(parent, ast.Call):
            if isinstance(parent.func, ast.Name):
                if parent.func.id in self.SAFE_FUNCTIONS:
                    return False

        return True

    def _get_parent_context(self, tree: ast.AST, target_node: ast.AST) -> ast.AST | None:
        """Find the parent node of target_node in the AST."""
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                if child is target_node:
                    return node
        return None
