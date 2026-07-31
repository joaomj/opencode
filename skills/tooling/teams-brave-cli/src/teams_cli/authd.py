from __future__ import annotations

import json
import os
import signal
import socketserver
from dataclasses import asdict
from fcntl import LOCK_EX, LOCK_NB, LOCK_UN, flock
from pathlib import Path
from threading import RLock, Thread
from typing import Any, TextIO

from teams_cli.auth import AuthUnavailable, TeamsAuth, auth_from_cookies
from teams_cli.cdp import CdpError, ChromiumBrowser
from teams_cli.config import (
    DAEMON_START_APPROVAL_ENV,
    MAX_REQUEST_BYTES,
    Settings,
    graphical_session,
    load_settings,
)
from teams_cli.logging_utils import configure_logging, get_logger

logger = get_logger(__name__)


class AuthRequestHandler(socketserver.StreamRequestHandler):
    server: AuthServer

    def handle(self) -> None:
        self.connection.settimeout(self.server.daemon.settings.cdp_command_timeout_seconds)
        try:
            request_line = self.rfile.readline(MAX_REQUEST_BYTES + 1)
        except OSError:
            return
        if len(request_line) > MAX_REQUEST_BYTES:
            self._write({"ok": False, "error": "request is too large"})
            return
        try:
            operation = json.loads(request_line).get("operation")
        except (json.JSONDecodeError, AttributeError):
            self._write({"ok": False, "error": "invalid request"})
            return
        if operation == "status":
            self._write(self.server.daemon.status())
            return
        if operation == "auth":
            try:
                self._write({"ok": True, "auth": asdict(self.server.daemon.auth())})
            except (AuthUnavailable, CdpError) as error:
                self._write({"ok": False, "error": str(error)})
            return
        self._write({"ok": False, "error": "unsupported operation"})

    def _write(self, payload: dict[str, Any]) -> None:
        self.wfile.write((json.dumps(payload) + "\n").encode())
        self.wfile.flush()


class AuthServer(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True

    def __init__(self, socket_path: Path, daemon: AuthDaemon) -> None:
        self.daemon = daemon
        super().__init__(str(socket_path), AuthRequestHandler)


class AuthDaemon:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.browser = ChromiumBrowser(settings)
        self._auth_lock = RLock()
        self.server: AuthServer | None = None
        self._lock_file: TextIO | None = None

    def run(self) -> None:
        if graphical_session():
            raise RuntimeError(
                "Teams authentication daemon is disabled in graphical sessions; "
                "use profile authentication."
            )
        if os.getenv(DAEMON_START_APPROVAL_ENV) != "1":
            raise RuntimeError(
                "Teams authentication daemon requires confirmation from the Teams CLI."
            )
        self.settings.socket_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.settings.socket_path.parent.chmod(0o700)
        self._acquire_instance_lock()
        try:
            self._remove_stale_socket()
            self.browser.start()
            self.server = AuthServer(self.settings.socket_path, self)
            self.settings.socket_path.chmod(0o600)
            logger.info("Teams authentication daemon listening on %s", self.settings.socket_path)
            self.server.serve_forever()
        finally:
            if self.server is not None:
                self.server.server_close()
            self.browser.stop()
            self._remove_stale_socket()
            self._release_instance_lock()

    def stop(self) -> None:
        if self.server is not None:
            self.server.shutdown()

    def status(self) -> dict[str, bool]:
        with self._auth_lock:
            try:
                auth_from_cookies(self.browser.get_cookies())
            except (AuthUnavailable, CdpError):
                authenticated = False
            else:
                authenticated = True
        return {"ok": True, "running": True, "authenticated": authenticated}

    def auth(self) -> TeamsAuth:
        with self._auth_lock:
            auth = auth_from_cookies(self.browser.get_cookies())
        logger.info("Retrieved Teams authentication from the dedicated browser profile")
        return auth

    def _remove_stale_socket(self) -> None:
        if not self.settings.socket_path.exists():
            return
        if not self.settings.socket_path.is_socket():
            raise RuntimeError(
                f"Authentication socket path is not a socket: {self.settings.socket_path}"
            )
        self.settings.socket_path.unlink()

    def _acquire_instance_lock(self) -> None:
        lock_path = self.settings.socket_path.with_suffix(".lock")
        lock_file = lock_path.open("a", encoding="utf-8")
        lock_path.chmod(0o600)
        try:
            flock(lock_file.fileno(), LOCK_EX | LOCK_NB)
        except BlockingIOError as error:
            lock_file.close()
            raise RuntimeError("Teams authentication daemon is already running.") from error
        self._lock_file = lock_file

    def _release_instance_lock(self) -> None:
        if self._lock_file is not None:
            flock(self._lock_file.fileno(), LOCK_UN)
            self._lock_file.close()
            self._lock_file = None


def main() -> None:
    configure_logging()
    daemon = AuthDaemon(load_settings())

    def shutdown(_signum: int, _frame: Any) -> None:
        Thread(target=daemon.stop, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    try:
        daemon.run()
    except (CdpError, OSError, RuntimeError) as error:
        logger.exception("Teams authentication daemon failed: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
