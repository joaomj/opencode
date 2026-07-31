"""OC-SKILL-CHECK: Validate skill description quality.

Checks:
- Every SKILL.md has a description in its frontmatter.
- Description uses "Use when..." or similar trigger language.
- Explicit-only skills have "explicitly" or "only when" in description.
- Description is not too short or unnecessarily verbose.
"""

import re
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation

_MIN_DESC_LENGTH = 20
_MAX_DESC_LENGTH = 600


class SkillDescriptions(Rule):
    """Rule OC-SKILL-CHECK: Skill description quality."""

    rule_id = "OC-SKILL-CHECK"
    description = "Skill descriptions must be clear, trigger-oriented, and well-formed"
    severity = "warning"
    categories = ["quality"]

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        """Check individual SKILL.md files."""
        violations: List[Violation] = []

        if file_path.name != "SKILL.md":
            return violations

        fm = self._parse_frontmatter(content)
        if fm is None:
            return violations

        name = fm.get("name", file_path.parent.name)
        description = fm.get("description", "")

        if not description:
            violations.append(self._create_violation(
                file_path=file_path,
                line_number=0,
                column=0,
                message=f"Skill '{name}' has no description in frontmatter.",
            ))
            return violations

        desc_len = len(description)

        if desc_len < _MIN_DESC_LENGTH:
            violations.append(self._create_violation(
                file_path=file_path,
                line_number=0,
                column=0,
                message=(
                    f"Skill '{name}' description is too short ({desc_len} chars, "
                    f"minimum {_MIN_DESC_LENGTH}). Add trigger-oriented detail."
                ),
            ))

        if desc_len > _MAX_DESC_LENGTH:
            violations.append(self._create_violation(
                file_path=file_path,
                line_number=0,
                column=0,
                message=(
                    f"Skill '{name}' description is very long ({desc_len} chars, "
                    f"maximum {_MAX_DESC_LENGTH}). Consider shortening to reduce context bloat."
                ),
            ))

        if not self._has_trigger_language(description):
            violations.append(self._create_violation(
                file_path=file_path,
                line_number=0,
                column=0,
                message=(
                    f"Skill '{name}' description should include trigger language "
                    "like 'Use when...' or 'Use for...'."
                ),
            ))

        # Check if the skill name suggests explicit-only but description doesn't say so
        if self._name_suggests_explicit(name) and not self._has_explicit_only_language(description):
            violations.append(self._create_violation(
                file_path=file_path,
                line_number=0,
                column=0,
                message=(
                    f"Skill '{name}' appears to be explicit-only (name suggests narrow scope) "
                    "but doesn't include 'only when explicitly asked' language."
                ),
            ))

        return violations

    def check_project(self, project_root: Path) -> List[Violation]:
        return []

    # ── helpers ──────────────────────────────────────────────

    def _parse_frontmatter(self, content: str) -> dict[str, str] | None:
        """Parse YAML frontmatter, handling folded (`>`) and literal (`|`) multiline values."""
        stripped = content.lstrip()
        if not stripped.startswith("---"):
            return None
        _, rest = stripped.split("---", 1)
        if "---" not in rest:
            return None
        fm_text, _ = rest.split("---", 1)

        result: dict[str, str] = {}
        current_key: str | None = None
        current_value: list[str] = []
        block_mode: str | None = None  # None, '>', '|'

        for line in fm_text.splitlines():
            # Check if this line starts a new key
            key_match = re.match(r"^(\w+):\s*(.*)$", line)
            if key_match is not None:
                # Save previous key
                if current_key is not None:
                    result[current_key] = self._join_block(current_value, block_mode)
                current_key = key_match.group(1)
                value_part = key_match.group(2).strip()
                current_value = [value_part] if value_part else []
                block_mode = None
                # Detect block indicator
                if value_part in (">", "|"):
                    block_mode = value_part
                    current_value = []
                continue

            # Continuation line for current key
            if current_key is not None:
                current_value.append(line.rstrip())

        if current_key is not None:
            result[current_key] = self._join_block(current_value, block_mode)

        return result

    def _join_block(self, lines: list[str], mode: str | None) -> str:
        """Join block scalar lines based on mode."""
        if not lines:
            return ""
        if mode == ">":
            # Folded: join with space
            return " ".join(lines)
        elif mode == "|":
            # Literal: join with newline
            return "\n".join(lines)
        else:
            # Simple single-line value
            return lines[0] if lines else ""

    def _has_trigger_language(self, description: str) -> bool:
        """Check for use-case trigger language."""
        triggers = [
            r"\bUse\s+(ONLY\s+)?(when|for|this|to)",
            r"\bApply\s+when",
            r"\bShould\s+be\s+used",
            r"\bLoaded\s+when",
            r"\bTrigger\s+when",
        ]
        return any(re.search(p, description) for p in triggers)

    def _has_explicit_only_language(self, description: str) -> bool:
        """Check for explicit-only constraint language."""
        markers = [
            "explicitly",
            "only when",
            "only if",
            "only when the user explicitly",
            "do not use unless",
        ]
        desc_lower = description.lower()
        return any(m in desc_lower for m in markers)

    def _name_suggests_explicit(self, name: str) -> bool:
        """Check if skill name suggests it should be explicit-only."""
        narrow_names = {
            "simplify", "research", "issue-writing",
            "create-pull-request", "doc-maintenance",
        }
        return name in narrow_names
