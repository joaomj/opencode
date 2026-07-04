"""OC-ROUTING: Validate AGENTS.md and skill directory structure.

Checks:
- AGENTS.md exists at project root.
- Skill directory names match their frontmatter name (mismatch warning).
"""

from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class RoutingConsistency(Rule):
    """Rule OC-ROUTING: Project structure consistency."""

    rule_id = "OC-ROUTING"
    description = "AGENTS.md and skill directory structure validation"
    severity = "error"
    categories = ["process"]

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        return []

    def check_project(self, project_root: Path) -> List[Violation]:
        violations: List[Violation] = []

        agents_md = project_root / "AGENTS.md"
        if not agents_md.exists():
            violations.append(self._create_violation(
                file_path=project_root,
                line_number=0,
                column=0,
                message="AGENTS.md not found at project root",
            ))
            return violations

        violations += self._check_skill_name_mismatches(project_root)

        return violations

    # ── helpers ──────────────────────────────────────────────

    def _find_skill_names(self, project_root: Path) -> dict[str, str]:
        """Return {frontmatter_name: directory_name} for local skills."""
        skills_dir = project_root / "skills"
        if not skills_dir.exists():
            return {}
        result: dict[str, str] = {}
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            content = skill_file.read_text(encoding="utf-8")
            fm_name = self._parse_frontmatter_name(content)
            result[fm_name or skill_dir.name] = skill_dir.name
        return result

    def _parse_frontmatter_name(self, content: str) -> str | None:
        """Extract `name:` from YAML frontmatter."""
        import re
        match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    # ── checks ───────────────────────────────────────────────

    def _check_skill_name_mismatches(
        self, project_root: Path
    ) -> List[Violation]:
        """Check name/directory mismatches for skills."""
        violations: List[Violation] = []
        local_skills = self._find_skill_names(project_root)

        for fm_name, dir_name in local_skills.items():
            if fm_name != dir_name:
                violations.append(self._create_violation(
                    file_path=project_root / "skills" / dir_name / "SKILL.md",
                    line_number=0,
                    column=0,
                    message=(
                        f"Skill directory '{dir_name}' differs from frontmatter name "
                        f"'{fm_name}'. Consider renaming the directory or the frontmatter name."
                    ),
                    severity="warning",
                ))

        return violations
