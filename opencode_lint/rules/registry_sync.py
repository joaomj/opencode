"""OC-REGISTRY: Validate rule implementations.

Rules are documented in opencode_lint/rules/ directly.
The AGENTS.md rules table has been removed.
"""

import ast
import re
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class RegistrySync(Rule):
    """Rule OC-REGISTRY: AGENTS.md rules table sync with filesystem."""

    rule_id = "OC-REGISTRY"
    description = "AGENTS.md rules table must match rule implementations"
    severity = "error"
    categories = ["process"]

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        return []

    def check_project(self, project_root: Path) -> List[Violation]:
        # The rules table was removed from AGENTS.md.
        # Rules are now documented in opencode_lint/rules/ directly.
        return []

    # ── helpers ──────────────────────────────────────────────

    def _parse_sections(self, content: str) -> dict[str, str]:
        sections: dict[str, str] = {}
        current_name = ""
        current_lines: list[str] = []
        for line in content.splitlines():
            if line.startswith("## "):
                if current_name:
                    sections[current_name] = "\n".join(current_lines)
                current_name = line[3:].strip()
                current_lines = []
            elif current_name:
                current_lines.append(line)
        if current_name:
            sections[current_name] = "\n".join(current_lines)
        return sections

    def _parse_rules_table(self, text: str) -> list[dict[str, str]]:
        """Parse the Rules markdown table into structured rows.

        Returns list of dicts with keys: id, title, file.
        """
        rows: list[dict[str, str]] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("|--"):
                continue
            if stripped.startswith("|") and stripped.endswith("|"):
                cells = [cell.strip() for cell in stripped.strip("|").split("|")]
                if len(cells) >= 3:
                    # Extract file reference: `filename.py` or descriptive text
                    file_cell = cells[2]
                    file_match = re.match(r"`([^`]+)`", file_cell)
                    file_ref = file_match.group(1) if file_match else file_cell
                    rows.append({
                        "id": cells[0],
                        "title": cells[1],
                        "file": file_ref,
                        "is_backtick": file_match is not None,
                    })
        return rows

    def _find_rule_files(self, project_root: Path) -> list[Path]:
        """Find all .py files in opencode_lint/rules/ with a Rule subclass."""
        rules_dir = project_root / "opencode_lint" / "rules"
        if not rules_dir.exists():
            return []
        rule_files: list[Path] = []
        for f in sorted(rules_dir.iterdir()):
            if f.suffix != ".py" or f.name == "__init__.py":
                continue
            if self._file_has_rule_subclass(f):
                rule_files.append(f)
        return rule_files

    def _file_has_rule_subclass(self, file_path: Path) -> bool:
        """Check if a Python file contains a class that inherits from Rule."""
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError:
            return False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Rule":
                        return True
                    if isinstance(base, ast.Attribute) and base.attr == "Rule":
                        return True
        return False

    def _extract_rule_id_from_file(self, file_path: Path) -> str | None:
        """Extract the `rule_id` string from a rule file using AST."""
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError:
            return None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == "rule_id":
                                if isinstance(item.value, ast.Constant):
                                    return str(item.value.value)
        return None

    def _extract_severity_from_file(self, file_path: Path) -> str | None:
        """Extract the `severity` string from a rule file using AST."""
        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError:
            return None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == "severity":
                                if isinstance(item.value, ast.Constant):
                                    return str(item.value.value)
        return None

    # ── checks ───────────────────────────────────────────────

    def _check_table_files_exist(
        self,
        table_rules: list[dict[str, str]],
        agents_md: Path,
        project_root: Path,
    ) -> List[Violation]:
        violations: List[Violation] = []
        rules_base = project_root / "opencode_lint" / "rules"

        for rule in table_rules:
            if not rule["is_backtick"]:
                # Process-rule description, not a file reference
                continue
            file_path = rules_base / rule["file"]
            if not file_path.exists():
                # Try just the filename (the table may use relative paths)
                if not file_path.exists():
                    violations.append(self._create_violation(
                        file_path=agents_md,
                        line_number=0,
                        column=0,
                        message=(
                            f"Rule {rule['id']}: file '{rule['file']}' not found "
                            f"at opencode_lint/rules/{rule['file']}"
                        ),
                    ))

        return violations

    def _check_file_ids_match(
        self,
        table_rules: list[dict[str, str]],
        agents_md: Path,
        project_root: Path,
    ) -> List[Violation]:
        violations: List[Violation] = []
        rules_base = project_root / "opencode_lint" / "rules"

        for rule in table_rules:
            if not rule["is_backtick"]:
                continue
            file_path = rules_base / rule["file"]
            if not file_path.exists():
                continue
            actual_id = self._extract_rule_id_from_file(file_path)
            if actual_id and actual_id != rule["id"]:
                violations.append(self._create_violation(
                    file_path=file_path,
                    line_number=0,
                    column=0,
                    message=(
                        f"Rule ID mismatch: table says '{rule['id']}' "
                        f"but file defines rule_id='{actual_id}'"
                    ),
                ))

        return violations

    def _check_unlisted_rules(
        self,
        table_rules: list[dict[str, str]],
        rule_files: list[Path],
        agents_md: Path,
        project_root: Path,
    ) -> List[Violation]:
        violations: List[Violation] = []

        table_ids = {r["id"] for r in table_rules}

        for file_path in rule_files:
            rule_id = self._extract_rule_id_from_file(file_path)
            if rule_id and rule_id not in table_ids:
                violations.append(self._create_violation(
                    file_path=file_path,
                    line_number=0,
                    column=0,
                    message=(
                        f"Rule '{rule_id}' in {file_path.name} is not listed "
                        "in AGENTS.md Rules table."
                    ),
                ))

        return violations
