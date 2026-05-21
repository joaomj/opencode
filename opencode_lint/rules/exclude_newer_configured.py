"""OC010: exclude-newer must be configured with 7-day buffer.

Prevents dependency resolution from using packages uploaded after
a 7-day cutoff, protecting against fresh malicious releases.
"""

import os
from pathlib import Path
from typing import List

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class ExcludeNewerConfigured(Rule):
    """Rule OC010: exclude-newer must be configured with 7-day buffer.

    Checks pyproject.toml for [tool.uv] exclude-newer = "1 week"
    Also checks ~/.config/uv/uv.toml for global exclude-newer.
    Falls back to checking UV_EXCLUDE_NEWER environment variable.
    """

    rule_id = "OC010"
    description = "exclude-newer with 7-day buffer required in pyproject.toml"
    severity = "error"
    categories = ["supply-chain"]

    VALID_DURATIONS = ("1 week", "7 days", "P7D")

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        violations = []

        if file_path.suffix not in (".toml",):
            return violations

        exclude_newer_found = False
        exclude_newer_value = None

        for line in content.splitlines():
            if line.strip().startswith("exclude-newer"):
                exclude_newer_found = True
                exclude_newer_value = line.split("=", 1)[1].strip()
                break

        if not exclude_newer_found:
            violations.append(
                self._create_violation(
                    file_path=file_path,
                    line_number=1,
                    column=0,
                    message=(
                        "exclude-newer not found in pyproject.toml. "
                        "Add [tool.uv] exclude-newer = \"1 week\" to protect "
                        "against fresh malicious releases. Per AGENTS.md OC010."
                    ),
                    fix='Add: exclude-newer = "1 week" under [tool.uv]',
                )
            )
            return violations

        normalized_value = exclude_newer_value.strip().strip('"').strip("'")
        if normalized_value not in self.VALID_DURATIONS:
            violations.append(
                self._create_violation(
                    file_path=file_path,
                    line_number=1,
                    column=0,
                    message=(
                        f"exclude-newer value '{exclude_newer_value}' is not a 7-day buffer. "
                        f"Use one of: {', '.join(self.VALID_DURATIONS)}. Per AGENTS.md OC010."
                    ),
                    fix='Set: exclude-newer = "1 week"',
                )
            )

        return violations

    def should_check_file(self, file_path: Path) -> bool:
        if not super().should_check_file(file_path):
            return False
        return file_path.name == "pyproject.toml"


def check_global_uv_config() -> List[Violation]:
    """Check global uv config for exclude-newer."""
    violations = []
    home_config = Path.home() / ".config" / "uv" / "uv.toml"

    if home_config.exists():
        content = home_config.read_text()
        if "exclude-newer" in content:
            return violations

    env_value = os.environ.get("UV_EXCLUDE_NEWER", "")
    if env_value:
        return violations

    violation = Violation(
        rule_id="OC010",
        file_path=Path.cwd() / "pyproject.toml",
        line_number=1,
        column=0,
        message=(
            "exclude-newer not configured: not in pyproject.toml, "
            "~/.config/uv/uv.toml, or UV_EXCLUDE_NEWER env var. "
            "Must be set with 7-day buffer per AGENTS.md OC010."
        ),
        severity="error",
    )
    violations.append(violation)
    return violations
