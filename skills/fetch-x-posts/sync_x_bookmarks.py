#!/usr/bin/env python3

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from xdk import Client

_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from x_common import (  # noqa: I001, E402
    EXPANSIONS,
    MEDIA_FIELDS,
    TWEET_FIELDS,
    USER_FIELDS,
    build_users_map,
    download_media,
    find_env_file,
    format_filename,
    build_markdown,
)

DEFAULT_OUTPUT_DIR = "x-bookmarks"
MAX_RESULTS = 100
RETRY_MAX = 3
RETRY_BASE_DELAY = 1.0
RATE_LIMIT_STATUS = 429
AUTH_SCRIPT = "auth_x.py"


def api_get(url: str, access_token: str, params: dict | None = None) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    for attempt in range(RETRY_MAX + 1):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 0
            if status == RATE_LIMIT_STATUS and attempt < RETRY_MAX:
                delay = RETRY_BASE_DELAY * (2**attempt)
                print(f"Rate limited. Retrying in {delay:.1f}s...", file=sys.stderr)
                time.sleep(delay)
                continue
            raise
        except requests.exceptions.RequestException as e:
            raise e


def load_access_token(token_path: Path) -> str:
    if not token_path.exists():
        auth = Path(__file__).resolve().parent / AUTH_SCRIPT
        print(
            f"No OAuth token at {token_path}.\n"
            f"Run the auth script first:\n"
            f"  uv run python {auth} --token-file {token_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        token_data = json.loads(token_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        auth = Path(__file__).resolve().parent / AUTH_SCRIPT
        print(
            f"Corrupted token file: {e}. Re-run:\n"
            f"  uv run python {auth} --token-file {token_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    client = Client(
        client_id=os.getenv("X_API_CLIENT_ID"),
        client_secret=os.getenv("X_API_CLIENT_SECRET"),
        token=token_data,
    )

    if client.is_token_expired():
        print("Token expired. Refreshing...", file=sys.stderr)
        try:
            new_token = client.refresh_token()
            token_path.write_text(json.dumps(new_token, indent=2))
        except Exception as e:
            auth = Path(__file__).resolve().parent / AUTH_SCRIPT
            print(
                f"Token refresh failed: {e}. Re-authorize:\n"
                f"  uv run python {auth} --token-file {token_path}",
                file=sys.stderr,
            )
            sys.exit(1)

    return client.access_token


def get_authenticated_user_id(access_token: str) -> str:
    data = api_get("https://api.x.com/2/users/me", access_token)
    return data["data"]["id"]


def fetch_bookmarks_all(access_token: str, user_id: str) -> list[dict]:
    bookmarks = []
    next_token = None
    base_url = f"https://api.x.com/2/users/{user_id}/bookmarks"
    while True:
        params = {
            "max_results": MAX_RESULTS,
            "tweet.fields": ",".join(TWEET_FIELDS),
            "expansions": ",".join(EXPANSIONS),
            "user.fields": ",".join(USER_FIELDS),
            "media.fields": ",".join(MEDIA_FIELDS),
        }
        if next_token:
            params["pagination_token"] = next_token

        data = api_get(base_url, access_token, params)
        bookmarks.append(data)
        meta = data.get("meta", {})
        next_token = meta.get("next_token")
        if not next_token or meta.get("result_count", 0) == 0:
            break
    return bookmarks


def fetch_folders(access_token: str, user_id: str) -> list[dict]:
    url = f"https://api.x.com/2/users/{user_id}/bookmarks/folders"
    data = api_get(url, access_token)
    return data.get("data", [])


def fetch_folder_members(
    access_token: str, user_id: str, folder_id: str
) -> list[str]:
    url = f"https://api.x.com/2/users/{user_id}/bookmarks/folders/{folder_id}"
    data = api_get(url, access_token)
    return [item["id"] for item in data.get("data", [])]


def load_state(state_path: Path) -> set[str]:
    if state_path.exists():
        state = json.loads(state_path.read_text())
        return set(state.get("processed_ids", []))
    return set()


def save_state(state_path: Path, processed_ids: set[str]):
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "processed_ids": sorted(processed_ids),
        "last_sync": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    state_path.write_text(json.dumps(state, indent=2))


def build_tweet_url(tweet_id: str, username: str) -> str:
    return f"https://x.com/{username}/status/{tweet_id}"


def sync_bookmarks(  # noqa: PLR0915
    access_token: str,
    output_dir: Path,
    state_path: Path,
    dry_run: bool,
    max_bookmarks: int = 0,
) -> None:
    print("Fetching authenticated user...", file=sys.stderr)
    user_id = get_authenticated_user_id(access_token)
    print(f"User ID: {user_id}", file=sys.stderr)

    print("Fetching folders...", file=sys.stderr)
    folders = fetch_folders(access_token, user_id)
    _ = {f["id"]: f["name"] for f in folders}

    print("Fetching folder memberships...", file=sys.stderr)
    tweet_to_folder: dict[str, str] = {}
    for folder in folders:
        folder_id = folder["id"]
        member_ids = fetch_folder_members(access_token, user_id, folder_id)
        for tid in member_ids:
            if tid not in tweet_to_folder:
                tweet_to_folder[tid] = folder["name"]

    print("Fetching all bookmarks...", file=sys.stderr)
    pages = fetch_bookmarks_all(access_token, user_id)

    existing_ids = load_state(state_path)
    new_count = 0

    for page in pages:
        data_list = page.get("data") or []
        includes = page.get("includes", {})
        users = build_users_map(includes)
        media_list = includes.get("media") or []

        for tweet in data_list:
            tweet_id = tweet["id"]
            if tweet_id in existing_ids:
                continue

            author_id = tweet.get("author_id", "")
            author = users.get(author_id, {})
            username = author.get("username", author_id)
            url = build_tweet_url(tweet_id, username)

            folder_name = tweet_to_folder.get(tweet_id, "Uncategorized")
            folder_dir = output_dir / folder_name

            if dry_run:
                fname = format_filename(username, tweet.get("created_at", ""), tweet_id)
                print(f"[dry-run] Would save: {folder_name}/{fname}")
                continue

            folder_dir.mkdir(parents=True, exist_ok=True)
            filename = format_filename(username, tweet.get("created_at", ""), tweet_id)
            output_path = folder_dir / filename

            stem = Path(filename).stem
            media_dir_name = f"{stem}_media"
            media_dir = folder_dir / media_dir_name
            media_rel_dir = media_dir_name

            media_mapping = download_media(media_list, media_dir)

            markdown = build_markdown(
                tweet, includes, url, media_mapping, media_rel_dir
            )
            output_path.write_text(markdown, encoding="utf-8")
            existing_ids.add(tweet_id)
            new_count += 1
            print(f"Saved: {output_path}")

            if max_bookmarks and new_count >= max_bookmarks:
                break
        else:
            continue
        break

    if not dry_run:
        save_state(state_path, existing_ids)

    print(f"Synced {new_count} new bookmarks.", file=sys.stderr)


def main() -> None:
    env_path = find_env_file()
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    if not os.getenv("X_API_CLIENT_ID"):
        print("Error: X_API_CLIENT_ID not found in .env", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Sync X bookmarks to local markdown files",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--state-file",
        default=None,
        help="State file path (default: <output-dir>/.sync-state.json)",
    )
    parser.add_argument(
        "--token-file",
        default=None,
        help="OAuth token file path (default: <output-dir>/.tokens.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List new bookmarks without saving",
    )
    parser.add_argument(
        "--max-bookmarks",
        type=int,
        default=0,
        help="Stop after processing N bookmarks (0 = unlimited)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    state_path = (
        Path(args.state_file) if args.state_file else output_dir / ".sync-state.json"
    )
    token_path = (
        Path(args.token_file) if args.token_file else output_dir / ".tokens.json"
    )

    try:
        access_token = load_access_token(token_path)
    except Exception as e:
        print(f"Authentication failed: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        sync_bookmarks(
            access_token, output_dir, state_path, args.dry_run, args.max_bookmarks
        )
    except Exception as e:
        print(f"Sync failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
