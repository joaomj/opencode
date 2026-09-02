"""Python changed-code budget checks."""

import ast
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation

PRODUCTION_LIMITS = {
    "function_lines": 60,
    "file_lines": 400,
    "arguments": 6,
    "nesting": 4,
    "complexity": 10,
}
TEST_LIMITS = {
    "function_lines": 100,
    "file_lines": 800,
    "nesting": 4,
    "complexity": 10,
}
CONTROL_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try)


class PythonBudgets(Rule):
    """Enforce the accepted Python production and test size limits."""

    rule_id = "LNT-PY-BUDGET"
    description = "Changed Python code stays within accepted complexity and size budgets"
    severity = "error"
    categories = ["quality", "python"]

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        return []

    def check_project(self, project_root: Path) -> List[Violation]:
        changed_paths = self._changed_paths(project_root)
        violations: List[Violation] = []
        for file_path in changed_paths:
            content = file_path.read_text(encoding="utf-8")
            violations.extend(self._check_python_file(file_path, content))
        return violations

    def _changed_paths(self, project_root: Path) -> List[Path]:
        if not (project_root / ".git").exists():
            return []

        git = shutil.which("git")
        if git is None:
            raise RuntimeError("Git is required to inspect changed Python files")
        diff_args = [git, "diff", "--name-only", "--diff-filter=ACMR"]
        if self.config.get("profile") == "fast":
            diff_args.append("--cached")
        else:
            diff_args.append("HEAD")
        diff_args.extend(["--", "*.py"])
        result = subprocess.run(  # noqa: S603
            diff_args,
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
        )  # noqa: S603
        if result.returncode != 0:
            detail = result.stderr.strip() or f"git exited with code {result.returncode}"
            raise RuntimeError(f"could not inspect changed Python files: {detail}")

        paths = {project_root / line for line in result.stdout.splitlines() if line}
        if self.config.get("profile") != "fast":
            untracked = subprocess.run(  # noqa: S603
                [git, "ls-files", "--others", "--exclude-standard", "--", "*.py"],
                cwd=project_root,
                check=False,
                capture_output=True,
                text=True,
            )  # noqa: S603
            if untracked.returncode != 0:
                detail = untracked.stderr.strip() or f"git exited with code {untracked.returncode}"
                raise RuntimeError(f"could not inspect untracked Python files: {detail}")
            paths.update(project_root / line for line in untracked.stdout.splitlines() if line)
        return sorted(path for path in paths if path.is_file())

    def _check_python_file(self, file_path: Path, content: str) -> List[Violation]:
        tree = ast.parse(content)
        is_test = self._is_test_file(file_path)
        limits = TEST_LIMITS if is_test else PRODUCTION_LIMITS
        lines = content.splitlines()
        violations = self._file_violations(file_path, lines, limits)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                violations.extend(self._function_violations(file_path, node, lines, limits))
        return violations

    def _file_violations(self, file_path: Path, lines: List[str], limits: dict) -> List[Violation]:
        """Check the source-line budget for one file."""
        file_lines = self._source_lines(lines)
        if file_lines <= limits["file_lines"]:
            return []
        return [
            self._violation(
                file_path,
                1,
                f"File has {file_lines} source lines; limit is {limits['file_lines']}.",
            )
        ]

    def _function_violations(
        self,
        file_path: Path,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        lines: List[str],
        limits: dict,
    ) -> List[Violation]:
        """Check size and control-flow budgets for one function."""
        start = min([node.lineno] + [decorator.lineno for decorator in node.decorator_list])
        end = node.end_lineno or node.lineno
        function_lines = self._source_lines(lines[start - 1 : end])
        complexity = self._complexity(node)
        nesting = self._nesting(node)
        checks = [
            (
                function_lines,
                limits["function_lines"],
                f"Function has {function_lines} source lines; limit is {limits['function_lines']}.",
            ),
            (
                complexity,
                limits["complexity"],
                f"Function complexity is {complexity}; limit is {limits['complexity']}.",
            ),
            (
                nesting,
                limits["nesting"],
                f"Function nesting depth is {nesting}; limit is {limits['nesting']}.",
            ),
        ]
        if "arguments" in limits:
            arguments = self._argument_count(node)
            checks.append(
                (
                    arguments,
                    limits["arguments"],
                    f"Function has {arguments} arguments; limit is {limits['arguments']}.",
                )
            )
        return [
            self._violation(file_path, node.lineno, message)
            for value, limit, message in checks
            if value > limit
        ]

    def _is_test_file(self, file_path: Path) -> bool:
        parts = {part.lower() for part in file_path.parts}
        name = file_path.name.lower()
        return "tests" in parts or name.startswith("test_") or name.endswith("_test.py")

    def _source_lines(self, lines: Iterable[str]) -> int:
        return sum(1 for line in lines if line.strip() and not line.lstrip().startswith("#"))

    def _argument_count(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        arguments = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
        return sum(1 for argument in arguments if argument.arg not in {"self", "cls"})

    def _complexity(self, node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp)):
                complexity += 1
            if isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            if isinstance(child, ast.ExceptHandler):
                complexity += 1
            if isinstance(child, ast.Match):
                complexity += len(child.cases)
        return complexity

    def _nesting(self, node: ast.AST) -> int:
        return max((self._node_depth(child, 0) for child in node.body), default=0)

    def _node_depth(self, node: ast.AST, current_depth: int) -> int:
        """Return the maximum control-flow depth below one AST node."""
        next_depth = current_depth + int(isinstance(node, CONTROL_NODES))
        return max(
            (self._node_depth(child, next_depth) for child in ast.iter_child_nodes(node)),
            default=next_depth,
        )

    def _violation(self, file_path: Path, line_number: int, message: str) -> Violation:
        return self._create_violation(file_path, line_number, 0, message)
