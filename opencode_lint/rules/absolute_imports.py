"""OC004: Absolute imports preferred.

Code organization rule from Factory.ai's "grep-ability" category.
Enforces: Use absolute imports instead of relative imports.
"""

import ast
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class AbsoluteImportsPreferred(Rule):
    """Rule OC004: Absolute imports preferred.
    
    Discourages:
    - from . import module
    - from .. import module
    - from .module import something
    - from ..module import something
    
    Encourages:
    - from myproject.module import something
    - import myproject.module
    
    Why: Absolute imports make code searchable and refactorable.
    Factory.ai's #1 recommendation for "grep-ability".
    """
    
    rule_id = "OC004"
    description = "Absolute imports preferred over relative imports"
    severity = "warning"
    categories = ["grep-ability", "code-organization"]
    
    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        """Check file for relative import violations."""
        violations = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # Check if this is a relative import
                if node.level > 0:
                    line_num = node.lineno
                    col = node.col_offset
                    
                    # Build the violation message
                    module_name = node.module or ""
                    dots = "." * node.level
                    
                    violations.append(
                        self._create_violation(
                            file_path=file_path,
                            line_number=line_num,
                            column=col,
                            message=(
                                f"Relative import detected: 'from {dots}{module_name} import ...'. "
                                f"Use absolute imports for better grep-ability. "
                                f"See AGENTS.md + Factory.ai: Grep-ability"
                            ),
                            fix=f"Replace with 'from project.{module_name} import ...'",
                        )
                    )
        
        return violations
