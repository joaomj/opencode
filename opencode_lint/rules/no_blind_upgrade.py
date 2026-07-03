"""OC011: No blind dependency upgrades.

Prevents blind --upgrade commands that pull latest versions
without specifying which package to upgrade.
Enforces targeted upgrades only.
"""

import re
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class NoBlindUpgrade(Rule):
    """Rule OC011: No blind dependency upgrades.

    Blocks patterns like 'uv lock --upgrade' without '--upgrade-package'.
    Allows 'uv lock --upgrade-package <name>'.
    """

    rule_id = "OC011"
    description = "No blind dependency upgrades — use --upgrade-package <name>"
    severity = "error"
    categories = ["supply-chain"]

    BLIND_UPGRADE_RE = re.compile(
        r"uv\s+lock\s+--upgrade(?!\s+--upgrade-package)"
    )

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        violations = []

        # Only check scripts, CI configs, makefiles, and markdown docs
        if not self._is_checkable_file(file_path):
            return violations

        for i, line in enumerate(content.splitlines(), 1):
            if self.BLIND_UPGRADE_RE.search(line):
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=i,
                        column=0,
                        message=(
                            "Blind 'uv lock --upgrade' detected. "
                            "Use 'uv lock --upgrade-package <name>' for targeted upgrades."
                        ),
                        fix="Replace with: uv lock --upgrade-package <package-name>",
                    )
                )

        return violations

    def _is_checkable_file(self, file_path: Path) -> bool:
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()
        if "opencode_lint/rules" in file_path.as_posix():
            return False
        if suffix in (".sh", ".yml", ".yaml", ".md", ".rst", ".txt", ".py"):
            return True
        if name in ("makefile", "dockerfile"):
            return True
        return False

    def should_check_file(self, file_path: Path) -> bool:
        if not super().should_check_file(file_path):
            return False
        return self._is_checkable_file(file_path)
