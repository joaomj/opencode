from __future__ import annotations

import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


BRAVE_PROFILE = Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser/Default"

COOKIE_NAMES = {
    "skypetoken": "skypetoken_asm",
    "authtoken": "authtoken",
    "authtoken_asm": "authtoken_asm",
    "tenant_id": "tenantId",
}

COOKIE_HOSTS = ["teams.microsoft.com", ".asyncgw.teams.microsoft.com"]


@dataclass
class TeamsAuth:
    skypetoken: str
    authtoken: str
    tenant_id: str
    authtoken_asm: str = ""


def _get_brave_key() -> bytes | None:
    result = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", "Brave Safe Storage"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip().encode()


def _derive_key(password: bytes) -> bytes:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=16,
        salt=b"saltysalt",
        iterations=1003,
        backend=default_backend(),
    )
    return kdf.derive(password)


def _decrypt_value(encrypted_value: bytes, key: bytes) -> bytes:
    if not encrypted_value.startswith(b"v10"):
        raise ValueError(f"unsupported encryption version: {encrypted_value[:3]!r}")
    ciphertext = encrypted_value[3:]
    iv = b" " * 16
    cipher = Cipher(algorithms.AES128(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    plain = decryptor.update(ciphertext) + decryptor.finalize()
    pad_len = plain[-1]
    if 0 < pad_len <= 16:
        plain = plain[:-pad_len]
    return plain


_JWT_STARTS = (b"Bearer%", b"eyJ")


def _extract_jwt_text(raw: bytes) -> str:
    for prefix in _JWT_STARTS:
        idx = raw.find(prefix)
        if idx >= 0:
            decoded = unquote(raw[idx:].decode("ascii"))
            return _strip_bearer_prefix(decoded)
    raise ValueError("no JWT/Bearer marker found in decrypted value")


def _strip_bearer_prefix(text: str) -> str:
    for prefix in ("Bearer=", "Bearer "):
        if text.startswith(prefix):
            return text[len(prefix):]
    return text


_HEADER_LENGTH = 32


def _extract_plain_text(raw: bytes) -> str:
    for prefix in _JWT_STARTS:
        idx = raw.find(prefix)
        if idx >= 0:
            return unquote(raw[idx:].decode("ascii"))
    try:
        return raw.decode("ascii")
    except (UnicodeDecodeError, ValueError):
        pass
    try:
        return raw[_HEADER_LENGTH:].decode("ascii")
    except (UnicodeDecodeError, ValueError):
        pass
    return raw.decode("utf-8", errors="replace")


def extract_auth(profile: str | None = None) -> TeamsAuth | None:
    profile_path = Path(profile) if profile else BRAVE_PROFILE
    cookies_db = profile_path / "Cookies"

    if not cookies_db.exists():
        raise FileNotFoundError(f"Cookies database not found: {cookies_db}")

    key = _get_brave_key()
    if not key:
        raise RuntimeError("Failed to retrieve encryption key from Keychain")

    derived = _derive_key(key)

    conn = sqlite3.connect(str(cookies_db))
    conn.row_factory = sqlite3.Row

    hosts_placeholder = ",".join("?" for _ in COOKIE_HOSTS)
    rows = conn.execute(
        f"SELECT host_key, name, encrypted_value FROM cookies WHERE host_key IN ({hosts_placeholder})",
        COOKIE_HOSTS,
    ).fetchall()

    conn.close()

    tokens: dict[str, str] = {}
    for row in rows:
        name = row["name"]
        try:
            raw = _decrypt_value(row["encrypted_value"], derived)
        except Exception:
            continue
        try:
            tokens[name] = _extract_jwt_text(raw)
        except ValueError:
            tokens[name] = _extract_plain_text(raw)

    skypetoken = tokens.get(COOKIE_NAMES["skypetoken"], "")
    authtoken = tokens.get(COOKIE_NAMES["authtoken"], "")
    authtoken_asm = tokens.get(COOKIE_NAMES["authtoken_asm"], "")
    tenant = tokens.get(COOKIE_NAMES["tenant_id"], "")

    if not skypetoken or not authtoken:
        return None

    return TeamsAuth(
        skypetoken=skypetoken,
        authtoken=authtoken,
        tenant_id=tenant,
        authtoken_asm=authtoken_asm,
    )
