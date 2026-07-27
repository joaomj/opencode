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

    def _find_skill_names(self, project_root: Path) -> dict[str, Path]:
        """Return {frontmatter_name: skill_directory} for local skills."""
        skills_dir = project_root / "skills"
        if not skills_dir.exists():
            return {}
        result: dict[str, Path] = {}
        for skill_file in skills_dir.rglob("SKILL.md"):
            relative_parts = skill_file.relative_to(skills_dir).parts
            if any(part.startswith(".") for part in relative_parts):
                continue
            skill_dir = skill_file.parent
            content = skill_file.read_text(encoding="utf-8")
            fm_name = self._parse_frontmatter_name(content)
            result[fm_name or skill_dir.name] = skill_dir
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

        for fm_name, skill_dir in local_skills.items():
            if fm_name != skill_dir.name:
                violations.append(self._create_violation(
                    file_path=skill_dir / "SKILL.md",
                    line_number=0,
                    column=0,
                    message=(
                        f"Skill directory '{skill_dir.name}' differs from frontmatter name "
                        f"'{fm_name}'. Consider renaming the directory or the frontmatter name."
                    ),
                    severity="warning",
                ))

        return violations
