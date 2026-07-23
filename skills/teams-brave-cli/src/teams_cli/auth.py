from __future__ import annotations

from dataclasses import dataclass
from typing import Any

COOKIE_DOMAINS = ("teams.microsoft.com", ".asyncgw.teams.microsoft.com")


class AuthUnavailable(RuntimeError):
    """Raised when the selected Teams authentication provider cannot authenticate."""


@dataclass(frozen=True)
class TeamsAuth:
    skypetoken: str
    authtoken: str
    tenant_id: str = ""
    authtoken_asm: str = ""


def auth_from_cookies(cookies: list[dict[str, Any]]) -> TeamsAuth:
    """Build Teams API credentials from Chromium CDP cookies."""
    values = {
        cookie.get("name"): cookie.get("value")
        for cookie in cookies
        if (
            isinstance(cookie.get("name"), str)
            and isinstance(cookie.get("value"), str)
            and cookie.get("domain") in COOKIE_DOMAINS
        )
    }
    skypetoken = values.get("skypetoken_asm", "")
    authtoken = values.get("authtoken", "")
    if not skypetoken or not authtoken:
        raise AuthUnavailable("Required Teams cookies are unavailable in the browser profile.")
    return TeamsAuth(
        skypetoken=skypetoken,
        authtoken=authtoken,
        tenant_id=values.get("tenantId", ""),
        authtoken_asm=values.get("authtoken_asm", ""),
    )
