from __future__ import annotations

import os
import subprocess
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
    Path("/snap/bin/chromium"),
)
DEFAULT_CDP_HOST = "127.0.0.1"
DEFAULT_CDP_START_TIMEOUT_SECONDS = 30.0
DEFAULT_CDP_COMMAND_TIMEOUT_SECONDS = 15.0
TEAMS_BROWSER_URL = "https://teams.microsoft.com/v2"
DAEMON_START_APPROVAL_ENV = "TEAMS_CDP_START_APPROVED"
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


@dataclass(frozen=True)
class Settings:
    browser: str
    cdp_host: str
    cdp_start_timeout_seconds: float
    cdp_command_timeout_seconds: float
    profile_dir: Path
    socket_path: Path


DEFAULT_PROFILE_DIR = Path.home() / ".config" / "teams-cli" / "teams-authd-profile"


def load_settings() -> Settings:
    data_dir = Path.home() / ".config" / "teams-cli"
    browser = os.getenv("TEAMS_CDP_BROWSER") or _default_browser()
    profile_env = os.getenv("TEAMS_CDP_PROFILE")
    profile_dir = Path(profile_env) if profile_env else DEFAULT_PROFILE_DIR
    return Settings(
        browser=browser,
        cdp_host=DEFAULT_CDP_HOST,
        cdp_start_timeout_seconds=DEFAULT_CDP_START_TIMEOUT_SECONDS,
        cdp_command_timeout_seconds=DEFAULT_CDP_COMMAND_TIMEOUT_SECONDS,
        profile_dir=profile_dir,
        socket_path=data_dir / "run" / "teams-authd.sock",
    )


def _default_browser() -> str:
    candidates = MACOS_BROWSER_CANDIDATES if sys.platform == "darwin" else LINUX_BROWSER_CANDIDATES
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return str(candidates[0])


def graphical_session() -> bool:
    """Return whether the current session has a graphical browser available."""
    gui_override = _environment_flag("TEAMS_CDP_GUI")
    if gui_override is not None:
        return gui_override
    headless_override = _environment_flag("TEAMS_CDP_HEADLESS")
    if headless_override is not None:
        return not headless_override
    if sys.platform == "darwin":
        return _macos_graphical_session()
    if sys.platform.startswith("linux"):
        return bool(os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))
    return False


def _environment_flag(name: str) -> bool | None:
    value = os.getenv(name)
    if value is None:
        return None
    return value.strip().lower() in TRUE_VALUES


def _macos_graphical_session() -> bool:
    try:
        result = subprocess.run(
            ["launchctl", "print", f"gui/{os.getuid()}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0
