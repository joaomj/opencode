"""OC009: Lockfile must exist and be committed.

Prevents projects from running without a lockfile, which enables
dependency drift and supply chain attacks.
"""

from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class LockfileRequired(Rule):
    """Rule OC009: Lockfile must exist and be committed.

    Checks for presence of uv.lock, pdm.lock, or poetry.lock
    in the project root. Also verifies the lockfile is not
    ignored by .gitignore.
    """

    rule_id = "OC009"
    description = "Lockfile must exist and be committed"
    severity = "error"
    categories = ["supply-chain"]

    LOCKFILE_NAMES = ("uv.lock", "pdm.lock", "poetry.lock")
    GITIGNORE_PATTERNS = (".gitignore", ".git/info/exclude")

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        violations = []

        if file_path.suffix not in (".toml", ".yaml", ".yml", ".txt", ".lock"):
            return violations

        if file_path.name in self.LOCKFILE_NAMES:
            violations.append(
                self._create_violation(
                    file_path=file_path,
                    line_number=1,
                    column=0,
                    message=(
                        f"Lockfile '{file_path.name}' found. "
                        "Verify it is committed to git and not in .gitignore."
                    ),
                )
            )

        return violations

    def should_check_file(self, file_path: Path) -> bool:
        path_str = str(file_path)
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return False
        return True


def check_root_for_lockfile(root: Path) -> List[Violation]:
    """Check project root for lockfile presence."""
    violations = []
    lockfile_found = False

    for name in LockfileRequired.LOCKFILE_NAMES:
        lockfile_path = root / name
        if lockfile_path.exists():
            lockfile_found = True
            break

    if not lockfile_found:
        violation = Violation(
            rule_id="OC009",
            file_path=root / "pyproject.toml",
            line_number=1,
            column=0,
            message=(
                "No lockfile found in project root. "
                "Expected one of: uv.lock, pdm.lock, poetry.lock. "
                "The repository policy requires a committed lockfile."
            ),
            severity="error",
        )
        violations.append(violation)
        return violations

    gitignore_path = root / ".gitignore"
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        for name in LockfileRequired.LOCKFILE_NAMES:
            if name in gitignore_content:
                violation = Violation(
                    rule_id="OC009",
                    file_path=gitignore_path,
                    line_number=1,
                    column=0,
                    message=(
                        f"Lockfile '{name}' appears in .gitignore. "
                        "The repository policy requires the lockfile to be committed."
                    ),
                    severity="error",
                )
                violations.append(violation)

    return violations
