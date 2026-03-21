"""Violation model for lint errors."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Violation:
    """Represents a single lint violation."""
    
    rule_id: str
    file_path: Path
    line_number: int
    column: int
    message: str
    severity: str  # "error" or "warning"
    fix: Optional[str] = None  # Suggested fix if available
    
    def __str__(self) -> str:
        severity_marker = "✗" if self.severity == "error" else "⚠"
        return (
            f"{severity_marker} {self.rule_id}: {self.file_path}:{self.line_number}:{self.column}\n"
            f"   {self.message}\n"
        )
    
    def to_dict(self) -> dict:
        """Convert violation to dictionary for serialization."""
        return {
            "rule_id": self.rule_id,
            "file_path": str(self.file_path),
            "line_number": self.line_number,
            "column": self.column,
            "message": self.message,
            "severity": self.severity,
            "fix": self.fix,
        }
