from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time

from teams_cli.auth import AuthUnavailable, TeamsAuth
from teams_cli.config import (
    DAEMON_START_APPROVAL_ENV,
    Settings,
    graphical_session,
    load_settings,
)


class DaemonUnavailable(AuthUnavailable):
    """Raised when the daemon socket cannot be reached."""


def request_daemon_auth(settings: Settings | None = None) -> TeamsAuth:
    """Request current Teams credentials from the local CDP daemon."""
    resolved_settings = settings or load_settings()
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(resolved_settings.cdp_command_timeout_seconds)
            connection.connect(str(resolved_settings.socket_path))
            connection.sendall(b'{"operation":"auth"}\n')
            response = b""
            while not response.endswith(b"\n"):
                chunk = connection.recv(4096)
                if not chunk:
                    break
                response += chunk
    except OSError as error:
        raise DaemonUnavailable(
            f"Teams authentication daemon is unavailable at {resolved_settings.socket_path}."
        ) from error
    try:
        payload = json.loads(response)
        if not payload.get("ok"):
            raise AuthUnavailable(payload.get("error", "Teams authentication is unavailable."))
        return TeamsAuth(**payload["auth"])
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise AuthUnavailable(
            "Teams authentication daemon returned an invalid response."
        ) from error


def start_daemon(settings: Settings | None = None) -> None:
    """Start the headless daemon after the caller has obtained user consent."""
    resolved_settings = settings or load_settings()
    if graphical_session():
        raise AuthUnavailable(
            "Starting the headless Teams daemon is disabled in graphical sessions; "
            "use profile authentication."
        )
    try:
        environment = os.environ.copy()
        environment[DAEMON_START_APPROVAL_ENV] = "1"
        subprocess.Popen(
            [sys.executable, "-m", "teams_cli.authd"],
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True,
        )
    except OSError as error:
        raise AuthUnavailable(
            f"Could not start the Teams authentication daemon: {error}"
        ) from error
    deadline = time.monotonic() + resolved_settings.cdp_start_timeout_seconds
    while time.monotonic() < deadline:
        try:
            request_daemon_status(resolved_settings)
            return
        except AuthUnavailable:
            pass
        time.sleep(0.25)
    raise AuthUnavailable(
        "Teams authentication daemon did not become available before the startup timeout."
    )


def request_daemon_status(settings: Settings | None = None) -> dict[str, bool]:
    """Return the daemon status without exposing authentication material."""
    resolved_settings = settings or load_settings()
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(resolved_settings.cdp_command_timeout_seconds)
            connection.connect(str(resolved_settings.socket_path))
            connection.sendall(b'{"operation":"status"}\n')
            response = b""
            while not response.endswith(b"\n"):
                chunk = connection.recv(4096)
                if not chunk:
                    break
                response += chunk
    except OSError as error:
        raise AuthUnavailable(
            f"Teams authentication daemon is unavailable at {resolved_settings.socket_path}."
        ) from error
    try:
        payload = json.loads(response)
    except json.JSONDecodeError as error:
        raise AuthUnavailable(
            "Teams authentication daemon returned an invalid response."
        ) from error
    if not payload.get("ok"):
        raise AuthUnavailable(payload.get("error", "Teams authentication is unavailable."))
    allowed_keys = {"ok", "running", "authenticated"}
    return {key: bool(value) for key, value in payload.items() if key in allowed_keys}
