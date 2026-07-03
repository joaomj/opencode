#!/usr/bin/env python3

import argparse
import json
import os
import sys
import urllib.parse
from pathlib import Path

from dotenv import load_dotenv
from xdk import Client

from x_common import find_env_file

OAUTH_SCOPES = "bookmark.read tweet.read users.read offline.access"
CALLBACK_URI = "http://localhost:8080/callback"


def main() -> None:
    env_path = find_env_file()
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    client_id = os.getenv("X_API_CLIENT_ID")
    client_secret = os.getenv("X_API_CLIENT_SECRET")

    if not client_id:
        print("Error: X_API_CLIENT_ID not found in .env", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="One-time OAuth 2.0 setup for X bookmark sync",
    )
    parser.add_argument(
        "--token-file",
        required=True,
        help="Path where the OAuth token will be saved",
    )
    parser.add_argument(
        "--callback-url",
        default=None,
        help="Full redirect URL after authorizing (contains ?code=...)",
    )
    args = parser.parse_args()

    token_path = Path(args.token_file).resolve()
    token_path.parent.mkdir(parents=True, exist_ok=True)
    verifier_path = Path(str(token_path) + ".pkcetmp")

    client = Client(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=CALLBACK_URI,
        scope=OAUTH_SCOPES,
    )

    if args.callback_url:
        if not verifier_path.exists():
            print(
                "Error: missing PKCE verifier file. Run without --callback-url first.",
                file=sys.stderr,
            )
            sys.exit(1)
        code_verifier = verifier_path.read_text().strip()
        client.oauth2_auth.set_pkce_parameters(code_verifier)
        _handle_callback(client, token_path, args.callback_url)
        verifier_path.unlink(missing_ok=True)
        return

    auth_url = client.get_authorization_url()
    code_verifier = client.oauth2_auth.get_code_verifier()
    verifier_path.write_text(code_verifier)
    _print_auth_instructions(auth_url, args)


def _print_auth_instructions(auth_url: str, args: argparse.Namespace) -> None:
    print(file=sys.stderr)
    print("=" * 56, file=sys.stderr)
    print("  STEP 1: Open this URL in YOUR browser (not this machine)", file=sys.stderr)
    print("=" * 56, file=sys.stderr)
    print(file=sys.stderr)
    print(auth_url, file=sys.stderr)
    print(file=sys.stderr)
    print("=" * 56, file=sys.stderr)
    print("  STEP 2: Authorize the app", file=sys.stderr)
    print("=" * 56, file=sys.stderr)
    print(file=sys.stderr)
    print(f"  Redirect URI: {CALLBACK_URI}", file=sys.stderr)
    print(f"  Scopes:        {OAUTH_SCOPES}", file=sys.stderr)
    print(file=sys.stderr)
    print("  After authorizing, your browser redirects to a page that says:", file=sys.stderr)
    print("    'Connection refused' (this is expected).", file=sys.stderr)
    print(file=sys.stderr)
    print("=" * 56, file=sys.stderr)
    print("  STEP 3: Copy and paste the redirect URL here", file=sys.stderr)
    print("=" * 56, file=sys.stderr)
    print(file=sys.stderr)
    print("  Copy the FULL URL from your browser address bar.", file=sys.stderr)
    print(f"  It looks like: {CALLBACK_URI}?code=...", file=sys.stderr)
    print(file=sys.stderr)
    print("  Then run:", file=sys.stderr)
    cmd = f"uv run python auth_x.py --token-file {args.token_file} --callback-url '<URL>'"
    print(f"    {cmd}", file=sys.stderr)
    print(file=sys.stderr)


def _handle_callback(client: Client, token_path: Path, callback_url: str) -> None:
    parsed = urllib.parse.urlparse(callback_url)
    params = urllib.parse.parse_qs(parsed.query)
    if "code" not in params:
        print("Error: no 'code' parameter found in callback URL", file=sys.stderr)
        print(f"Parsed URL: {parsed}", file=sys.stderr)
        print(f"Query params: {dict(params)}", file=sys.stderr)
        sys.exit(1)

    code = params["code"][0]
    print("[auth] Exchanging authorization code for tokens...", file=sys.stderr)
    token_data = client.exchange_code(code)
    token_path.write_text(json.dumps(token_data, indent=2))
    print(f"[auth] Token saved to {token_path}", file=sys.stderr)
    print("[auth] Ready. Run: uv run python sync_x_bookmarks.py --max-bookmarks 1", file=sys.stderr)


if __name__ == "__main__":
    main()
