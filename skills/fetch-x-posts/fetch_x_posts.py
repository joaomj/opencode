#!/usr/bin/env python3

import argparse
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
from x_common import (  # noqa: E402
    EXPANSIONS,
    MEDIA_FIELDS,
    TWEET_FIELDS,
    USER_FIELDS,
    find_env_file,
    parse_url,
    write_output,
)

RETRY_MAX = 3
RETRY_BASE_DELAY = 1.0
RATE_LIMIT_STATUS = 429


def fetch_post(
    client: Client, tweet_id: str
) -> tuple[dict | None, dict | None, list | None]:
    last_exc = None
    for attempt in range(RETRY_MAX + 1):
        try:
            resp = client.posts.get_by_id(
                tweet_id,
                tweet_fields=TWEET_FIELDS,
                expansions=EXPANSIONS,
                user_fields=USER_FIELDS,
                media_fields=MEDIA_FIELDS,
            )
            return resp.data, resp.includes, resp.errors
        except requests.exceptions.HTTPError as e:
            last_exc = e
            status = e.response.status_code if e.response is not None else 0
            if status == RATE_LIMIT_STATUS and attempt < RETRY_MAX:
                delay = RETRY_BASE_DELAY * (2**attempt)
                print(
                    f"Rate limited. Retrying in {delay:.1f}s...",
                    file=sys.stderr,
                )
                time.sleep(delay)
                continue
        except requests.exceptions.RequestException as e:
            last_exc = e
            break

    if isinstance(last_exc, requests.exceptions.HTTPError):
        print(f"Error: {last_exc}", file=sys.stderr)
    elif isinstance(last_exc, requests.exceptions.RequestException):
        print(f"Network error: {last_exc}", file=sys.stderr)
    return None, None, None


def main() -> None:
    env_path = find_env_file()
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    token = os.getenv("X_API_BEARER_TOKEN")
    if not token:
        print("Error: X_API_BEARER_TOKEN not found in .env", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Fetch X post and save as markdown")
    parser.add_argument("url", help="X post URL (x.com/username/status/id)")
    parser.add_argument(
        "--output-dir",
        "-o",
        default=".",
        help="Output directory (default: cwd)",
    )
    args = parser.parse_args()

    try:
        tweet_id = parse_url(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    client = Client(bearer_token=token)
    data, includes, errors = fetch_post(client, tweet_id)

    if not data:
        if errors:
            err_msg = (
                errors[0].get("detail", "Unknown error") if errors else None
            )
            print(f"Error: {err_msg}", file=sys.stderr)
        sys.exit(1)

    output_path = write_output(data, includes, args.url, output_dir)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
