#!/usr/bin/env python3
"""
browser_cdp.py — Read-only browser operations via Chrome DevTools Protocol (CDP).

Cross-platform (macOS + Linux). Uses the local Brave Browser (or Chromium fallback)
via CDP over WebSocket. No Puppeteer, no Playwright, no Selenium.

Setup (one-time):
    python3 -m venv .venv
    source .venv/bin/activate
    pip install websockets

Usage:
    python browser_cdp.py navigate <url>
    python browser_cdp.py screenshot [--output path.png] [--full-page]
    python browser_cdp.py eval <js_expression>
    python browser_cdp.py console [--url <url>]
    python browser_cdp.py network [--url <url>]
    python browser_cdp.py dom [--selector <css_selector>]
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import pathlib
import platform
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from typing import Any

import websockets


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEBUG_PORT = 9222
BROWSER_TIMEOUT = 30.0

MACOS_BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

LINUX_BINARIES = [
    "brave-browser",
    "brave",
    "chromium",
    "chromium-browser",
    "google-chrome-stable",
]

HEADLESS_ARGS = [
    "--headless=new",
    "--remote-debugging-port=9222",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-setuid-sandbox",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-breakpad",
    "--disable-client-side-phishing-detection",
    "--disable-component-extensions-with-background-pages",
    "--disable-default-apps",
    "--disable-extensions",
    "--disable-hang-monitor",
    "--disable-infobars",
    "--disable-ipc-flooding-protection",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-renderer-backgrounding",
    "--force-color-profile=srgb",
    "--metrics-recording-only",
    "--safebrowsing-disable-auto-update",
    "--enable-automation",
    "--password-store=basic",
    "--use-mock-keychain",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_browser() -> str | None:
    """Return path to Brave/Chromium binary, or None."""
    system = platform.system()
    if system == "Darwin":
        if os.path.isfile(MACOS_BRAVE):
            return MACOS_BRAVE
    # Linux or fallback
    for name in LINUX_BINARIES:
        path = shutil.which(name)
        if path:
            return path
    return None


def _is_browser_running() -> bool:
    """Check whether something is listening on DEBUG_PORT."""
    try:
        with socket.create_connection(("localhost", DEBUG_PORT), timeout=1):
            return True
    except OSError:
        return False


def _ensure_browser() -> subprocess.Popen | None:
    """Launch browser if not already running. Returns Popen handle or None."""
    if _is_browser_running():
        return None

    binary = _find_browser()
    if not binary:
        print(json.dumps({"error": "No browser found. Install Brave or Chromium."}))
        sys.exit(1)

    cmd = [binary] + HEADLESS_ARGS
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Wait for port to open
    deadline = time.monotonic() + BROWSER_TIMEOUT
    while time.monotonic() < deadline:
        if _is_browser_running():
            return proc
        time.sleep(0.2)

    print(json.dumps({"error": f"Browser did not start on port {DEBUG_PORT} within {BROWSER_TIMEOUT}s"}))
    sys.exit(1)


def _fetch_json(url: str) -> Any:
    """HTTP GET and parse JSON."""
    with urllib.request.urlopen(url, timeout=5) as resp:
        return json.loads(resp.read().decode())


def _get_ws_url() -> str:
    """Return WebSocket debugger URL for the first page target."""
    targets = _fetch_json(f"http://localhost:{DEBUG_PORT}/json/list")
    for target in targets:
        if target.get("type") == "page":
            return target["webSocketDebuggerUrl"]
    raise RuntimeError("No page target found on CDP endpoint")


# ---------------------------------------------------------------------------
# CDP Client
# ---------------------------------------------------------------------------

class CDPClient:
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.ws: websockets.WebSocketClientProtocol | None = None
        self._seq = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._events: list[dict] = []

    async def connect(self) -> None:
        self.ws = await websockets.connect(self.ws_url)
        asyncio.create_task(self._read_loop())

    async def disconnect(self) -> None:
        if self.ws:
            await self.ws.close()
            self.ws = None

    async def _read_loop(self) -> None:
        assert self.ws is not None
        async for raw in self.ws:
            msg = json.loads(raw)
            if "id" in msg and msg["id"] in self._pending:
                self._pending[msg["id"]].set_result(msg)
            else:
                self._events.append(msg)

    async def send(self, method: str, params: dict | None = None) -> dict:
        assert self.ws is not None
        self._seq += 1
        msg_id = self._seq
        payload = {"id": msg_id, "method": method, "params": params or {}}
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[msg_id] = fut
        await self.ws.send(json.dumps(payload))
        result = await asyncio.wait_for(fut, timeout=15)
        if "error" in result:
            raise RuntimeError(f"CDP error: {result['error']}")
        return result.get("result", {})

    async def enable_domain(self, domain: str) -> None:
        await self.send(f"{domain}.enable")

    def drain_events(self) -> list[dict]:
        evs = self._events[:]
        self._events.clear()
        return evs


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

async def cmd_navigate(url: str) -> dict:
    _ensure_browser()
    ws_url = _get_ws_url()
    async with websockets.connect(ws_url) as ws:
        client = CDPClient(ws_url)
        client.ws = ws
        asyncio.create_task(client._read_loop())
        result = await client.send("Page.navigate", {"url": url})
        return {"ok": True, "frameId": result.get("frameId")}


async def cmd_screenshot(output: str | None = None, full_page: bool = False) -> dict:
    _ensure_browser()
    ws_url = _get_ws_url()
    async with websockets.connect(ws_url) as ws:
        client = CDPClient(ws_url)
        client.ws = ws
        asyncio.create_task(client._read_loop())

        if full_page:
            # Get full page dimensions
            await client.send("Page.enable")
            metrics = await client.send("Page.getLayoutMetrics")
            width = int(metrics["contentSize"]["width"])
            height = int(metrics["contentSize"]["height"])
            await client.send("Emulation.setDeviceMetricsOverride", {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": False,
            })
            params = {"format": "png", "captureBeyondViewport": True}
        else:
            params = {"format": "png"}

        result = await client.send("Page.captureScreenshot", params)
        b64data = result["data"]
        png_bytes = base64.b64decode(b64data)

        path = output or f"screenshot-{int(time.time())}.png"
        pathlib.Path(path).write_bytes(png_bytes)
        return {"ok": True, "file": path, "size": len(png_bytes)}


async def cmd_eval(expression: str) -> dict:
    _ensure_browser()
    ws_url = _get_ws_url()
    async with websockets.connect(ws_url) as ws:
        client = CDPClient(ws_url)
        client.ws = ws
        asyncio.create_task(client._read_loop())
        result = await client.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
        })
        return {"ok": True, "result": result.get("result", {}).get("value")}


async def cmd_console(url: str | None = None) -> dict:
    _ensure_browser()
    ws_url = _get_ws_url()
    async with websockets.connect(ws_url) as ws:
        client = CDPClient(ws_url)
        client.ws = ws
        asyncio.create_task(client._read_loop())
        await client.enable_domain("Runtime")
        if url:
            await client.send("Page.navigate", {"url": url})
            await asyncio.sleep(2)
        else:
            await asyncio.sleep(1)

        events = client.drain_events()
        logs = [
            {
                "type": e["params"].get("type"),
                "text": " ".join(str(a.get("value", a)) for a in e["params"].get("args", [])),
            }
            for e in events
            if e.get("method") == "Runtime.consoleAPICalled"
        ]
        return {"ok": True, "logs": logs}


async def cmd_network(url: str | None = None) -> dict:
    _ensure_browser()
    ws_url = _get_ws_url()
    async with websockets.connect(ws_url) as ws:
        client = CDPClient(ws_url)
        client.ws = ws
        asyncio.create_task(client._read_loop())
        await client.enable_domain("Network")
        if url:
            await client.send("Page.navigate", {"url": url})
            await asyncio.sleep(3)
        else:
            await asyncio.sleep(2)

        events = client.drain_events()
        requests = [
            {
                "url": e["params"].get("request", {}).get("url"),
                "method": e["params"].get("request", {}).get("method"),
                "type": e["params"].get("type"),
            }
            for e in events
            if e.get("method") == "Network.requestWillBeSent"
        ]
        return {"ok": True, "requests": requests}


async def cmd_dom(selector: str | None = None) -> dict:
    _ensure_browser()
    ws_url = _get_ws_url()
    async with websockets.connect(ws_url) as ws:
        client = CDPClient(ws_url)
        client.ws = ws
        asyncio.create_task(client._read_loop())
        await client.enable_domain("DOM")
        doc = await client.send("DOM.getDocument")
        root = doc["root"]

        if selector:
            node_id = root["nodeId"]
            found = await client.send("DOM.querySelector", {
                "nodeId": node_id,
                "selector": selector,
            })
            if found.get("nodeId"):
                detail = await client.send("DOM.describeNode", {
                    "nodeId": found["nodeId"],
                    "depth": 2,
                })
                return {"ok": True, "node": detail.get("node", {})}
            return {"ok": True, "node": None}
        return {"ok": True, "title": root.get("nodeValue", ""), "nodeName": root.get("nodeName", "")}


def _kill_browser() -> dict:
    """Terminate the browser process listening on DEBUG_PORT."""
    system = platform.system()
    killed = False
    if system == "Darwin":
        # macOS: use lsof to find PID and kill it
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{DEBUG_PORT}"],
                capture_output=True,
                text=True,
                check=True,
            )
            for pid_str in result.stdout.strip().splitlines():
                pid = int(pid_str)
                os.kill(pid, signal.SIGTERM)
                killed = True
        except subprocess.CalledProcessError:
            pass
    else:
        # Linux: use fuser or ss
        for cmd in [
            ["fuser", "-k", f"{DEBUG_PORT}/tcp"],
            ["kill", "-9", "$(ss", "-ltnp", f"| grep {DEBUG_PORT}", "|", "awk", "'{print $7}'", "|", "cut -d','", "-f2", "|", "cut -d'='", "-f2)"],
        ]:
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                killed = True
                break
            except Exception:
                pass
    return {"ok": True, "stopped": killed}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only browser via CDP")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_nav = sub.add_parser("navigate", help="Navigate to URL")
    p_nav.add_argument("url")

    p_shot = sub.add_parser("screenshot", help="Capture screenshot")
    p_shot.add_argument("--output", "-o", default=None)
    p_shot.add_argument("--full-page", action="store_true")

    p_eval = sub.add_parser("eval", help="Evaluate JavaScript expression")
    p_eval.add_argument("expression")

    p_console = sub.add_parser("console", help="Collect console logs")
    p_console.add_argument("--url", default=None)

    p_network = sub.add_parser("network", help="Collect network requests")
    p_network.add_argument("--url", default=None)

    p_dom = sub.add_parser("dom", help="Get DOM information")
    p_dom.add_argument("--selector", default=None)

    p_stop = sub.add_parser("stop", help="Stop the headless browser process")

    args = parser.parse_args()

    async def run() -> None:
        if args.cmd == "navigate":
            result = await cmd_navigate(args.url)
        elif args.cmd == "screenshot":
            result = await cmd_screenshot(args.output, args.full_page)
        elif args.cmd == "eval":
            result = await cmd_eval(args.expression)
        elif args.cmd == "console":
            result = await cmd_console(args.url)
        elif args.cmd == "network":
            result = await cmd_network(args.url)
        elif args.cmd == "dom":
            result = await cmd_dom(args.selector)
        elif args.cmd == "stop":
            result = _kill_browser()
        else:
            raise ValueError(f"Unknown command: {args.cmd}")
        print(json.dumps(result, indent=2, default=str))

    asyncio.run(run())


if __name__ == "__main__":
    main()
