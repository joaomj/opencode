from __future__ import annotations

import json
import socket

from teams_cli.auth import AuthUnavailable, TeamsAuth
from teams_cli.config import Settings, load_settings


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
        raise AuthUnavailable(
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
