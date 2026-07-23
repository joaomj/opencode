from __future__ import annotations

import json

from teams_cli.auth import AuthUnavailable
from teams_cli.daemon_client import request_daemon_status


def main() -> None:
    try:
        print(json.dumps(request_daemon_status(), indent=2))
    except AuthUnavailable as error:
        print(f"Teams authentication daemon unavailable: {error}")
        raise SystemExit(1) from error
