"""OC012: No unsafe downloads (curl | bash).

Prevents supply chain attacks via script injection in
curl-to-shell patterns.
"""

import re
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class NoUnsafeDownloads(Rule):
    """Rule OC012: No unsafe downloads.

    Blocks 'curl ... | bash' and similar pipe-to-shell patterns.
    """

    rule_id = "OC012"
    description = "No unsafe curl | bash downloads — use explicit install steps"
    severity = "error"
    categories = ["supply-chain", "security"]

    UNSAFE_DOWNLOAD_RE = re.compile(
        r"(?:curl|wget)\s+[^|\n]*\|\s*(?:bash|sh|zsh|python[23]?|perl|ruby)"
    )

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        violations = []

        # Check scripts, CI configs, markdown docs
        if not self._is_checkable_file(file_path):
            return violations

        for i, line in enumerate(content.splitlines(), 1):
            if self.UNSAFE_DOWNLOAD_RE.search(line):
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=i,
                        column=0,
                        message=(
                            "Unsafe 'curl | bash' detected. "
                            "Download scripts can be manipulated. "
                            "Use explicit install steps or verify checksums."
                        ),
                        fix="Use explicit package manager install (apt, uv, pip, etc.)",
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
