from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.parse
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger("jira")

ISSUE_KEY_RE = __import__("re").compile(r"^[A-Z][A-Z0-9_]+-\d+$")


class JiraError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Jira CLI - fetch, create, and search issues"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser(
        "fetch", help="Fetch issue and save as markdown"
    )
    fetch_parser.add_argument("issue_key", help="Jira issue key (e.g., PROJ-123)")
    fetch_parser.add_argument("--output", type=Path, help="Output file path")

    create_parser = subparsers.add_parser(
        "create", help="Create a new issue (interactive or via JSON)"
    )
    create_parser.add_argument("--config", type=Path, help="JSON config file")
    create_parser.add_argument("--project-key", help="Project key (overrides config)")
    create_parser.add_argument("--summary", help="Issue summary")
    create_parser.add_argument("--description", help="Issue description")
    create_parser.add_argument(
        "--issue-type", default="Story", help="Issue type (default: Story)"
    )
    create_parser.add_argument("--story-points", type=int, help="Story points")
    create_parser.add_argument("--labels", help="Comma-separated labels")
    create_parser.add_argument(
        "--assignee", help="Assignee accountId, 'self', or 'none'"
    )
    create_parser.add_argument(
        "--story-points-field",
        default="customfield_10016",
        help="Story points field ID",
    )
    create_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be created"
    )
    create_parser.add_argument(
        "--yes", action="store_true", help="Skip confirmation prompt"
    )

    search_parser = subparsers.add_parser("search", help="Search issues via JQL")
    search_parser.add_argument("jql", help="JQL query")
    search_parser.add_argument(
        "--max-results", type=int, default=50, help="Max results (default: 50)"
    )
    search_parser.add_argument(
        "--fields", help="Comma-separated field names to include"
    )

    parser.add_argument(
        "--env-file", type=Path, default=Path(".env"), help=".env file path"
    )
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


def get_credentials(args: argparse.Namespace) -> tuple[str, str, str]:
    base_url = (args.env_file.parent / ".env").read_text().split() if False else None
    base_url = os.environ.get("JIRA_BASE_URL", "").strip().strip('"')
    email = os.environ.get("JIRA_EMAIL", "").strip()
    api_key = os.environ.get("JIRA_API_KEY", "").strip()
    if not base_url or not email or not api_key:
        raise JiraError(
            "Missing Jira credentials. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_KEY in .env"
        )
    return base_url, email, api_key


def adf_to_markdown(adf: dict[str, Any]) -> str:
    def apply_marks(text: str, marks: list[dict[str, Any]]) -> str:
        for mark in marks or []:
            mark_type = mark.get("type", "")
            if mark_type == "strong":
                text = f"**{text}**"
            elif mark_type == "em":
                text = f"*{text}*"
            elif mark_type == "strike":
                text = f"~~{text}~~"
            elif mark_type == "code":
                text = f"`{text}`"
            elif mark_type == "underline":
                text = f"<u>{text}</u>"
            elif mark_type == "link":
                href = mark.get("attrs", {}).get("href", "")
                text = f"[{text}]({href})"
        return text

    def render_inline(node: dict[str, Any]) -> str:
        node_type = node.get("type", "")
        if node_type == "text":
            return apply_marks(node.get("text", ""), node.get("marks"))
        elif node_type == "hardBreak":
            return "\n"
        elif node_type == "emoji":
            return node.get("attrs", {}).get("shortName", "")
        elif node_type == "mention":
            attrs = node.get("attrs", {})
            text = attrs.get("text") or f"@{attrs.get('userName', 'unknown')}"
            return text
        elif node_type == "inlineCard":
            url = node.get("attrs", {}).get("url", "link")
            return f"[{url}]({url})"
        elif node_type == "date":
            return node.get("attrs", {}).get("timestamp", "")
        elif node_type == "status":
            text = node.get("attrs", {}).get("text", "")
            return f"`{text}`"
        return ""

    def render_content(content: list[dict[str, Any]] | None) -> str:
        return "".join(render_inline(n) for n in (content or []))

    def render_block(node: dict[str, Any]) -> str:
        node_type = node.get("type", "")

        if node_type == "paragraph":
            return render_content(node.get("content"))

        elif node_type == "heading":
            level = node.get("attrs", {}).get("level", 1)
            return f"{'#' * level} {render_content(node.get('content'))}"

        elif node_type == "bulletList":
            items = []
            for item in node.get("content", []):
                item_content = render_block(item)
                items.append(f"- {item_content}")
            return "\n".join(items)

        elif node_type == "orderedList":
            items = []
            for idx, item in enumerate(node.get("content", []), start=1):
                item_content = render_block(item)
                items.append(f"{idx}. {item_content}")
            return "\n".join(items)

        elif node_type == "listItem":
            return render_content(node.get("content"))

        elif node_type == "codeBlock":
            lang = node.get("attrs", {}).get("language", "")
            return f"```{lang}\n{render_content(node.get('content'))}\n```"

        elif node_type == "blockquote":
            lines = []
            for block in node.get("content", []):
                block_text = render_block(block)
                lines.append(f"> {block_text}")
            return "\n".join(lines)

        elif node_type == "rule":
            return "---"

        elif node_type == "table":
            rows = node.get("content", [])
            if not rows:
                return ""

            all_rows = [row.get("content", []) for row in rows]
            col_count = max(len(row) for row in all_rows) if all_rows else 0

            def cell_text(cell: dict[str, Any]) -> str:
                return render_content(cell.get("content"))

            table_data = [[cell_text(c) for c in row] for row in all_rows]
            widths = [
                max(len(table_data[r][c]) for r in range(len(table_data)))
                if col_count > 0
                else 0
                for c in range(col_count)
            ]

            formatted = []
            for row in table_data:
                cells = [
                    f"{table_data[formatted.index(row)][c] if formatted.index(row) < len(formatted) else ''}"
                    for c in range(col_count)
                ]
                formatted_row = (
                    "| "
                    + " | ".join(
                        row[c] + " " * (widths[c] - len(row[c])) if c < len(row) else ""
                        for c in range(col_count)
                    )
                    + " |"
                )
                formatted.append(formatted_row)

            result = []
            for i, row in enumerate(table_data):
                cells = " | ".join(
                    row[c] + " " * (widths[c] - len(row[c])) if c < len(row) else ""
                    for c in range(col_count)
                )
                result.append(f"| {cells} |")
                if i == 0:
                    sep = " | ".join("-" * widths[c] for c in range(col_count))
                    result.append(f"| {sep} |")
            return "\n".join(result)

        elif node_type in ("tableHeader", "tableCell"):
            return render_content(node.get("content"))

        elif node_type == "panel":
            panel_type = node.get("attrs", {}).get("panelType", "Info")
            content = "\n".join(render_block(b) for b in node.get("content", []))
            return f"> **{panel_type} Panel**\n> {content.replace(chr(10), chr(10) + '> ')}"

        elif node_type == "nestedExpand":
            title = node.get("attrs", {}).get("title", "Expand")
            content = "\n\n".join(render_block(b) for b in node.get("content", []))
            return f"<details>\n<summary>**{title}**</summary>\n\n{content}\n</details>"

        return ""

    if adf.get("type") == "doc":
        blocks = [render_block(b) for b in adf.get("content", [])]
        return "\n\n".join(b for b in blocks if b)
    return ""


class JiraClient:
    def __init__(self, base_url: str, email: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_key = api_key

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        import subprocess

        url = f"{self.base_url}{path}"
        cmd = [
            "curl",
            "-sS",
            "-u",
            f"{self.email}:{self.api_key}",
            "-H",
            "Accept: application/json",
            "-H",
            "Content-Type: application/json",
            "-X",
            method,
            url,
            "-w",
            "\n%{http_code}",
        ]
        if payload:
            cmd.extend(["--data", json.dumps(payload, ensure_ascii=True)])

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise JiraError(f"curl failed: {result.stderr.strip()}")

        if "\n" not in result.stdout:
            raise JiraError("Unexpected Jira response format")

        body, status_text = result.stdout.rsplit("\n", 1)
        status_code = int(status_text.strip() or "0")
        if status_code >= 400:
            try:
                error_data = json.loads(body)
                messages = error_data.get("errorMessages", [])
                errors = error_data.get("errors", {})
                detail = messages or [f"{k}: {v}" for k, v in errors.items()]
                raise JiraError(f"Jira API {status_code}: {detail}")
            except json.JSONDecodeError:
                raise JiraError(f"Jira API {status_code}: {body[:500]}")

        if not body.strip():
            return {}

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise JiraError(f"Non-JSON response: {body[:500]}") from exc

    def myself(self) -> dict[str, Any]:
        return self._request("GET", "/rest/api/3/myself")

    def get_issue(self, issue_key: str, fields: str = "") -> dict[str, Any]:
        query = ""
        if fields:
            query = f"?fields={fields}"
        return self._request("GET", f"/rest/api/3/issue/{issue_key}{query}")

    def get_comments(self, issue_key: str) -> list[dict[str, Any]]:
        data = self._request("GET", f"/rest/api/3/issue/{issue_key}/comment")
        return data.get("comments", [])

    def create_issue(self, fields: dict[str, Any]) -> str:
        data = self._request("POST", "/rest/api/3/issue", {"fields": fields})
        return data["key"]

    def jql(self, jql: str, max_results: int = 50, fields: str = "") -> dict[str, Any]:
        params = urllib.parse.urlencode(
            {
                "jql": jql,
                "maxResults": max_results,
            }
        )
        if fields:
            params += f"&fields={fields}"
        return self._request("GET", f"/rest/api/3/search/jql?{params}")


def fetch_issue(args: argparse.Namespace) -> int:
    client = JiraClient(*get_credentials(args))

    issue_key = args.issue_key.upper()
    if not ISSUE_KEY_RE.match(issue_key):
        raise JiraError(f"Invalid issue key format: {issue_key}")

    LOGGER.info("Fetching %s...", issue_key)

    issue_data = client.get_issue(
        issue_key,
        "summary,description,status,assignee,created,updated,priority,labels,components,issuetype",
    )
    fields = issue_data.get("fields", {})

    comments = client.get_comments(issue_key)

    summary = fields.get("summary", "No summary")
    status = fields.get("status", {}).get("name", "Unknown")
    assignee = fields.get("assignee", {}).get("displayName", "Unassigned")
    created = fields.get("created", "Unknown")[:10]
    updated = fields.get("updated", "Unknown")[:10]
    priority = fields.get("priority", {}).get("name", "None")
    issue_type = fields.get("issuetype", {}).get("name", "Unknown")
    labels = ", ".join(fields.get("labels", [])) or "None"
    components = (
        ", ".join(c.get("name", "") for c in fields.get("components", [])) or "None"
    )

    description_adf = fields.get("description")
    description_md = (
        adf_to_markdown(description_adf)
        if description_adf
        else "_No description provided_"
    )

    output = []
    output.append(f"# {issue_key}: {summary}\n")
    output.append("| Field | Value |")
    output.append("|-------|-------|")
    output.append(f"| **Type** | {issue_type} |")
    output.append(f"| **Status** | {status} |")
    output.append(f"| **Priority** | {priority} |")
    output.append(f"| **Assignee** | {assignee} |")
    output.append(f"| **Created** | {created} |")
    output.append(f"| **Updated** | {updated} |")
    output.append(f"| **Labels** | {labels} |")
    output.append(f"| **Components** | {components} |")
    output.append("\n---\n\n## Description\n\n" + description_md)

    if comments:
        output.append("\n\n---\n\n## Comments\n\n")
        for comment in comments:
            author = comment.get("author", {}).get("displayName", "Unknown")
            created_date = comment.get("created", "")[:10]
            body_adf = comment.get("body")
            body_md = adf_to_markdown(body_adf) if body_adf else ""
            output.append(f"### {author} - {created_date}\n\n{body_md}\n\n---\n\n")

    output_file = args.output or Path(f"{issue_key.lower()}.md")
    output_file.write_text("".join(output))
    LOGGER.info("Saved to %s", output_file)
    return 0


def create_issue_interactive(args: argparse.Namespace) -> int:
    client = JiraClient(*get_credentials(args))

    config_data: dict[str, Any] = {}
    if args.config and args.config.exists():
        config_data = json.loads(args.config.read_text())

    project_key = args.project_key or config_data.get("project_key")
    if not project_key:
        raise JiraError("project_key is required (--project-key or config)")

    summary = args.summary
    if not summary:
        raise JiraError("--summary is required")

    description_text = args.description or ""
    issue_type = args.issue_type or config_data.get("default_issue_type", "Story")

    assignee_option = (
        args.assignee if args.assignee else config_data.get("assignee", "self")
    )
    if assignee_option == "self":
        account_id = client.myself().get("accountId")
    elif assignee_option == "none":
        account_id = None
    else:
        account_id = assignee_option

    story_points_field = config_data.get(
        "story_points_field", args.story_points_field or "customfield_10016"
    )

    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "issuetype": {"name": issue_type},
        "summary": summary,
    }

    if description_text:
        fields["description"] = {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description_text}],
                }
            ],
        }

    if account_id:
        fields["assignee"] = {"accountId": account_id}

    if args.story_points is not None:
        fields[story_points_field] = args.story_points

    if args.labels:
        fields["labels"] = [l.strip() for l in args.labels.split(",") if l.strip()]

    fields.update(config_data.get("fields", {}))

    LOGGER.info("Issue to be created:")
    LOGGER.info("  Project: %s", project_key)
    LOGGER.info("  Type: %s", issue_type)
    LOGGER.info("  Summary: %s", summary)
    LOGGER.info("  Assignee: %s", account_id or "unassigned")
    LOGGER.info("  Story Points: %s", fields.get(story_points_field, "none"))
    LOGGER.info("  Labels: %s", fields.get("labels", "none"))

    if args.dry_run:
        LOGGER.info("[dry-run] Issue would be created (not actually created)")
        return 0

    if not args.yes:
        confirm = input("\nCreate this issue? [y/N] ")
        if confirm.lower() != "y":
            LOGGER.info("Aborted.")
            return 0

    issue_key = client.create_issue(fields)
    LOGGER.info("Created: %s", issue_key)
    return 0


def search_issues(args: argparse.Namespace) -> int:
    client = JiraClient(*get_credentials(args))

    LOGGER.info("Searching: %s", args.jql)
    data = client.jql(args.jql, max_results=args.max_results, fields=args.fields or "")

    issues = data.get("issues", [])
    LOGGER.info("Found %d issues", len(issues))

    for issue in issues:
        key = issue.get("key", "?")
        summary = issue.get("fields", {}).get("summary", "?")
        print(f"{key}: {summary}")

    return 0


def run() -> int:
    args = parse_args()
    setup_logging(args.verbose)

    env_file = args.env_file
    if env_file.exists():
        load_env_file(env_file)
    else:
        alt_env = (
            Path.home() / ".config" / "opencode" / "skills" / "jira-issues" / ".env"
        )
        if alt_env.exists():
            load_env_file(alt_env)

    try:
        if args.command == "fetch":
            return fetch_issue(args)
        elif args.command == "create":
            return create_issue_interactive(args)
        elif args.command == "search":
            return search_issues(args)
        else:
            raise JiraError(f"Unknown command: {args.command}")
    except JiraError as exc:
        LOGGER.error(str(exc))
        return 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
