"""OC-DECISION: Validate material decision note structure and lifecycle."""

import re
from datetime import date
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation

_LIFECYCLES = {"proposed", "accepted", "rejected", "archived"}
_FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
_STATUS_RE = re.compile(r"^Status:\s*(proposed|accepted|rejected|archived)\s*$")
_REQUIRED_SECTIONS = {"Problem", "Why", "Alternatives", "Product impact", "Risks", "Approval"}


class DecisionNotes(Rule):
    """Rule OC-DECISION: Decision notes have a valid, reviewable format."""

    rule_id = "OC-DECISION"
    description = "Decision notes must use valid lifecycle, structure, and approval data"
    severity = "error"
    categories = ["process"]

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        return []

    def check_project(self, project_root: Path) -> List[Violation]:
        decisions_dir = project_root / ".agents" / "decisions"
        if not decisions_dir.exists():
            return []

        violations: List[Violation] = []
        for note_path in sorted(decisions_dir.rglob("*.md")):
            if note_path == decisions_dir / "README.md":
                continue
            try:
                content = note_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                violations.append(
                    self._create_violation(
                        file_path=note_path,
                        line_number=1,
                        column=1,
                        message=f"Decision note could not be read: {error}",
                    )
                )
                continue
            violations.extend(self._check_note(note_path, content, decisions_dir))
        return violations

    def _check_note(
        self,
        note_path: Path,
        content: str,
        decisions_dir: Path,
    ) -> List[Violation]:
        violations: List[Violation] = []
        relative_parts = note_path.relative_to(decisions_dir).parts

        if len(relative_parts) != 2 or relative_parts[0] not in _LIFECYCLES:
            violations.append(
                self._create_violation(
                    file_path=note_path,
                    line_number=1,
                    column=1,
                    message=(
                        "Decision note must be one Markdown file under "
                        ".agents/decisions/{proposed,accepted,rejected,archived}/."
                    ),
                )
            )
            return violations

        lifecycle = relative_parts[0]
        filename = relative_parts[1]
        if not _FILENAME_RE.fullmatch(filename):
            violations.append(
                self._create_violation(
                    file_path=note_path,
                    line_number=1,
                    column=1,
                    message="Decision note filename must be YYYY-MM-DD-lowercase-title.md.",
                )
            )
        else:
            try:
                date.fromisoformat(filename[:10])
            except ValueError:
                violations.append(
                    self._create_violation(
                        file_path=note_path,
                        line_number=1,
                        column=1,
                        message="Decision note filename contains an invalid calendar date.",
                    )
                )

        lines = content.splitlines()
        if not lines or not re.fullmatch(r"# Decision:\s+.+", lines[0]):
            violations.append(
                self._create_violation(
                    file_path=note_path,
                    line_number=1,
                    column=1,
                    message="Decision note must start with '# Decision: <title>'.",
                )
            )

        status_matches = [
            (line_number, _STATUS_RE.fullmatch(line))
            for line_number, line in enumerate(lines, start=1)
        ]
        status_entry = next(((number, match) for number, match in status_matches if match), None)
        if status_entry is None:
            violations.append(
                self._create_violation(
                    file_path=note_path,
                    line_number=1,
                    column=1,
                    message="Decision note must contain one valid Status line.",
                )
            )
            status = None
        else:
            status_line, status_match = status_entry
            status = status_match.group(1)
            if status != lifecycle:
                violations.append(
                    self._create_violation(
                        file_path=note_path,
                        line_number=status_line,
                        column=1,
                        message=f"Status '{status}' must match lifecycle folder '{lifecycle}'.",
                    )
                )

        owner_line = next(
            (
                line_number
                for line_number, line in enumerate(lines, start=1)
                if re.fullmatch(r"Owner:\s*.+", line)
            ),
            None,
        )
        if owner_line is None:
            violations.append(
                self._create_violation(
                    file_path=note_path,
                    line_number=1,
                    column=1,
                    message="Decision note must contain a non-empty Owner line.",
                )
            )

        sections = self._parse_sections(lines)
        required_sections = set(_REQUIRED_SECTIONS)
        if status in {"proposed", "rejected"}:
            required_sections.add("Recommendation")
        elif status == "accepted":
            required_sections.add("Decision")
        elif status == "archived":
            if "Decision" not in sections and "Recommendation" not in sections:
                required_sections.add("Decision")

        for section in sorted(required_sections):
            if section not in sections or not sections[section].strip():
                violations.append(
                    self._create_violation(
                        file_path=note_path,
                        line_number=1,
                        column=1,
                        message=f"Decision note must contain a non-empty '## {section}' section.",
                    )
                )

        if status == "accepted":
            approval = sections.get("Approval", "")
            if not re.search(r"\bapproved\s+by\b", approval, re.IGNORECASE):
                violations.append(
                    self._create_violation(
                        file_path=note_path,
                        line_number=1,
                        column=1,
                        message="Accepted decision notes must state who approved the decision.",
                    )
                )

        return violations

    def _parse_sections(self, lines: List[str]) -> dict[str, str]:
        sections: dict[str, list[str]] = {}
        current: str | None = None
        for line in lines:
            heading = re.fullmatch(r"##\s+(.+)", line)
            if heading:
                current = heading.group(1).strip()
                sections[current] = []
            elif current is not None:
                sections[current].append(line)
        return {name: "\n".join(body) for name, body in sections.items()}
