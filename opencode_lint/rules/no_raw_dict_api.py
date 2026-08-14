"""OC001: No raw dicts for API schemas.

Type safety rule for API endpoints.
Enforces: Use Pydantic models instead of raw dict for API responses.
"""

import ast
from pathlib import Path
from typing import List, Set

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class NoRawDictAPISchema(Rule):
    """Rule OC001: No raw dicts for API schemas.

    Prevents:
    - FastAPI: def endpoint() -> dict
    - Flask: return {"key": value} (when function returns dict type)
    - Django: JsonResponse with dict (in typed functions)

    Requires:
    - FastAPI: def endpoint() -> PydanticModel
    - Proper Pydantic model definitions

    Why: Raw dicts bypass Pydantic validation, type safety,
    and OpenAPI generation. Common LLM mistake.
    """

    rule_id = "OC001"
    description = "No raw dicts for API schemas"
    severity = "error"
    categories = ["type-safety", "api", "pydantic"]

    # Framework decorators that indicate API endpoints
    API_DECORATORS: Set[str] = {
        'get', 'post', 'put', 'delete', 'patch',  # FastAPI
        'route', 'app.route',  # Flask
        'api_view',  # DRF
    }

    # Functions that should not return raw dicts
    TYPED_API_INDICATORS: Set[str] = {
        'jsonify', 'JSONResponse', 'JsonResponse',
    }

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        """Check file for raw dict API schema violations."""
        violations = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Check function return type annotation
                violation = self._check_function_return_type(node, file_path, content)
                if violation:
                    violations.append(violation)

                # Check return statements in the function
                violations.extend(
                    self._check_return_statements(node, file_path, content)
                )

        return violations

    def _check_function_return_type(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        content: str,
    ) -> Violation | None:
        """Check if function has -> dict return type annotation."""
        # Check if this is an API endpoint
        if not self._is_api_endpoint(node):
            return None

        # Check return type annotation
        if node.returns:
            if self._is_dict_type(node.returns):
                line_num = node.lineno
                col = node.col_offset
                return self._create_violation(
                    file_path=file_path,
                    line_number=line_num,
                    column=col,
                    message=(
                        f"API endpoint '{node.name}' returns raw dict. "
                        f"Use a Pydantic model instead. "
                         "Project policy: use typed API schemas instead of raw dictionaries."
                    ),
                    fix=f"Define a Pydantic model for {node.name} response",
                )

        return None

    def _check_return_statements(
        self,
        func_node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        content: str,
    ) -> List[Violation]:
        """Check return statements in API endpoint functions."""
        violations = []

        if not self._is_api_endpoint(func_node):
            return violations

        # Find all return statements in the function
        for node in ast.walk(func_node):
            if isinstance(node, ast.Return) and node.value:
                # Check if returning a dict literal
                if isinstance(node.value, ast.Dict):
                    # Check if function has explicit dict return type or no return type
                    if func_node.returns is None or self._is_dict_type(func_node.returns):
                        line_num = node.lineno
                        col = node.col_offset
                        violations.append(
                            self._create_violation(
                                file_path=file_path,
                                line_number=line_num,
                                column=col,
                                message=(
                                    f"API endpoint '{func_node.name}' returns dict literal. "
                                    f"Use a Pydantic model instead. "
                                     "Project policy: use typed API schemas instead of "
                                     "raw dictionaries."
                                ),
                                fix="Create Pydantic model and return model instance",
                            )
                        )

        return violations

    def _is_api_endpoint(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if function is an API endpoint based on decorators."""
        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name:
                # Check if decorator name indicates API endpoint
                base_name = decorator_name.split('.')[-1].split('(')[0]
                if base_name in self.API_DECORATORS:
                    return True
                # Check for FastAPI router patterns
                if any(x in decorator_name for x in ['.get(', '.post(', '.put(', '.delete(']):
                    return True
        return False

    def _get_decorator_name(self, decorator: ast.expr) -> str | None:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_attribute_chain(decorator)}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{self._get_attribute_chain(decorator.func)}"
        return None

    def _get_attribute_chain(self, node: ast.Attribute) -> str:
        """Get full attribute chain (e.g., 'router.get')."""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))

    def _is_dict_type(self, node: ast.expr) -> bool:
        """Check if AST node represents a dict type annotation."""
        if isinstance(node, ast.Name) and node.id == 'dict':
            return True
        if isinstance(node, ast.Constant) and node.value is dict:
            return True
        # Check for Dict from typing
        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name):
                if node.value.id in ('Dict', 'dict'):
                    return True
        return False
