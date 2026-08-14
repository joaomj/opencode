"""OC003: No privileged containers in docker-compose.

Security rule to prevent privileged mode in Docker containers.
Enforces: Containers must not run with privileged: true or cap_add: [ALL].
"""

from pathlib import Path
from typing import List

try:
    import importlib.util  # noqa: F401
    HAS_YAML = importlib.util.find_spec('yaml') is not None
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
        'privileged': True,
        'security_opt': lambda x: isinstance(x, list) and any(
            'unconfined' in str(item).lower() for item in x
        ),
    }

    def should_check_file(self, file_path: Path) -> bool:
        """Only check docker-compose files."""
        if not super().should_check_file(file_path):
            return False

        name = file_path.name.lower()
        # Check if file is a yaml file AND contains docker-compose pattern
        if not name.endswith(('.yml', '.yaml')):
            return False

        # Match docker-compose, compose, or files with "compose" in the name
        return any(
            pattern in name
            for pattern in ['docker-compose', 'compose', 'docker_compose']
        )

    def check_file(self, file_path: Path, content: str) -> List[Violation]:
        """Check docker-compose file for privileged containers."""
        violations: List[Violation] = []

        # Import yaml here to avoid issues if not available
        try:
            import yaml
        except ImportError:
            # Can't parse without PyYAML
            return violations

        try:
            data = yaml.safe_load(content)
        except Exception:
            return violations

        if not isinstance(data, dict):
            return violations

        services = data.get('services', {})
        if not isinstance(services, dict):
            return violations

        for service_name, service_config in services.items():
            if not isinstance(service_config, dict):
                continue

            # Check privileged: true
            if service_config.get('privileged') is True:
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=self._find_line_number(content, 'privileged'),
                        column=0,
                        message=(
                            f"Service '{service_name}' has privileged: true. "
                            f"This grants full host access and is a security risk. "
                            f"Use specific capabilities instead. "
                            "Project policy: do not use privileged containers."
                        ),
                        fix="Remove privileged: true and add only required capabilities",
                    )
                )

            # Check cap_add: [ALL]
            cap_add = service_config.get('cap_add', [])
            if isinstance(cap_add, list) and any(
                str(cap).upper() == 'ALL' for cap in cap_add
            ):
                violations.append(
                    self._create_violation(
                        file_path=file_path,
                        line_number=self._find_line_number(content, 'cap_add'),
                        column=0,
                        message=(
                            f"Service '{service_name}' has cap_add: ALL. "
                            f"This grants all Linux capabilities. "
                            f"Add only required capabilities. "
                            "Project policy: do not use privileged containers."
                        ),
                        fix="Replace 'ALL' with specific required capabilities",
                    )
                )

            # Check security_opt for unconfined
            security_opt = service_config.get('security_opt', [])
            if isinstance(security_opt, list):
                for opt in security_opt:
                    if isinstance(opt, str) and 'unconfined' in opt.lower():
                        violations.append(
                            self._create_violation(
                                file_path=file_path,
                                line_number=self._find_line_number(content, 'security_opt'),
                                column=0,
                                message=(
                                    f"Service '{service_name}' has unconfined security option. "
                                    f"This disables seccomp profiles. "
                                    "Project policy: do not use privileged containers."
                                ),
                                fix="Remove security_opt or use confined profile",
                            )
                        )
                        break

        return violations

    def _find_line_number(self, content: str, key: str) -> int:
        """Find the line number of a key in the content."""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if key in line:
                return i
        return 1
