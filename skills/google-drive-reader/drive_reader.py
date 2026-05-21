from __future__ import annotations

import argparse
import logging
import os
import re
from pathlib import Path

LOGGER = logging.getLogger("drive-reader")

SKILL_DIR = Path.home() / ".config" / "opencode" / "skills" / "google-drive-reader"

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

MIME_EXPORT_MAP: dict[str, tuple[str, str]] = {
    "application/vnd.google-apps.document": (
        "text/markdown",
        ".md",
    ),
    "application/vnd.google-apps.spreadsheet": (
        "text/csv",
        ".csv",
    ),
    "application/vnd.google-apps.presentation": (
        "text/plain",
        ".txt",
    ),
    "application/vnd.google-apps.drawing": (
        "image/png",
        ".png",
    ),
}

MIME_TYPE_NAMES: dict[str, str] = {
    "application/vnd.google-apps.document": "Google Doc",
    "application/vnd.google-apps.spreadsheet": "Google Sheet",
    "application/vnd.google-apps.presentation": "Google Slides",
    "application/vnd.google-apps.drawing": "Google Drawing",
    "application/vnd.google-apps.folder": "Folder",
}

DRIVE_URL_PATTERNS = [
    re.compile(r"/document/d/([a-zA-Z0-9_-]+)"),
    re.compile(r"/spreadsheets/d/([a-zA-Z0-9_-]+)"),
    re.compile(r"/presentation/d/([a-zA-Z0-9_-]+)"),
    re.compile(r"/file/d/([a-zA-Z0-9_-]+)"),
    re.compile(r"[?&]id=([a-zA-Z0-9_-]+)"),
    re.compile(r"/folders/([a-zA-Z0-9_-]+)"),
]

FILE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{10,}$")


class DriveError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Google Drive Reader - read and search Drive files"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    read_parser = subparsers.add_parser("read", help="Read a file from Google Drive")
    read_parser.add_argument("file_id_or_url", help="File ID or Google Drive URL")
    read_parser.add_argument("--output", type=Path, help="Output file path")
    read_parser.add_argument(
        "--format",
        choices=["markdown", "csv", "txt", "pdf"],
        help="Override export format",
    )

    list_parser = subparsers.add_parser("list", help="List or search Drive files")
    list_parser.add_argument("query", nargs="?", default="", help="Drive query string")
    list_parser.add_argument(
        "--max-results", type=int, default=20, help="Max results (default: 20)"
    )
    list_parser.add_argument("--folder", help="Restrict to folder ID")
    list_parser.add_argument("--mime-type", help="Filter by MIME type")

    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def load_env_file(env_file: Path) -> None:
    if not env_file.exists():
        return
    for raw_line in env_file.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


def extract_file_id(input_str: str) -> str:
    for pattern in DRIVE_URL_PATTERNS:
        match = pattern.search(input_str)
        if match:
            return match.group(1)
    cleaned = input_str.strip()
    if FILE_ID_RE.match(cleaned):
        return cleaned
    raise DriveError(
        f"Cannot extract file ID from input: {input_str}. "
        "Provide a Google Drive URL or a raw file ID."
    )


def get_credentials() -> tuple[str, str]:
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        raise DriveError(
            "Missing Google OAuth credentials. Set GOOGLE_CLIENT_ID and "
            "GOOGLE_CLIENT_SECRET in the skill .env file."
        )
    return client_id, client_secret


def build_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build as build_api

    client_id, client_secret = get_credentials()
    token_path = SKILL_DIR / "token.json"

    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        LOGGER.info("Refreshing expired token...")
        creds.refresh(Request())
        token_path.write_text(creds.to_json())
    elif not creds or not creds.valid:
        LOGGER.info("No valid token found. Opening browser for OAuth consent...")
        client_config = {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        token_path.write_text(creds.to_json())
        LOGGER.info("Token saved to %s", token_path)

    return build_api("drive", "v3", credentials=creds)


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > 200:
        cleaned = cleaned[:200].rsplit(" ", 1)[0]
    return cleaned or "untitled"


def get_mime_type_name(mime_type: str) -> str:
    return MIME_TYPE_NAMES.get(
        mime_type, mime_type.split("/")[-1] if "/" in mime_type else mime_type
    )


def resolve_export(
    mime_type: str, format_override: str | None
) -> tuple[str | None, str]:
    if format_override:
        format_map = {
            "markdown": ("text/markdown", ".md"),
            "csv": ("text/csv", ".csv"),
            "txt": ("text/plain", ".txt"),
            "pdf": ("application/pdf", ".pdf"),
        }
        if format_override in format_map:
            return format_map[format_override]

    if mime_type in MIME_EXPORT_MAP:
        return MIME_EXPORT_MAP[mime_type]

    return None, ""


def read_file(args: argparse.Namespace) -> int:
    service = build_service()

    file_id = extract_file_id(args.file_id_or_url)
    LOGGER.info("Fetching file metadata: %s", file_id)

    try:
        file_meta = (
            service.files()
            .get(
                fileId=file_id,
                fields="id,name,mimeType,modifiedTime,size,webViewLink",
            )
            .execute()
        )
    except Exception as exc:
        raise DriveError(f"Failed to fetch file metadata: {exc}") from exc

    name = file_meta.get("name", "untitled")
    mime_type = file_meta.get("mimeType", "")
    modified = file_meta.get("modifiedTime", "")[:10]
    web_view_link = file_meta.get("webViewLink", "")

    LOGGER.info("File: %s (%s)", name, get_mime_type_name(mime_type))

    export_mime, ext = resolve_export(mime_type, args.format)

    output_dir = Path(".gdrive")
    output_dir.mkdir(exist_ok=True)

    if args.output:
        output_path = args.output
    else:
        safe_name = sanitize_filename(name)
        if not ext:
            base, existing_ext = os.path.splitext(name)
            ext = existing_ext or ".bin"
        output_path = output_dir / f"{safe_name}{ext}"

    if output_path.exists():
        stamp = __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S")
        stem = output_path.stem
        output_path = output_dir / f"{stem}-{stamp}{output_path.suffix}"

    if export_mime and mime_type.startswith("application/vnd.google-apps."):
        LOGGER.info("Exporting as %s...", export_mime)
        try:
            content = (
                service.files().export(fileId=file_id, mimeType=export_mime).execute()
            )
        except Exception as exc:
            raise DriveError(f"Export failed: {exc}") from exc

        if isinstance(content, bytes):
            output_path.write_bytes(content)
        else:
            text_content = (
                content.decode("utf-8") if isinstance(content, bytes) else str(content)
            )
            frontmatter = (
                "---\n"
                f"name: {name}\n"
                f"source: {web_view_link}\n"
                f"mime_type: {mime_type}\n"
                f"exported_as: {export_mime}\n"
                f"fetched_at: {__import__('datetime').datetime.now().isoformat()}\n"
                f"modified: {modified}\n"
                "---\n\n"
            )
            output_path.write_text(frontmatter + text_content, encoding="utf-8")
    else:
        LOGGER.info("Downloading raw file...")
        try:
            request = service.files().get_media(fileId=file_id)
            content = request.execute()
        except Exception as exc:
            raise DriveError(f"Download failed: {exc}") from exc

        output_path.write_bytes(
            content if isinstance(content, bytes) else content.encode("utf-8")
        )

    LOGGER.info("Saved to: %s", output_path)
    return 0


def list_files(args: argparse.Namespace) -> int:
    service = build_service()

    conditions = ["trashed = false"]

    if args.query:
        conditions.append(f"({args.query})")
    if args.folder:
        conditions.append(f"'{args.folder}' in parents")
    if args.mime_type:
        conditions.append(f"mimeType = '{args.mime_type}'")

    q = " and ".join(conditions)
    LOGGER.info("Query: %s", q)

    try:
        results = (
            service.files()
            .list(
                q=q,
                pageSize=args.max_results,
                fields="files(id,name,mimeType,modifiedTime)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )
    except Exception as exc:
        raise DriveError(f"Search failed: {exc}") from exc

    files = results.get("files", [])
    if not files:
        LOGGER.info("No files found.")
        return 0

    LOGGER.info("Found %d file(s):\n", len(files))
    for f in files:
        name = f.get("name", "?")
        mime = f.get("mimeType", "?")
        modified = f.get("modifiedTime", "")[:10]
        fid = f.get("id", "?")
        type_name = get_mime_type_name(mime)
        print(f"{name} | {type_name} | {modified} | {fid}")

    return 0


def run() -> int:
    args = parse_args()
    setup_logging(args.verbose)

    env_paths = [SKILL_DIR / ".env", Path(".env")]
    for env_path in env_paths:
        if env_path.exists():
            load_env_file(env_path)
            break

    try:
        if args.command == "read":
            return read_file(args)
        elif args.command == "list":
            return list_files(args)
        else:
            raise DriveError(f"Unknown command: {args.command}")
    except DriveError as exc:
        LOGGER.error(str(exc))
        return 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
