"""OC003: No privileged containers in docker-compose.

Security rule to prevent privileged mode in Docker containers.
Enforces: Containers must not run with privileged: true or cap_add: [ALL].
"""

from pathlib import Path
from typing import List

try:
    import importlib.util

    HAS_YAML = importlib.util.find_spec("yaml") is not None
except ImportError:
    HAS_YAML = False

from opencode_lint.rule import Rule
from opencode_lint.violation import Violation


class NoPrivilegedContainers(Rule):
    """Rule OC003: No privileged containers in docker-compose.

    Prevents:
    - privileged: true
    - cap_add: [ALL]
    - security_opt: ["seccomp:unconfined"]

    Why: Privileged containers have full access to host resources,
    bypassing security boundaries. Agents often add this to "fix"
    permission issues.
    """

    rule_id = "OC003"
    description = "No privileged containers in docker-compose"
    severity = "error"
    categories = ["security", "docker"]

    VIOLATION_KEYS = {
        "privileged": True,
        "security_opt": lambda x: (
            isinstance(x, list) and any("unconfined" in str(item).lower() for item in x)
        ),
    }

    def should_check_file(self, file_path: Path) -> bool:
        """Only check docker-compose files."""
        if not super().should_check_file(file_path):
            return False

        name = file_path.name.lower()
        # Check if file is a yaml file AND contains docker-compose pattern
        if not name.endswith((".yml", ".yaml")):
            return False

        # Match docker-compose, compose, or files with "compose" in the name
        return any(pattern in name for pattern in ["docker-compose", "compose", "docker_compose"])

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        """Check docker-compose file for privileged containers."""
        if not HAS_YAML:
            raise RuntimeError("PyYAML is required to parse compose files")
        import yaml

        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            return []

        services = data.get("services", {})
        if not isinstance(services, dict):
            return []
        return [
            violation
            for service_name, service_config in services.items()
            if isinstance(service_config, dict)
            for violation in self._service_violations(
                file_path, content, service_name, service_config
            )
        ]

    def _service_violations(
        self, file_path: Path, content: str, service_name: str, service_config: dict
    ) -> List[Violation]:
        """Check each protected compose setting for one service."""
        return (
            self._privileged_violation(file_path, content, service_name, service_config)
            + self._capability_violation(file_path, content, service_name, service_config)
            + self._security_violation(file_path, content, service_name, service_config)
        )

    def _privileged_violation(
        self, file_path: Path, content: str, service_name: str, service_config: dict
    ) -> List[Violation]:
        if service_config.get("privileged") is not True:
            return []
        return [
            self._create_violation(
                file_path=file_path,
                line_number=self._find_line_number(content, "privileged"),
                column=0,
                message=(
                    f"Service '{service_name}' has privileged: true. "
                    "This grants full host access and is a security risk. "
                    "Use specific capabilities instead. "
                    "Project policy: do not use privileged containers."
                ),
                fix="Remove privileged: true and add only required capabilities",
            )
        ]

    def _capability_violation(
        self, file_path: Path, content: str, service_name: str, service_config: dict
    ) -> List[Violation]:
        cap_add = service_config.get("cap_add", [])
        has_all = isinstance(cap_add, list) and any(
            str(capability).upper() == "ALL" for capability in cap_add
        )
        if not has_all:
            return []
        return [
            self._create_violation(
                file_path=file_path,
                line_number=self._find_line_number(content, "cap_add"),
                column=0,
                message=(
                    f"Service '{service_name}' has cap_add: ALL. "
                    "This grants all Linux capabilities. "
                    "Add only required capabilities. "
                    "Project policy: do not use privileged containers."
                ),
                fix="Replace 'ALL' with specific required capabilities",
            )
        ]

    def _security_violation(
        self, file_path: Path, content: str, service_name: str, service_config: dict
    ) -> List[Violation]:
        security_opt = service_config.get("security_opt", [])
        if not isinstance(security_opt, list):
            return []
        unconfined = next(
            (
                option
                for option in security_opt
                if isinstance(option, str) and "unconfined" in option.lower()
            ),
            None,
        )
        if unconfined is None:
            return []
        return [
            self._create_violation(
                file_path=file_path,
                line_number=self._find_line_number(content, "security_opt"),
                column=0,
                message=(
                    f"Service '{service_name}' has unconfined security option. "
                    "This disables seccomp profiles. "
                    "Project policy: do not use privileged containers."
                ),
                fix="Remove security_opt or use confined profile",
            )
        ]

    def _find_line_number(self, content: str, key: str) -> int:
        """Find the line number of a key in the content."""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if key in line:
                return i
        return 1
