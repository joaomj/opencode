from __future__ import annotations

import json
import time
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

import httpx

DEFAULT_TEAMS_BASE = "https://teams.microsoft.com"
CLIENT_VERSION = "1415/1.0.0.2025010401"


def _b64url_decode(data: str) -> bytes:
    data = data.replace("-", "+").replace("_", "/")
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return __import__("base64").urlsafe_b64decode(data)


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    return json.loads(_b64url_decode(parts[1]))


def _detect_region(skypetoken: str) -> str:
    try:
        payload = _decode_jwt_payload(skypetoken)
        endpoint = payload.get("skypeendpoint", "")
        m = endpoint and __import__("re").search(r"/chatsvc/([a-z]+)", endpoint)
        if m:
            return m.group(1)
    except Exception:
        pass
    return "amer"


@dataclass
class Message:
    id: str
    sender: str
    timestamp: str
    content: str
    message_type: str = "Text"
    reply_to_id: str | None = None
    conversation_id: str = ""
    channel_identity: dict[str, str] | None = None
    is_deleted: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    id: str
    topic: str
    chat_type: str  # oneOnOne, group, meeting, channel
    last_message_time: str = ""
    last_message_from: str = ""
    last_message_preview: str = ""


class TeamsClient:
    def __init__(self, skypetoken: str, authtoken: str, tenant_id: str = ""):
        self.skypetoken = skypetoken
        self.authtoken = authtoken
        self.tenant_id = tenant_id
        self.region = _detect_region(skypetoken)
        self.base = DEFAULT_TEAMS_BASE
        self._client = httpx.Client(timeout=30.0)

    @property
    def _read_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": self.base,
            "Referer": f"{self.base}/",
            "Authentication": f"skypetoken={self.skypetoken}",
            "Authorization": f"Bearer {self.authtoken}",
        }

    @property
    def _write_headers(self) -> dict[str, str]:
        return {**self._read_headers, "X-Ms-Client-Version": CLIENT_VERSION}

    def _url(self, path: str) -> str:
        return f"{self.base}{path.format(region=self.region)}"

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        url = self._url(path)
        r = self._client.request(method, url, **kwargs)
        return r

    def test_auth(self) -> bool:
        r = self._request(
            "GET",
            "/api/chatsvc/{region}/v1/users/ME/conversations?pageSize=1",
            headers=self._read_headers,
        )
        return r.status_code == 200

    def list_conversations(self, limit: int = 50) -> list[Conversation]:
        r = self._request(
            "GET",
            "/api/chatsvc/{region}/v1/users/ME/conversations?view=msnp24Equivalent&pageSize=200",
            headers=self._read_headers,
        )
        r.raise_for_status()
        data = r.json()

        conversations: list[Conversation] = []
        raw_list = data if isinstance(data, list) else data.get("conversations", [])
        for c in raw_list:
            cid = c.get("id", "")
            if not cid:
                continue
            thread_props = c.get("threadProperties", {}) or {}
            topic = thread_props.get("topic", "") or ""
            last_msg = c.get("lastMessage", {}) or {}
            conv = Conversation(
                id=cid,
                topic=topic,
                chat_type=_classify_chat_type(cid),
                last_message_time=(
                    last_msg.get("originalarrivaltime", "")
                    or last_msg.get("composetime", "")
                ),
                last_message_from=last_msg.get("imdisplayname", ""),
                last_message_preview=_clean_content(last_msg.get("content", "")),
            )
            conversations.append(conv)

        return conversations[:limit]

    def get_messages(
        self, conversation_id: str, limit: int = 20
    ) -> list[Message]:
        enc_id = quote(conversation_id, safe="")
        r = self._request(
            "GET",
            f"/api/chatsvc/{{region}}/v1/users/ME/conversations/{enc_id}/messages",
            headers=self._read_headers,
        )
        r.raise_for_status()
        data = r.json()

        messages = data.get("messages", data) if isinstance(data, dict) else data
        if not isinstance(messages, list):
            messages = data if isinstance(data, list) else []

        parsed: list[Message] = []
        for m in reversed(messages):
            parsed.append(_parse_message(m, conversation_id))

        return parsed[-limit:] if limit > 0 else parsed

    def send_message(
        self,
        conversation_id: str,
        content: str,
        reply_to: str | None = None,
        display_name: str = "",
        message_type: str = "Text",
    ) -> str:
        conversation_path = conversation_id
        if reply_to:
            conversation_path = f"{conversation_id};messageid={reply_to}"
        enc_path = quote(conversation_path, safe="")

        client_msg_id = f"{int(time.time() * 1000)}{random.randint(100000, 999999)}"
        body: dict[str, Any] = {
            "content": content,
            "messagetype": "RichText/Html" if message_type == "html" else "Text",
            "contenttype": "text",
            "imdisplayname": display_name,
            "clientmessageid": client_msg_id,
        }

        path = f"/api/chatsvc/{{region}}/v1/users/ME/conversations/{enc_path}/messages"
        r = self._request("POST", path, headers=self._write_headers, json=body)
        r.raise_for_status()
        return r.text

    def close(self):
        self._client.close()


def _classify_chat_type(conv_id: str) -> str:
    if "meeting_" in conv_id:
        return "meeting"
    if "@thread.tacv2" in conv_id:
        return "channel"
    if "@unq.gbl.spaces" in conv_id:
        return "oneOnOne"
    if "@thread.v2" in conv_id:
        return "group"
    return "chat"


_HTML_ENTITIES = {
    "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
    "&quot;": "\"", "&#39;": "'", "&apos;": "'",
}


def _clean_content(content: str) -> str:
    import re
    content = re.sub(r"<[^>]+>", "", content)
    for entity, replacement in _HTML_ENTITIES.items():
        content = content.replace(entity, replacement)
    return content[:500]


def _parse_message(raw: dict[str, Any], conv_id: str) -> Message:
    mid = raw.get("id", "")
    sender = raw.get("imdisplayname", "")
    if not sender:
        from_info = raw.get("from", "")
        if isinstance(from_info, dict):
            user = from_info.get("user", {}) or {}
            sender = user.get("displayName", "")
    msg_type = raw.get("messagetype", "Text")
    content = raw.get("content", "")
    if msg_type == "RichText/Html" and content:
        content = _clean_content(content)
    return Message(
        id=mid,
        sender=sender,
        timestamp=raw.get("composetime", "") or raw.get("originalarrivaltime", ""),
        content=content,
        message_type=msg_type,
        reply_to_id=None,
        conversation_id=conv_id,
        channel_identity=raw.get("channelIdentity"),
        is_deleted=bool(raw.get("deleted")),
        raw=raw,
    )
