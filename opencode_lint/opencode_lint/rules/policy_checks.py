"""Objective policy checks that do not require a language parser."""

import re
import shutil
import subprocess
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation

TEXT_SUFFIXES = frozenset({".md", ".py", ".rst", ".sh", ".toml", ".txt", ".yml", ".yaml"})


class SuppressionPolicy(Rule):
    """Reject broad static-analysis suppressions."""

    rule_id = "LNT004"
    description = "Broad checker suppressions must not hide findings"
    severity = "error"
    categories = ["policy", "quality"]

    BROAD_NOQA_RE = re.compile(r"#\s*noqa\s*(?::\s*)?$", re.IGNORECASE)
    BROAD_TYPE_IGNORE_RE = re.compile(r"#\s*type:\s*ignore(?:\s|$)", re.IGNORECASE)

    def should_check_file(self, file_path: Path) -> bool:
        return super().should_check_file(file_path) and file_path.suffix.lower() in TEXT_SUFFIXES

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        violations: List[Violation] = []
        for line_number, line in enumerate(content.splitlines(), 1):
            if self.BROAD_NOQA_RE.search(line) or self.BROAD_TYPE_IGNORE_RE.search(line):
                violations.append(
                    self._create_violation(
                        file_path,
                        line_number,
                        0,
                        (
                            "Broad checker suppression detected; use a targeted code "
                            "and an approved reason."
                        ),
                    )
                )
        return violations


class TestSuppressionPolicy(Rule):
    """Require explicit reasons for skipped or expected-failure tests."""

    rule_id = "LNT005"
    description = "Test skips and expected failures require explicit reasons"
    severity = "error"
    categories = ["policy", "testing"]
    DECORATOR_RE = re.compile(r"pytest\.mark\.(skip|xfail)(?:if)?(?:\(([^)]*)\))?", re.IGNORECASE)
    EMPTY_CALL_RE = re.compile(r"pytest\.(?:skip|xfail)\s*\(\s*\)", re.IGNORECASE)

    def should_check_file(self, file_path: Path) -> bool:
        return super().should_check_file(file_path) and file_path.suffix.lower() == ".py"

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        violations: List[Violation] = []
        for line_number, line in enumerate(content.splitlines(), 1):
            for match in self.DECORATOR_RE.finditer(line):
                arguments = match.group(2) or ""
                if "reason" not in arguments.lower():
                    violations.append(
                        self._create_violation(
                            file_path,
                            line_number,
                            match.start(),
                            "Skipped and expected-failure tests require an explicit reason.",
                        )
                    )
            if self.EMPTY_CALL_RE.search(line):
                violations.append(
                    self._create_violation(
                        file_path,
                        line_number,
                        0,
                        "Skipped and expected-failure tests require an explicit reason.",
                    )
                )
        return violations


class MechanicalWriting(Rule):
    """Report objective writing violations in durable text artifacts."""

    rule_id = "LNT020"
    description = "Durable text artifacts follow configured mechanical writing rules"
    severity = "warning"
    categories = ["quality", "documentation"]
    EM_DASH_RE = re.compile("\\u2014")
    EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF]")

    def should_check_file(self, file_path: Path) -> bool:
        return super().should_check_file(file_path) and file_path.suffix.lower() in {
            ".md",
            ".rst",
            ".txt",
        }

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        violations: List[Violation] = []
        for line_number, line in enumerate(content.splitlines(), 1):
            em_dash = self.EM_DASH_RE.search(line)
            if em_dash:
                violations.append(
                    self._create_violation(
                        file_path,
                        line_number,
                        em_dash.start(),
                        "Use a comma, colon, or separate sentence instead of an em dash.",
                    )
                )
            emoji = self.EMOJI_RE.search(line)
            if emoji:
                violations.append(
                    self._create_violation(
                        file_path,
                        line_number,
                        emoji.start(),
                        "Do not use emoji in durable project artifacts.",
                    )
                )
        return violations


class AgentArtifactCommit(Rule):
    """Reject staged local agent artifacts and plan files."""

    rule_id = "LNT025"
    description = "Local agent artifacts and plan files must not be committed"
    severity = "error"
    categories = ["policy", "security"]

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        return []

    def check_project(self, project_root: Path) -> List[Violation]:
        if not (project_root / ".git").exists():
            return []
        staged_paths = self._staged_paths(project_root)
        return [
            self._artifact_violation(project_root, staged_path)
            for staged_path in staged_paths
            if self._is_protected_path(staged_path)
        ]

    def _staged_paths(self, project_root: Path) -> List[Path]:
        """Return staged paths from the repository."""
        git = shutil.which("git")
        if git is None:
            raise RuntimeError("Git is required to inspect staged paths")
        result = subprocess.run(  # noqa: S603
            [git, "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or f"git exited with code {result.returncode}"
            raise RuntimeError(f"could not inspect staged paths: {detail}")
        return [Path(path) for path in result.stdout.splitlines() if path]

    def _is_protected_path(self, staged_path: Path) -> bool:
        """Return whether a staged path is a local-only artifact."""
        normalized = staged_path.as_posix().lower()
        name = staged_path.name.lower()
        in_agent_directory = normalized == ".agents" or normalized.startswith(".agents/")
        in_plan_directory = any(part.lower() == "plans" for part in staged_path.parts)
        is_plan_name = (
            name == "plan.md"
            or name.endswith("-plan.md")
            or (name.startswith("plan-") and name.endswith(".md"))
        )
        return in_agent_directory or in_plan_directory or is_plan_name

    def _artifact_violation(self, project_root: Path, staged_path: Path) -> Violation:
        """Create a violation for a protected staged path."""
        return self._create_violation(
            project_root / staged_path,
            0,
            0,
            "Agent artifacts and plan files are local-only and must not be staged.",
        )
