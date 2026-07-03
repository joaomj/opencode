import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import requests

URL_PATTERN = re.compile(
    r"^(?:https?://)?(?:www\.)?(?:x\.com|twitter\.com)/([a-zA-Z0-9_]+)/status/(\d+)"
)

TWEET_FIELDS = [
    "article",
    "note_tweet",
    "created_at",
    "public_metrics",
    "entities",
    "attachments",
    "lang",
    "possibly_sensitive",
    "referenced_tweets",
    "conversation_id",
    "in_reply_to_user_id",
]

EXPANSIONS = [
    "author_id",
    "attachments.media_keys",
    "referenced_tweets.id",
]

USER_FIELDS = ["username", "name"]
MEDIA_FIELDS = ["url", "type", "preview_image_url", "alt_text"]

MEDIA_EXT_FALLBACK = {
    "photo": "jpg",
    "video": "mp4",
    "animated_gif": "gif",
}


def find_env_file() -> str | None:
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path.home() / ".config" / "opencode" / ".env",
    ]
    for p in candidates:
        if p.is_file():
            return str(p)
    return None


def parse_url(url: str) -> str:
    m = URL_PATTERN.match(url.strip())
    if not m:
        raise ValueError(f"Invalid X URL: {url!r}")
    return m.group(2)


def format_filename(username: str, created_at: str, tweet_id: str) -> str:
    safe_username = re.sub(r"[^a-zA-Z0-9_]", "_", username)
    ts = created_at.replace(":", "-").replace("T", "_").replace("Z", "").split(".")[0]
    return f"{safe_username}_{ts}_{tweet_id}.md"


def build_users_map(includes: dict) -> dict:
    return {u["id"]: u for u in (includes.get("users") or [])}


def build_frontmatter(data: dict, users: dict, url: str) -> list[str]:
    tweet_id = data["id"]
    author_id = data.get("author_id", "")
    created_at = data.get("created_at", "")
    author = users.get(author_id, {})
    username = author.get("username", author_id)
    fetched_at = datetime.now(UTC).isoformat()
    return [
        "---",
        f"url: {url}",
        f"author: {username}",
        f"created_at: {created_at}",
        f"tweet_id: {tweet_id}",
        f"fetched_at: {fetched_at}",
        "---",
    ]


def media_extension(url: str, media_type: str) -> str:
    parsed = urlparse(url)
    path = parsed.path
    ext = Path(path).suffix.lstrip(".")
    if ext:
        return ext
    return MEDIA_EXT_FALLBACK.get(media_type, "bin")


def download_media(media_list: list, media_dir: Path) -> dict[str, str]:
    media_dir.mkdir(parents=True, exist_ok=True)
    mapping: dict[str, str] = {}
    for m in media_list:
        m_key = m.get("media_key", "")
        m_type = m.get("type", "unknown")
        m_url = m.get("url") or m.get("preview_image_url", "")
        if not m_url:
            continue
        ext = media_extension(m_url, m_type)
        local_name = f"{m_key}.{ext}"
        local_path = media_dir / local_name
        if local_path.exists():
            mapping[m_key] = local_name
            continue
        try:
            r = requests.get(m_url, timeout=30)
            r.raise_for_status()
            local_path.write_bytes(r.content)
            mapping[m_key] = local_name
        except requests.RequestException as e:
            print(f"Warning: failed to download {m_url}: {e}", file=sys.stderr)
    return mapping


def build_media_section(
    media_list: list, media_mapping: dict[str, str], media_rel_dir: str
) -> list[str]:
    if not media_list:
        return []
    lines = ["", "## Media", ""]
    for m in media_list:
        m_key = m.get("media_key", "")
        m_type = m.get("type", "unknown")
        alt = m.get("alt_text", "") or m_type
        local_name = media_mapping.get(m_key)
        if local_name:
            lines.append(f"![{alt}]({media_rel_dir}/{local_name})")
        else:
            m_url = m.get("url") or m.get("preview_image_url", "")
            if m_url:
                lines.append(f"[{m_type}]({m_url})")
            else:
                lines.append(f"- {m_type} (unavailable)")
    return lines


def build_references_section(
    referenced: list, includes: dict, users: dict
) -> list[str]:
    if not referenced:
        return []
    ref_tweets = includes.get("tweets") or []
    lines = ["", "## References", ""]
    for ref in referenced:
        ref_id = ref.get("id", "")
        ref_type = ref.get("type", "unknown")
        ref_tweet = next(
            (t for t in ref_tweets if t.get("id") == ref_id), None
        )
        ref_username = ""
        if ref_tweet:
            ref_author_id = ref_tweet.get("author_id", "")
            ref_user = users.get(ref_author_id, {})
            ref_username = ref_user.get("username", "")
        label = (
            f"https://x.com/{ref_username}/status/{ref_id}"
            if ref_username
            else ref_id
        )
        lines.append(f"- {ref_type}: {label}")
    return lines


def build_markdown(
    data: dict,
    includes: dict,
    url: str,
    media_mapping: dict[str, str],
    media_rel_dir: str,
) -> str:
    text = data.get("note_tweet", {}).get("text") or data.get("text", "")
    article = data.get("article")

    users = build_users_map(includes)
    media_list = includes.get("media") or []
    referenced = data.get("referenced_tweets") or []

    parts = []
    parts.extend(build_frontmatter(data, users, url))
    parts.extend(["", text, ""])

    if article:
        parts.extend(["", "## Article", ""])
        if isinstance(article, dict):
            parts.append(f"Article metadata: {json.dumps(article)}")
        else:
            parts.append(str(article))

    parts.extend(build_media_section(media_list, media_mapping, media_rel_dir))
    parts.extend(build_references_section(referenced, includes, users))

    return "\n".join(parts).rstrip("\n") + "\n"


def write_output(
    data: dict, includes: dict, url: str, output_dir: Path
) -> Path:
    author_id = data.get("author_id", "")
    users = build_users_map(includes)
    author = users.get(author_id, {})
    username = author.get("username", author_id)
    created_at = data.get("created_at", "")
    tweet_id = data["id"]

    filename = format_filename(username, created_at, tweet_id)
    output_path = output_dir / filename

    stem = output_path.stem
    media_dir_name = f"{stem}_media"
    media_dir = output_dir / media_dir_name
    media_rel_dir = media_dir_name

    media_mapping = download_media(includes.get("media") or [], media_dir)

    markdown = build_markdown(
        data, includes, url, media_mapping, media_rel_dir
    )
    output_path.write_text(markdown, encoding="utf-8")
    return output_path
