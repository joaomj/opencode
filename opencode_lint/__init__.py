"""OpenCode Lint - Custom linter for repository policies.

This package encodes repository policies as machine-checkable rules.
"""

__version__ = "1.0.0"

from opencode_lint.rule import Rule
from opencode_lint.runner import LinterRunner
from opencode_lint.violation import Violation

__all__ = ["Violation", "Rule", "LinterRunner"]
