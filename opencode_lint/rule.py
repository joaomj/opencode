"""Base Rule class for lint rules."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Set

from opencode_lint.violation import Violation


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
        self.exclude_patterns: Set[str] = set(
            self.config.get("exclude", [])
        )
    
    @abstractmethod
    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        """Check a file for violations of this rule.
        
        Args:
            file_path: Path to the file being checked
            content: File content as string
            
        Returns:
            List of violations found
        """
        pass
    
    def should_check_file(self, file_path: Path) -> bool:
        """Determine if this rule applies to the given file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if rule should check this file
        """
        if not self.enabled:
            return False
        
        # Check exclude patterns
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
    ) -> Violation:
        """Helper to create a violation for this rule."""
        return Violation(
            rule_id=self.rule_id,
            file_path=file_path,
            line_number=line_number,
            column=column,
            message=message,
            severity=self.severity,
            fix=fix,
        )
