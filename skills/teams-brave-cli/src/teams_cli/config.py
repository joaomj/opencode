from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

MACOS_BROWSER_CANDIDATES = (
    Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
)
LINUX_BROWSER_CANDIDATES = (
    Path("/usr/bin/brave-browser"),
    Path("/usr/bin/brave"),
    Path("/usr/bin/chromium"),
    Path("/usr/bin/chromium-browser"),
    Path("/usr/bin/google-chrome"),
)
DEFAULT_CDP_HOST = "127.0.0.1"
DEFAULT_CDP_START_TIMEOUT_SECONDS = 30.0
DEFAULT_CDP_COMMAND_TIMEOUT_SECONDS = 15.0
TEAMS_BROWSER_URL = "https://teams.microsoft.com/v2"


@dataclass(frozen=True)
class Settings:
    browser: str
    cdp_host: str
    cdp_start_timeout_seconds: float
    cdp_command_timeout_seconds: float
    profile_dir: Path
    socket_path: Path


def load_settings() -> Settings:
    data_dir = Path.home() / ".config" / "teams-cli"
    browser = os.getenv("TEAMS_CDP_BROWSER") or _default_browser()
    return Settings(
        browser=browser,
        cdp_host=DEFAULT_CDP_HOST,
        cdp_start_timeout_seconds=DEFAULT_CDP_START_TIMEOUT_SECONDS,
        cdp_command_timeout_seconds=DEFAULT_CDP_COMMAND_TIMEOUT_SECONDS,
        profile_dir=data_dir / "teams-authd-profile",
        socket_path=data_dir / "run" / "teams-authd.sock",
    )


def _default_browser() -> str:
    candidates = MACOS_BROWSER_CANDIDATES if sys.platform == "darwin" else LINUX_BROWSER_CANDIDATES
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return str(candidates[0])
