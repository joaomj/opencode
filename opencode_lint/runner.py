"""LinterRunner - Main linter orchestration."""

from pathlib import Path
from typing import Iterator, List, Optional, Type

from opencode_lint.rule import Rule
from opencode_lint.rules.absolute_imports import AbsoluteImportsPreferred
from opencode_lint.rules.exclude_newer_configured import (
    ExcludeNewerConfigured,
    check_global_uv_config,
)
from opencode_lint.rules.lockfile_required import LockfileRequired, check_root_for_lockfile
from opencode_lint.rules.no_blind_upgrade import NoBlindUpgrade
from opencode_lint.rules.no_env_file_access import NoEnvFileAccess
from opencode_lint.rules.no_hardcoded_config import NoHardcodedConfig
from opencode_lint.rules.no_privileged_containers import NoPrivilegedContainers
from opencode_lint.rules.no_raw_dict_api import NoRawDictAPISchema
from opencode_lint.rules.no_test_mock_abuse import NoTestMockAbuse
from opencode_lint.rules.no_unsafe_downloads import NoUnsafeDownloads
from opencode_lint.rules.registry_sync import RegistrySync
from opencode_lint.rules.routing_consistency import RoutingConsistency
from opencode_lint.rules.skill_descriptions import SkillDescriptions
from opencode_lint.rules.strict_type_hints import StrictTypeHints
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

RULE_REGISTRY: List[Type[Rule]] = [
    NoRawDictAPISchema,
    NoEnvFileAccess,
    NoPrivilegedContainers,
    AbsoluteImportsPreferred,
    StrictTypeHints,
    LockfileRequired,
    ExcludeNewerConfigured,
    NoBlindUpgrade,
    NoUnsafeDownloads,
    NoTestMockAbuse,
    NoHardcodedConfig,
    RoutingConsistency,
    RegistrySync,
    SkillDescriptions,
]


class LinterRunner:
    """Main linter runner that orchestrates all rules."""

    def __init__(self, config: Optional[dict] = None):
        """Initialize linter with optional configuration."""
        self.config = config or {}
        self.rules: List[Rule] = []
        self._initialize_rules()

    def _initialize_rules(self) -> None:
        """Initialize all enabled rules."""
        rule_configs = self.config.get("rules", {})

        for rule_class in RULE_REGISTRY:
            rule_id = rule_class.rule_id
            rule_config = rule_configs.get(rule_id, {})

            if rule_config.get("enabled", True):
                self.rules.append(rule_class(config=rule_config))

    def check_file(self, file_path: Path) -> List[Violation]:
        """Check a single file for violations."""
        violations = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except (IOError, UnicodeDecodeError):
            return violations

        for rule in self.rules:
            if rule.should_check_file(file_path):
                rule_violations = rule.check_file(file_path, content)
                violations.extend(rule_violations)

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
            extensions = [".py", ".yml", ".yaml"]

        all_violations = []

        for file_path in self._iter_lintable_files(directory, extensions):
            all_violations.extend(self.check_file(file_path))

        return all_violations

    def _iter_lintable_files(self, directory: Path, extensions: List[str]) -> Iterator[Path]:
        """Yield lintable files while pruning dependency/cache directories."""
        stack = [directory]

        while stack:
            current = stack.pop()
            try:
                entries = list(current.iterdir())
            except OSError:
                continue

            for entry in entries:
                if entry.is_dir():
                    if entry.name in DEFAULT_EXCLUDED_DIRS:
                        continue
                    stack.append(entry)
                    continue
                if entry.is_file() and entry.suffix in extensions:
                    yield entry

    def run(
        self,
        targets: List[Path],
        fix: bool = False,
    ) -> tuple[List[Violation], int]:
        """Run linter on targets.

        Args:
            targets: Files or directories to check
            fix: Whether to attempt auto-fixes

        Returns:
            Tuple of (violations, exit_code)
        """
        all_violations: List[Violation] = []

        for target in targets:
            if target.is_file():
                all_violations.extend(self.check_file(target))
            elif target.is_dir():
                all_violations.extend(self.check_directory(target))

        project_root = self._find_project_root(targets)
        if project_root:
            if (project_root / "pyproject.toml").exists():
                all_violations.extend(check_root_for_lockfile(project_root))
                all_violations.extend(check_global_uv_config())
            for rule in self.rules:
                all_violations.extend(rule.check_project(project_root))

        error_count = sum(1 for v in all_violations if v.severity == "error")
        exit_code = 1 if error_count > 0 else 0

        return all_violations, exit_code

    def _find_project_root(self, targets: List[Path]) -> Path | None:
        """Find the project root directory from targets."""
        for target in targets:
            if target.is_dir():
                pyproject = target / "pyproject.toml"
                if pyproject.exists():
                    return target
            else:
                parent = target.parent
                pyproject = parent / "pyproject.toml"
                if pyproject.exists():
                    return parent
        if targets:
            return targets[0].parent if targets[0].is_file() else targets[0]
        return None
