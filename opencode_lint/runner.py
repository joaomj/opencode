"""LinterRunner - Main linter orchestration."""

from pathlib import Path
from typing import Iterator, List, Optional, Type

from opencode_lint.rule import Rule
from opencode_lint.rules.no_env_file_access import NoEnvFileAccess
from opencode_lint.rules.no_privileged_containers import NoPrivilegedContainers
from opencode_lint.rules.no_unsafe_downloads import NoUnsafeDownloads
from opencode_lint.rules.policy_checks import (
    AgentArtifactCommit,
    MechanicalWriting,
    SuppressionPolicy,
    TestSuppressionPolicy,
)
from opencode_lint.rules.python_budgets import PythonBudgets
from opencode_lint.rules.skill_descriptions import SkillDescriptions
from opencode_lint.violation import Violation

DEFAULT_EXCLUDED_DIRS = frozenset(
    {
        ".cache",
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
        "venv",
    }
)

DEFAULT_LINTABLE_EXTENSIONS = [
    ".md",
    ".py",
    ".rst",
    ".sh",
    ".txt",
    ".toml",
    ".yml",
    ".yaml",
]

RULE_REGISTRY: List[Type[Rule]] = [
    NoEnvFileAccess,
    NoPrivilegedContainers,
    NoUnsafeDownloads,
    SkillDescriptions,
    SuppressionPolicy,
    TestSuppressionPolicy,
    MechanicalWriting,
    AgentArtifactCommit,
    PythonBudgets,
]


def find_project_root(targets: List[Path]) -> Path | None:
    """Find the nearest repository or project root for the targets."""
    for target in targets:
        candidate = target.resolve()
        if candidate.is_file():
            candidate = candidate.parent

        for parent in (candidate, *candidate.parents):
            if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
                return parent

    if targets:
        fallback = targets[0].resolve()
        return fallback if fallback.is_dir() else fallback.parent
    return None


def load_config(project_root: Path | None) -> dict:
    """Load the optional project configuration and fail on invalid config."""
    if project_root is None:
        return {}

    config_path = next(
        (
            project_root / filename
            for filename in (".opencode-lint.yaml", ".opencode-lint.yml")
            if (project_root / filename).exists()
        ),
        None,
    )
    if config_path is None:
        return {}

    try:
        import yaml
    except ImportError as error:
        raise RuntimeError("PyYAML is required to read linter configuration") from error

    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        raise RuntimeError(
            f"linter configuration could not be parsed: {config_path.name}"
        ) from error

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise RuntimeError("linter configuration must contain a mapping")
    return data


class LinterRunner:
    """Main linter runner that orchestrates all rules."""

    def __init__(self, config: Optional[dict] = None, profile: str = "coding"):
        """Initialize linter with optional configuration."""
        self.config = config or {}
        self.profile = profile
        self.rules: List[Rule] = []
        self._initialize_rules()

    def _initialize_rules(self) -> None:
        """Initialize all enabled rules."""
        rule_configs = self.config.get("rules", {})

        for rule_class in RULE_REGISTRY:
            rule_id = rule_class.rule_id
            rule_config = dict(rule_configs.get(rule_id, {}))
            rule_config.setdefault("profile", self.profile)

            if rule_config.get("enabled", True):
                self.rules.append(rule_class(config=rule_config))

    def _failure(self, file_path: Path, check: str, error: Exception) -> Violation:
        """Return an error when a required check cannot complete."""
        return Violation(
            rule_id="LNT022",
            file_path=file_path,
            line_number=0,
            column=0,
            message=(
                f"{check} could not complete ({type(error).__name__}); "
                "policy evaluation failed closed."
            ),
            severity="error",
        )

    def check_file(self, file_path: Path) -> List[Violation]:
        """Check a single file for violations."""
        violations = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except (IOError, UnicodeDecodeError) as error:
            return [self._failure(file_path, "file read", error)]

        for rule in self.rules:
            try:
                if rule.should_check_file(file_path):
                    rule_violations = rule.check_file(file_path, content)
                    violations.extend(rule_violations)
            except Exception as error:
                violations.append(self._failure(file_path, rule.rule_id, error))

        violations.sort(key=lambda v: (v.file_path, v.line_number))

        return violations

    def check_files(self, file_paths: List[Path]) -> List[Violation]:
        """Check multiple files for violations."""
        all_violations = []

        for file_path in file_paths:
            all_violations.extend(self.check_file(file_path))

        return all_violations

    def check_directory(
        self,
        directory: Path,
        extensions: Optional[List[str]] = None,
    ) -> List[Violation]:
        """Check all files in a directory recursively."""
        if extensions is None:
            extensions = DEFAULT_LINTABLE_EXTENSIONS

        all_violations = []

        try:
            for file_path in self._iter_lintable_files(directory, extensions):
                all_violations.extend(self.check_file(file_path))
        except OSError as error:
            all_violations.append(self._failure(directory, "directory scan", error))

        return all_violations

    def _iter_lintable_files(self, directory: Path, extensions: List[str]) -> Iterator[Path]:
        """Yield lintable files while pruning dependency/cache directories."""
        stack = [directory]

        while stack:
            current = stack.pop()
            entries = list(current.iterdir())

            for entry in entries:
                if entry.is_dir():
                    if entry.name in DEFAULT_EXCLUDED_DIRS:
                        continue
                    stack.append(entry)
                    continue
                if entry.is_file() and (
                    entry.suffix in extensions or entry.name.lower() in {"dockerfile", "makefile"}
                ):
                    yield entry

    def run(
        self,
        targets: List[Path],
    ) -> tuple[List[Violation], int]:
        """Run linter on targets.

        Args:
            targets: Files or directories to check

        Returns:
            Tuple of (violations, exit_code)
        """
        all_violations: List[Violation] = []

        for target in targets:
            if target.is_file():
                all_violations.extend(self.check_file(target))
            elif target.is_dir():
                all_violations.extend(self.check_directory(target))

        project_root = find_project_root(targets)
        if project_root:
            for rule in self.rules:
                try:
                    all_violations.extend(rule.check_project(project_root))
                except Exception as error:
                    all_violations.append(self._failure(project_root, rule.rule_id, error))

        error_count = sum(1 for v in all_violations if v.severity == "error")
        exit_code = 1 if error_count > 0 else 0

        return all_violations, exit_code

    def _find_project_root(self, targets: List[Path]) -> Path | None:
        """Find the project root directory from targets."""
        return find_project_root(targets)
