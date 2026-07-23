from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

import keyring
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from keyring.errors import KeyringError

from teams_cli.auth import TeamsAuth
from teams_cli.logging_utils import get_logger

logger = get_logger(__name__)

MACOS_USER_DATA_DIR = Path("Library/Application Support/BraveSoftware/Brave-Browser")
LINUX_USER_DATA_DIRS = (
    Path(".config/BraveSoftware/Brave-Browser"),
    Path(".config/brave-browser"),
)
DEFAULT_PROFILE_NAME = "Default"
COOKIE_DATABASE_NAME = "Cookies"
COOKIE_HOSTS = ("teams.microsoft.com", ".asyncgw.teams.microsoft.com")
COOKIE_NAMES = {
    "skypetoken_asm": "skypetoken",
    "authtoken": "authtoken",
    "authtoken_asm": "authtoken_asm",
    "tenantId": "tenant_id",
}
KEYRING_CANDIDATES = (
    ("Brave Safe Storage", "Brave"),
    ("Chrome Safe Storage", "Chrome"),
    ("Chromium Safe Storage", "Chromium"),
)
AES_IV = b" " * 16
PBKDF2_SALT = b"saltysalt"
PBKDF2_ITERATIONS = 1003
PBKDF2_KEY_LENGTH = 16
_JWT_MARKERS = (b"Bearer%", b"eyJ")


def supported_platform() -> bool:
    """Return whether the current operating system is supported."""
    return sys.platform == "darwin" or sys.platform.startswith("linux")


def _default_user_data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / MACOS_USER_DATA_DIR
    if sys.platform.startswith("linux"):
        for relative_path in LINUX_USER_DATA_DIRS:
            candidate = Path.home() / relative_path
            if candidate.exists():
                return candidate
        return Path.home() / LINUX_USER_DATA_DIRS[0]
    raise RuntimeError(f"Unsupported platform: {sys.platform}. Only macOS and Linux are supported.")


def resolve_brave_profile(profile: str | None = None) -> Path:
    """Resolve a Brave profile directory from a path or profile name."""
    if profile:
        requested = Path(profile).expanduser()
        if requested.is_absolute() or profile.startswith((".", "~", "/")):
            return requested
        return _default_user_data_dir() / requested
    return _default_user_data_dir() / DEFAULT_PROFILE_NAME


def _get_brave_key(user_data_dir: Path) -> bytes:
    if sys.platform == "darwin":
        return _get_brave_key_macos()
    if sys.platform.startswith("linux"):
        return _get_brave_key_linux()
    raise RuntimeError(f"Unsupported platform: {sys.platform}. Only macOS and Linux are supported.")


def _get_brave_key_macos() -> bytes:
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-w", "-s", "Brave Safe Storage"],
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
    except FileNotFoundError as error:
        raise RuntimeError("The macOS security command is unavailable.") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Timed out while reading Brave Safe Storage from Keychain.") from error

    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(
            "Could not read Brave Safe Storage from Keychain. "
            "Approve the Keychain prompt and log into Teams in Brave."
        )
    logger.debug("Retrieved Brave encryption key from macOS Keychain")
    return result.stdout.strip().encode()


def _get_brave_key_linux() -> bytes:
    for service, username in KEYRING_CANDIDATES:
        try:
            password = keyring.get_password(service, username)
        except KeyringError as error:
            logger.debug("Linux keyring lookup failed for service=%s: %s", service, error)
            continue
        if password:
            logger.debug("Retrieved Brave encryption key from Linux keyring service=%s", service)
            return password.encode()

    raise RuntimeError(
        "Could not read Brave Safe Storage from the Linux keyring. "
        "Install and unlock a Secret Service keyring, then restart Brave."
    )


def _derive_key(password: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=PBKDF2_KEY_LENGTH,
        salt=PBKDF2_SALT,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password)


def _decrypt_value(encrypted_value: bytes, key: bytes) -> bytes:
    if not encrypted_value.startswith((b"v10", b"v11")):
        raise ValueError("unsupported Brave cookie encryption version")
    ciphertext = encrypted_value[3:]
    if not ciphertext or len(ciphertext) % 16 != 0:
        raise ValueError("invalid Brave cookie ciphertext length")
    cipher = Cipher(algorithms.AES128(key), modes.CBC(AES_IV))
    decryptor = cipher.decryptor()
    plain = decryptor.update(ciphertext) + decryptor.finalize()
    pad_len = plain[-1]
    if not 0 < pad_len <= 16:
        raise ValueError("invalid Brave cookie padding")
    return plain[:-pad_len]


def _extract_cookie_text(raw: bytes) -> str:
    for marker in _JWT_MARKERS:
        index = raw.find(marker)
        if index >= 0:
            return _strip_bearer_prefix(unquote(raw[index:].decode("ascii")))
    return raw.decode("utf-8", errors="replace")


def _strip_bearer_prefix(value: str) -> str:
    for prefix in ("Bearer=", "Bearer "):
        if value.startswith(prefix):
            return value[len(prefix) :]
    return value


def extract_auth(profile: str | None = None) -> TeamsAuth | None:
    """Extract Teams authentication cookies from a local Brave profile."""
    profile_path = resolve_brave_profile(profile)
    cookies_db = profile_path / COOKIE_DATABASE_NAME
    logger.info("Scanning Brave cookies profile=%s", profile_path)

    if not cookies_db.exists():
        raise FileNotFoundError(f"Brave cookies database not found: {cookies_db}")
    if not supported_platform():
        raise RuntimeError(
            f"Unsupported platform: {sys.platform}. Only macOS and Linux are supported."
        )

    key = _derive_key(_get_brave_key(profile_path.parent))
    rows = _read_cookie_rows(cookies_db)
    tokens: dict[str, str] = {}
    failures = 0

    for row in rows:
        try:
            value = row["encrypted_value"] or row["value"].encode()
            tokens[row["name"]] = _extract_cookie_text(_decrypt_value(value, key))
        except (UnicodeDecodeError, ValueError, TypeError):
            failures += 1

    logger.info(
        "Brave cookie scan complete profile=%s rows=%d decryption_failures=%d required_cookies=%s",
        profile_path,
        len(rows),
        failures,
        bool(tokens.get("skypetoken_asm") and tokens.get("authtoken")),
    )

    skypetoken = tokens.get("skypetoken_asm", "")
    authtoken = tokens.get("authtoken", "")
    if not skypetoken or not authtoken:
        return None

    return TeamsAuth(
        skypetoken=skypetoken,
        authtoken=authtoken,
        tenant_id=tokens.get("tenantId", ""),
        authtoken_asm=tokens.get("authtoken_asm", ""),
    )


def _read_cookie_rows(cookies_db: Path) -> list[sqlite3.Row]:
    try:
        with sqlite3.connect(cookies_db) as connection:
            connection.row_factory = sqlite3.Row
            host_placeholders = ",".join("?" for _ in COOKIE_HOSTS)
            name_placeholders = ",".join("?" for _ in COOKIE_NAMES)
            query = (
                "SELECT name, encrypted_value, value FROM cookies "
                f"WHERE host_key IN ({host_placeholders}) "
                f"AND name IN ({name_placeholders})"
            )
            parameters = (*COOKIE_HOSTS, *COOKIE_NAMES)
            return connection.execute(query, parameters).fetchall()
    except sqlite3.Error as error:
        logger.exception("Could not read Brave cookie database path=%s", cookies_db)
        raise RuntimeError(f"Could not read Brave cookies database: {cookies_db}") from error
