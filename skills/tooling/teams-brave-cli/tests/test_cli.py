from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from teams_cli.logging_utils import redact_credentials

SKILL_DIR = Path(__file__).resolve().parents[1]


def _run_cli(
    home: Path,
    *arguments: str,
    extra_environment: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["HOME"] = str(home)
    if extra_environment:
        environment.update(extra_environment)
    return subprocess.run(
        [sys.executable, "-m", "teams_cli.main", *arguments],
        cwd=SKILL_DIR,
        env=environment,
        capture_output=True,
        text=True,
        input=input_text,
        check=False,
    )


def test_help_exposes_explicit_local_authentication_providers(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, "--help")

    assert result.returncode == 0
    assert "auth" in result.stdout
    assert "--auth-provider" in result.stdout
    assert "auto" in result.stdout
    assert "daemon" in result.stdout
    assert "login" not in result.stdout
    assert "mcp" not in result.stdout.lower()
    assert "TEAMS_SKYPETOKEN" not in result.stdout


def test_auth_reports_missing_local_brave_database(tmp_path: Path) -> None:
    profile = tmp_path / "Brave" / "Default"
    profile.mkdir(parents=True)

    result = _run_cli(tmp_path, "--profile", str(profile), "auth")

    assert result.returncode == 1
    assert "Brave cookies database not found" in result.stdout
    log_file = tmp_path / ".config" / "teams-cli" / "logs" / "teams-cli.log"
    assert log_file.exists()
    log_text = log_file.read_text(encoding="utf-8")
    assert "Teams authentication" in log_text
    assert "skypetoken" not in log_text.lower()
    assert "authtoken" not in log_text.lower()


def test_auto_provider_uses_profile_on_gui_without_starting_daemon(tmp_path: Path) -> None:
    result = _run_cli(
        tmp_path,
        "--auth-provider",
        "auto",
        "auth",
        extra_environment={"TEAMS_CDP_GUI": "1"},
    )

    assert result.returncode == 1
    assert "Brave cookies database not found" in result.stdout
    assert not (tmp_path / ".config" / "teams-cli" / "run" / "teams-authd.sock").exists()


def test_auto_provider_asks_before_starting_daemon_on_headless_host(tmp_path: Path) -> None:
    result = _run_cli(
        tmp_path,
        "auth",
        extra_environment={"TEAMS_CDP_HEADLESS": "1"},
        input_text="n\n",
    )

    assert result.returncode == 1
    assert "Start it now?" in result.stdout
    assert "was not started" in result.stdout
    assert not (tmp_path / ".config" / "teams-cli" / "run" / "teams-authd.sock").exists()


def test_auth_daemon_refuses_to_start_on_gui_host(tmp_path: Path) -> None:
    environment = os.environ.copy()
    environment.update({"HOME": str(tmp_path), "TEAMS_CDP_GUI": "1"})
    result = subprocess.run(
        [sys.executable, "-m", "teams_cli.authd"],
        cwd=SKILL_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert not (tmp_path / ".config" / "teams-cli" / "run" / "teams-authd.sock").exists()
    log_file = tmp_path / ".config" / "teams-cli" / "logs" / "teams-cli.log"
    assert "disabled in graphical sessions" in log_file.read_text(encoding="utf-8")


def test_auth_daemon_requires_cli_approval_on_headless_host(tmp_path: Path) -> None:
    environment = os.environ.copy()
    environment.update({"HOME": str(tmp_path), "TEAMS_CDP_HEADLESS": "1"})
    result = subprocess.run(
        [sys.executable, "-m", "teams_cli.authd"],
        cwd=SKILL_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert not (tmp_path / ".config" / "teams-cli" / "run" / "teams-authd.sock").exists()
    log_file = tmp_path / ".config" / "teams-cli" / "logs" / "teams-cli.log"
    assert "requires confirmation from the Teams CLI" in log_file.read_text(encoding="utf-8")


def test_log_redaction_removes_credentials_and_jwts() -> None:
    message = (
        "Authentication=secret-value Authorization=Bearer-value token=eyJheader.payload.signature"
    )

    redacted = redact_credentials(message)

    assert "secret-value" not in redacted
    assert "Bearer-value" not in redacted
    assert "eyJheader.payload.signature" not in redacted
    assert "[REDACTED]" in redacted
    assert "[REDACTED_JWT]" in redacted


def test_send_requires_confirmation_before_authentication(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, "send", "conversation-id", "message text")

    assert result.returncode == 2
    assert "Write blocked" in result.stdout


def test_reply_requires_confirmation_before_authentication(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, "reply", "conversation-id", "message-id", "message text")

    assert result.returncode == 2
    assert "Write blocked" in result.stdout
