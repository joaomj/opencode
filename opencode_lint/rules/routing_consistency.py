"""OC-ROUTING: Validate AGENTS.md routing table against filesystem.

Checks:
- Every `Load <skill>` reference resolves to a skill (by frontmatter name or directory).
- Every `Use /command>` reference resolves to a command file.
- Every `Include the <gate>` reference matches a named gate section.
- Every skill directory in `skills/` is referenced (orphan warning).
- Every command file in `commands/` is referenced (orphan warning).
- Routing Determinism section exists in AGENTS.md.
- Skill directory name matches its frontmatter name (mismatch warning).
- Actions use only known verbs: Load, Use, Include.
"""

import re
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


_KNOWN_VERBS = {"Load", "Use", "Include"}


class RoutingConsistency(Rule):
    """Rule OC-ROUTING: AGENTS.md routing table consistency."""

    rule_id = "OC-ROUTING"
    description = "AGENTS.md routing table must match filesystem"
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

        content = agents_md.read_text(encoding="utf-8")

        sections = self._parse_sections(content)
        violations += self._check_routing_determinism_section(sections, agents_md)
        violations += self._check_routing_table(sections, agents_md, project_root)
        violations += self._check_command_table(sections, agents_md, project_root)

        return violations

    # ── helpers ──────────────────────────────────────────────

    def _parse_sections(self, content: str) -> dict[str, str]:
        """Split AGENTS.md into named sections by ## headings."""
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

    def _parse_table_rows(self, text: str) -> list[list[str]]:
        """Extract rows from a markdown table."""
        rows: list[list[str]] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("|--"):
                continue
            if stripped.startswith("|"):
                # Normalize: ensure trailing pipe, then split
                normalized = stripped if stripped.endswith("|") else stripped + "|"
                row = [
                    cell.strip()
                    for cell in normalized.strip("|").split("|")
                ]
                if row:
                    rows.append(row)
        return rows

    def _extract_actions(self, text: str) -> list[tuple[str, int]]:
        """Extract action phrases and their approximate line numbers."""
        actions: list[tuple[str, int]] = []
        rows = self._parse_table_rows(text)
        current_line_base = 0
        for row in rows:
            if len(row) >= 2:
                action = row[1]
                # Skip header rows
                if action.lower() in ("action",):
                    current_line_base += 1
                    continue
                actions.append((action, current_line_base))
            current_line_base += 1
        return actions

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

    def _find_command_names(self, project_root: Path) -> set[str]:
        """Return set of command names (without .md)."""
        commands_dir = project_root / "commands"
        if not commands_dir.exists():
            return set()
        return {
            f.stem
            for f in commands_dir.iterdir()
            if f.suffix == ".md"
        }

    def _parse_frontmatter_name(self, content: str) -> str | None:
        """Extract `name:` from YAML frontmatter."""
        match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def _find_load_references(self, action_text: str) -> list[str]:
        """Find Load `...` references in action text."""
        return re.findall(r"Load\s+`([^`]+)`", action_text)

    def _find_use_references(self, action_text: str) -> list[str]:
        """Find Use `/...` references in action text."""
        return re.findall(r"Use\s+`/?([^`]+)`", action_text)

    def _find_include_references(self, action_text: str) -> list[str]:
        """Find Include the <...> references."""
        return re.findall(r"Include\s+the\s+<([^>]+)>", action_text)

    def _find_gate_sections(self, content: str) -> list[str]:
        """Find ## ... Gate sections."""
        return [
            line[3:].strip()
            for line in content.splitlines()
            if line.startswith("## ") and "Gate" in line or "Gate" in line[3:]
        ]

    # ── checks ───────────────────────────────────────────────

    def _check_routing_determinism_section(
        self, sections: dict[str, str], agents_md: Path
    ) -> List[Violation]:
        violations: List[Violation] = []
        if "Routing Determinism" not in sections:
            violations.append(Violation(
                rule_id=self.rule_id,
                file_path=agents_md,
                line_number=0,
                column=0,
                message=(
                    "AGENTS.md is missing a '## Routing Determinism' section. "
                    "Add one to define ambiguity behavior."
                ),
                severity="warning",
            ))
        return violations

    def _check_routing_table(
        self, sections: dict[str, str], agents_md: Path, project_root: Path
    ) -> List[Violation]:
        violations: List[Violation] = []

        routing_text = sections.get("Skill Routing", "")
        if not routing_text:
            violations.append(self._create_violation(
                file_path=agents_md,
                line_number=0,
                column=0,
                message="No '## Skill Routing' section found in AGENTS.md",
            ))
            return violations

        local_skills = self._find_skill_names(project_root)
        local_commands = self._find_command_names(project_root)

        referenced_skills: set[str] = set()
        referenced_commands: set[str] = set()

        actions = self._extract_actions(routing_text)
        action_lines = routing_text.splitlines()

        for action_text, _ in actions:
            # Check Load references
            for skill_ref in self._find_load_references(action_text):
                referenced_skills.add(skill_ref)
                if skill_ref not in local_skills:
                    violations.append(self._create_violation(
                        file_path=agents_md,
                        line_number=0,
                        column=0,
                        message=(
                            f"Load `{skill_ref}`: no local skill found. "
                            "Check that skills/<name>/SKILL.md exists with matching frontmatter."
                        ),
                    ))

            # Check Use references (commands)
            for cmd_ref in self._find_use_references(action_text):
                referenced_commands.add(cmd_ref)
                if cmd_ref not in local_commands:
                    violations.append(self._create_violation(
                        file_path=agents_md,
                        line_number=0,
                        column=0,
                        message=(
                            f"Use `/{cmd_ref}`: no command file found. "
                            f"Check that commands/{cmd_ref}.md exists."
                        ),
                    ))

            # Check Include references (gates)
            for gate_ref in self._find_include_references(action_text):
                found = any(gate_ref.lower() in g.lower() for g in sections)
                if not found:
                    violations.append(self._create_violation(
                        file_path=agents_md,
                        line_number=0,
                        column=0,
                        message=(
                            f"Include the <{gate_ref}>: no matching section heading found in AGENTS.md."
                        ),
                    ))

            # Warn about unknown verbs
            has_known = False
            for verb in _KNOWN_VERBS:
                pattern = rf"\b{verb}\s+"
                if re.search(pattern, action_text):
                    has_known = True
                    break
            if not has_known and action_lines:
                violations.append(self._create_violation(
                    file_path=agents_md,
                    line_number=0,
                    column=0,
                    message=(
                        f"Routing action contains no known verb (Load/Use/Include): "
                        f"'{action_text[:80]}'"
                    ),
                    severity="warning",
                ))

        # Check for orphan skills
        for skill_name, dir_name in local_skills.items():
            if skill_name not in referenced_skills:
                violations.append(self._create_violation(
                    file_path=agents_md,
                    line_number=0,
                    column=0,
                    message=(
                        f"Orphan skill: 'skills/{dir_name}/' (frontmatter name '{skill_name}') "
                        "is not referenced in the Skill Routing table."
                    ),
                    severity="warning",
                ))

        # Check name/directory mismatches for skills
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

    def _check_command_table(
        self, sections: dict[str, str], agents_md: Path, project_root: Path
    ) -> List[Violation]:
        """Validate the Commands table references and detect orphans."""
        violations: List[Violation] = []
        commands_text = sections.get("Commands", "")
        if not commands_text:
            return violations

        local_commands = self._find_command_names(project_root)
        table_commands: set[str] = set()

        for row in self._parse_table_rows(commands_text):
            if len(row) < 2:
                continue
            cmd_cell = row[0].strip()
            match = re.match(r"`?(/[a-z][a-z0-9_-]*)`?", cmd_cell)
            if match:
                cmd_name = match.group(1).lstrip("/")
                table_commands.add(cmd_name)
                if cmd_name not in local_commands:
                    violations.append(self._create_violation(
                        file_path=agents_md,
                        line_number=0,
                        column=0,
                        message=(
                            f"Command '/{cmd_name}' in Commands table has no matching "
                            f"commands/{cmd_name}.md file."
                        ),
                        severity="warning",
                    ))

        # Check for orphan commands
        for cmd_name in local_commands:
            if cmd_name not in table_commands:
                violations.append(self._create_violation(
                    file_path=project_root / "commands" / f"{cmd_name}.md",
                    line_number=0,
                    column=0,
                    message=(
                        f"Orphan command: 'commands/{cmd_name}.md' "
                        "is not listed in the Commands table."
                    ),
                    severity="warning",
                ))

        return violations
