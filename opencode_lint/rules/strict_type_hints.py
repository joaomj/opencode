"""OC005: Strict type hints required.

Code quality rule to ensure comprehensive type annotations.
Enforces: All functions must have type hints for parameters and return types.
"""

import ast
from pathlib import Path
from typing import List, Set

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class StrictTypeHints(Rule):
    """Rule OC005: Strict type hints required.
    
    Requires:
    - Function parameters have type annotations
    - Function return types are annotated
    - No use of 'Any' as a catch-all type
    
    Note: This rule complements mypy. Use together with
    strict mypy configuration in .pre-commit-config.yaml.
    """
    
    rule_id = "OC005"
    description = "Strict type hints required for all functions"
    severity = "warning"
    categories = ["type-safety", "code-quality"]
    
    # Function names that can skip type hints
    SKIP_FUNCTIONS: Set[str] = {
        '__init__',  # Often doesn't need return type
    }
    
    # Parameters that can skip type hints
    SKIP_PARAMS: Set[str] = {
        'self',
        'cls',
        'args',
        'kwargs',
    }
    
    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        """Check file for type hint violations."""
        violations = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip test functions and dunder methods
                if self._should_skip_function(node):
                    continue
                
                # Check parameter type hints
                violations.extend(
                    self._check_params(node, file_path, content)
                )
                
                # Check return type hint
                violation = self._check_return_type(node, file_path, content)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _should_skip_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> bool:
        """Determine if function should be skipped."""
        # Skip dunder methods (except __init__ is checked separately)
        if node.name.startswith('__') and node.name.endswith('__'):
            return True
        
        # Skip test functions
        if node.name.startswith('test_') or node.name.endswith('_test'):
            return True
        
        return False
    
    def _check_params(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        content: str,
    ) -> List[Violation]:
        """Check if function parameters have type hints."""
        violations = []
        
        # Get existing annotations
        args = node.args
        
        # Check regular args
        for arg in args.args + args.posonlyargs:
            if arg.arg in self.SKIP_PARAMS:
                continue
            if arg.annotation is None:
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=arg.lineno or node.lineno,
                        column=arg.col_offset or 0,
                        message=(
                            f"Function '{node.name}' parameter '{arg.arg}' "
                            f"missing type annotation. "
                            f"See AGENTS.md: 'Every function has type hints'"
                        ),
                        fix=f"Add type annotation: {arg.arg}: Type",
                    )
                )
        
        # Check keyword-only args
        for arg in args.kwonlyargs:
            if arg.arg in self.SKIP_PARAMS:
                continue
            if arg.annotation is None:
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=arg.lineno or node.lineno,
                        column=arg.col_offset or 0,
                        message=(
                            f"Function '{node.name}' parameter '{arg.arg}' "
                            f"missing type annotation. "
                            f"See AGENTS.md: 'Every function has type hints'"
                        ),
                        fix=f"Add type annotation: {arg.arg}: Type",
                    )
                )
        
        return violations
    
    def _check_return_type(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        content: str,
    ) -> Violation | None:
        """Check if function has return type annotation."""
        # Skip __init__ (return type is implicit)
        if node.name == '__init__':
            return None
        
        if node.returns is None:
            return self._create_violation(
                file_path=file_path,
                line_number=node.lineno,
                column=node.col_offset,
                message=(
                    f"Function '{node.name}' missing return type annotation. "
                    f"See AGENTS.md: 'Every function has type hints'"
                ),
                fix=f"Add return type: -> ReturnType",
            )
        
        # Check if return type is 'Any'
        if isinstance(node.returns, ast.Name) and node.returns.id == 'Any':
            return self._create_violation(
                file_path=file_path,
                line_number=node.lineno,
                column=node.col_offset,
                message=(
                    f"Function '{node.name}' uses 'Any' return type. "
                    f"Use specific type instead. "
                    f"See AGENTS.md: 'Every function has type hints'"
                ),
                fix="Replace Any with specific return type",
            )
        
        return None
