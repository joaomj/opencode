"""Base Rule class for lint rules."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Set

from opencode_lint.violation import Violation

NON_CODE_SUFFIXES = frozenset({".md", ".mdx", ".rst", ".txt", ".toml", ".yml", ".yaml"})
SECURITY_CATEGORIES = frozenset({"security", "supply-chain"})


class Rule(ABC):
    """Base class for all lint rules."""

    rule_id: str = ""
    description: str = ""
    severity: str = "error"  # "error" or "warning"
    categories: List[str] = []

    def __init__(self, config: Optional[dict] = None):
        """Initialize rule with optional configuration."""
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.severity = self.config.get("severity", self.severity)
        self.severity_configured = "severity" in self.config
        self.exclude_patterns: Set[str] = set(self.config.get("exclude", []))

    @abstractmethod
    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        """Check a single file for violations of this rule.

        Args:
            file_path: Path to the file being checked
            content: File content as string

        Returns:
            List of violations found
        """
        pass

    def check_project(self, project_root: Path) -> List[Violation]:
        """Check project-level structure (not individual files).

        Override this for rules that need to validate repo-wide
        consistency (routing tables, registry sync, etc.).

        Args:
            project_root: The project root directory

        Returns:
            List of violations found
        """
        return []

    def should_check_file(self, file_path: Path) -> bool:
        """Determine if this rule applies to the given file.

        Args:
            file_path: Path to check

        Returns:
            True if rule should check this file
        """
        if not self.enabled:
            return False

        path_str = str(file_path)
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return False

        return True

    def _create_violation(
        self,
        file_path: Path,
        line_number: int,
        column: int,
        message: str,
        fix: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> Violation:
        """Helper to create a violation for this rule.

        Args:
            severity: Override the rule's default severity if provided.
        """
        effective_severity = severity or self.severity
        if (
            severity is None
            and not self.severity_configured
            and effective_severity == "error"
            and file_path.suffix.lower() in NON_CODE_SUFFIXES
            and not SECURITY_CATEGORIES.intersection(self.categories)
        ):
            effective_severity = "warning"

        return Violation(
            rule_id=self.rule_id,
            file_path=file_path,
            line_number=line_number,
            column=column,
            message=message,
            severity=effective_severity,
            fix=fix,
        )
