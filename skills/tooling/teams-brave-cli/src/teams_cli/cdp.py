from __future__ import annotations

import json
import subprocess
import time
from threading import RLock
from typing import Any

import httpx
from websockets.sync.client import ClientConnection, connect

from teams_cli.config import (
    CDP_ENDPOINT_POLL_INTERVAL_SECONDS,
    CDP_VERSION_PATH,
    TEAMS_BROWSER_URL,
    Settings,
)


class CdpError(RuntimeError):
    """Raised when Chromium's CDP endpoint is unavailable."""


class ChromiumBrowser:
    """Own a dedicated headless browser profile and retrieve its cookies via CDP."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._process: subprocess.Popen[bytes] | None = None
        self._lock = RLock()
        self._command_id = 0

    def start(self) -> None:
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                return
            self.settings.profile_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.settings.profile_dir.chmod(0o700)
            (self.settings.profile_dir / "DevToolsActivePort").unlink(missing_ok=True)
            command = [
                self.settings.browser,
                "--headless=new",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-gpu",
                "--password-store=basic",
                f"--user-data-dir={self.settings.profile_dir}",
                f"--remote-debugging-address={self.settings.cdp_host}",
                "--remote-debugging-port=0",
                TEAMS_BROWSER_URL,
            ]
            try:
                self._process = subprocess.Popen(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except OSError as error:
                raise CdpError(f"Could not start the configured browser: {error}") from error
            try:
                self._wait_for_endpoint()
            except CdpError:
                self.stop()
                raise

    def stop(self) -> None:
        process = self._process
        self._process = None
        if process is None or process.poll() is not None:
            return
        process.terminate()
        try:
            process.wait(timeout=self.settings.cdp_command_timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    def get_cookies(self) -> list[dict[str, Any]]:
        with self._lock:
            self.start()
            with connect(
                self._browser_websocket_url(),
                open_timeout=self.settings.cdp_command_timeout_seconds,
                close_timeout=self.settings.cdp_command_timeout_seconds,
                max_size=None,
            ) as websocket:
                target = self._command(websocket, "Target.createTarget", {"url": "about:blank"})
                target_id = target["targetId"]
                try:
                    attached = self._command(
                        websocket,
                        "Target.attachToTarget",
                        {"targetId": target_id, "flatten": True},
                    )
                    cookies = self._command(
                        websocket,
                        "Network.getAllCookies",
                        session_id=attached["sessionId"],
                    )
                    return cookies.get("cookies", [])
                finally:
                    self._command(websocket, "Target.closeTarget", {"targetId": target_id})

    def _wait_for_endpoint(self) -> None:
        deadline = time.monotonic() + self.settings.cdp_start_timeout_seconds
        while time.monotonic() < deadline:
            if self._process is not None and self._process.poll() is not None:
                raise CdpError("Browser exited before its CDP endpoint became ready.")
            try:
                self._browser_websocket_url()
                return
            except CdpError:
                time.sleep(CDP_ENDPOINT_POLL_INTERVAL_SECONDS)
        raise CdpError("Browser CDP endpoint did not start before the timeout.")

    def _browser_websocket_url(self) -> str:
        endpoint_file = self.settings.profile_dir / "DevToolsActivePort"
        try:
            port, _websocket_path = endpoint_file.read_text(encoding="utf-8").splitlines()
        except (OSError, ValueError) as error:
            raise CdpError("Browser CDP endpoint is not ready.") from error
        url = f"http://{self.settings.cdp_host}:{port}{CDP_VERSION_PATH}"
        try:
            response = httpx.get(url, timeout=self.settings.cdp_command_timeout_seconds)
            response.raise_for_status()
            value = response.json().get("webSocketDebuggerUrl")
        except (httpx.HTTPError, ValueError, TypeError) as error:
            raise CdpError("Could not query the local browser CDP endpoint.") from error
        expected_prefix = f"ws://{self.settings.cdp_host}:"
        if not isinstance(value, str) or not value.startswith(expected_prefix):
            raise CdpError("Browser returned an invalid local CDP endpoint.")
        return value

    def _command(
        self,
        websocket: ClientConnection,
        method: str,
        params: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        self._command_id += 1
        command: dict[str, Any] = {"id": self._command_id, "method": method, "params": params or {}}
        if session_id is not None:
            command["sessionId"] = session_id
        websocket.send(json.dumps(command))
        while True:
            try:
                message = json.loads(
                    websocket.recv(timeout=self.settings.cdp_command_timeout_seconds)
                )
            except TimeoutError as error:
                raise CdpError(f"CDP command timed out: {method}") from error
            if message.get("id") != command["id"]:
                continue
            if message.get("error"):
                raise CdpError(f"CDP command failed: {method}")
            result = message.get("result", {})
            if not isinstance(result, dict):
                raise CdpError(f"CDP returned an invalid result for {method}")
            return result
