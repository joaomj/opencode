#!/usr/bin/env python3
from __future__ import annotations
import argparse
import base64
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, TypedDict
class JiraError(RuntimeError):
    pass
@dataclass(frozen=True)
class JiraConfig:
    base_url: str
    email: str
    api_key: str
    project_key: str = ""
class ADFDocument(TypedDict):
    type: str
    version: int
    content: list[dict[str, Any]]


REQUIRED_ENV_KEYS: tuple[str, ...] = (
    "JIRA_BASE_URL",
    "JIRA_EMAIL",
    "JIRA_API_KEY",
)

ENV_ALIASES: dict[str, tuple[str, ...]] = {
    "JIRA_BASE_URL": ("JIRA_URL",),
    "JIRA_EMAIL": ("JIRA_USER_EMAIL", "ATLASSIAN_EMAIL"),
    "JIRA_API_KEY": ("JIRA_API_TOKEN", "JIRA_TOKEN", "ATLASSIAN_API_TOKEN"),
}


def _strip_wrapped_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def _parse_dotenv(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        result[key] = _strip_wrapped_quotes(value.strip())
    return result


def load_required_env_fallbacks() -> None:
    for target_key, aliases in ENV_ALIASES.items():
        if os.environ.get(target_key):
            continue
        for alias in aliases:
            alias_value = os.environ.get(alias)
            if alias_value:
                os.environ[target_key] = alias_value
                break

    missing_keys = [key for key in REQUIRED_ENV_KEYS if not os.environ.get(key)]
    if not missing_keys:
        return

    candidates: list[Path] = []
    explicit_env_file = os.environ.get("JIRA_ENV_FILE")
    if explicit_env_file:
        candidates.append(Path(explicit_env_file).expanduser())

    cwd = Path.cwd()
    candidates.extend([cwd / ".env", cwd.parent / ".env"])

    loaded: dict[str, str] = {}
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            loaded = _parse_dotenv(candidate)
            break
        except OSError:
            continue

    if not loaded:
        return

    for key in REQUIRED_ENV_KEYS:
        if os.environ.get(key):
            continue
        if key in loaded and loaded[key]:
            os.environ[key] = loaded[key]
            continue
        for alias in ENV_ALIASES.get(key, ()):  # pragma: no branch - tiny alias set
            value = loaded.get(alias)
            if value:
                os.environ[key] = value
                break

def load_config(args: argparse.Namespace) -> JiraConfig:
    load_required_env_fallbacks()
    email: str = args.jira_email or os.environ.get("JIRA_EMAIL", "")
    api_key: str = os.environ.get("JIRA_API_KEY", "")
    if not email:
        raise JiraError(
            "Missing JIRA_EMAIL. Ask the user for their Jira email and retry with --jira-email."
        )
    if not api_key:
        raise JiraError("Missing JIRA_API_KEY in environment. Do not ask the user to share secret keys in chat.")
    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    if not base_url:
        raise JiraError("Missing JIRA_BASE_URL in environment. Set it to your Jira instance URL.")
    return JiraConfig(
        base_url=base_url,
        email=email,
        api_key=api_key,
    )

def parse_issue_key(project_key: str, raw_key: str) -> str:
    key: str = raw_key.strip().upper()
    if not re.match(r"^[A-Z]+-\d+$", key):
        raise JiraError(f"Issue key must match PROJECTKEY-<number> (got: {raw_key})")
    if project_key and not key.startswith(f"{project_key}-"):
        raise JiraError(f"Issue key must be in project {project_key} (got: {key})")
    return key

def auth_header(config: JiraConfig) -> str:
    token: str = base64.b64encode(f"{config.email}:{config.api_key}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"

def api_error(body: str) -> str:
    text: str = body.strip()
    if not text:
        return "No response body"
    try:
        payload: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError:
        return text
    error_messages: Any = payload.get("errorMessages")
    if isinstance(error_messages, list) and error_messages:
        return "; ".join(str(item) for item in error_messages)
    errors: Any = payload.get("errors")
    if isinstance(errors, dict) and errors:
        return "; ".join(f"{k}: {v}" for k, v in errors.items())
    message: Any = payload.get("message")
    return message if isinstance(message, str) and message else text


def jira_request(config: JiraConfig, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    url: str = f"{config.base_url}{path}"
    headers: dict[str, str] = {"Accept": "application/json", "Authorization": auth_header(config)}
    data: bytes | None = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request: urllib.request.Request = urllib.request.Request(url=url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text: str = response.read().decode("utf-8")
            return {} if not text.strip() else json.loads(text)
    except urllib.error.HTTPError as exc:
        body: str = exc.read().decode("utf-8", errors="replace")
        raise JiraError(f"Jira API error {exc.code} on {method} {path}: {api_error(body)}") from exc
    except urllib.error.URLError as exc:
        raise JiraError(f"Could not reach Jira API: {exc.reason}") from exc


def current_account_id(config: JiraConfig) -> str:
    profile: Any = jira_request(config, "GET", "/rest/api/3/myself")
    account_id: Any = profile.get("accountId") if isinstance(profile, dict) else None
    if not isinstance(account_id, str) or not account_id:
        raise JiraError("Could not determine current Jira user accountId")
    return account_id


def issue_by_key(config: JiraConfig, issue_key: str) -> dict[str, Any]:
    issue: Any = jira_request(config, "GET", f"/rest/api/3/issue/{issue_key}")
    if not isinstance(issue, dict):
        raise JiraError("Unexpected Jira issue response")
    return issue


def ensure_assigned_issue(issue: dict[str, Any], project_key: str, account_id: str) -> None:
    fields: Any = issue.get("fields")
    if not isinstance(fields, dict):
        raise JiraError("Unexpected Jira payload: missing fields")
    if project_key:
        project: Any = fields.get("project")
        issue_project_key: Any = project.get("key") if isinstance(project, dict) else None
        if not isinstance(issue_project_key, str) or issue_project_key.upper() != project_key:
            raise JiraError(f"Issue is outside allowed project {project_key}")
    assignee: Any = fields.get("assignee")
    assignee_id: Any = assignee.get("accountId") if isinstance(assignee, dict) else None
    if assignee_id != account_id:
        raise JiraError("Issue is not assigned to the authenticated user")


def adf_from_text(text: str) -> ADFDocument:
    cleaned: str = text.strip()
    if not cleaned:
        raise JiraError("Description text cannot be empty")
    blocks: list[str] = [part.strip() for part in cleaned.split("\n\n") if part.strip()]
    content: list[dict[str, Any]] = []
    for block in blocks:
        content.append({"type": "paragraph", "content": [{"type": "text", "text": block}]})
    return {"type": "doc", "version": 1, "content": content}


def adf_to_text(raw: Any) -> str:
    if not isinstance(raw, dict):
        return ""

    def inline_text(children: Any) -> str:
        if not isinstance(children, list):
            return ""
        parts: list[str] = []
        for child in children:
            if not isinstance(child, dict):
                continue
            child_type = child.get("type")
            if child_type == "text":
                parts.append(str(child.get("text", "")))
            elif child_type == "hardBreak":
                parts.append("\n")
            elif isinstance(child.get("content"), list):
                nested = inline_text(child.get("content"))
                if nested:
                    parts.append(nested)
        return "".join(parts).strip()

    lines: list[str] = []

    def walk(node: Any) -> None:
        if not isinstance(node, dict):
            return
        node_type = node.get("type")
        content = node.get("content")

        if node_type in {"paragraph", "heading"}:
            text = inline_text(content)
            if text:
                lines.append(text)
            return

        if node_type in {"bulletList", "orderedList"} and isinstance(content, list):
            for item in content:
                item_text_parts: list[str] = []
                item_content = item.get("content") if isinstance(item, dict) else None
                if isinstance(item_content, list):
                    for part in item_content:
                        if isinstance(part, dict) and part.get("type") in {"paragraph", "heading"}:
                            text = inline_text(part.get("content"))
                            if text:
                                item_text_parts.append(text)
                        else:
                            before = len(lines)
                            walk(part)
                            appended = lines[before:]
                            if appended:
                                item_text_parts.extend(appended)
                                del lines[before:]
                item_text = " ".join(part.strip() for part in item_text_parts if part.strip())
                if item_text:
                    lines.append(f"- {item_text}")
            return

        if isinstance(content, list):
            for child in content:
                walk(child)

    walk(raw)
    return "\n\n".join(lines)


def build_jql(project_key: str, extra_jql: str | None, include_done: bool) -> str:
    clauses: list[str] = ["assignee = currentUser()"]
    if project_key:
        clauses.insert(0, f'project = "{project_key}"')
    if not include_done:
        clauses.append("resolution = Unresolved")
    if extra_jql:
        clauses.append(f"({extra_jql})")
    return " AND ".join(clauses) + " ORDER BY updated DESC"


def cmd_search(args: argparse.Namespace, config: JiraConfig) -> int:
    payload: dict[str, Any] = {
        "jql": build_jql(config.project_key, args.jql, args.include_done),
        "maxResults": args.limit,
        "fields": ["summary", "status", "assignee", "updated", "project"],
    }
    result: Any = jira_request(config, "POST", "/rest/api/3/search/jql", payload)
    issues: Any = result.get("issues", []) if isinstance(result, dict) else []
    if not isinstance(issues, list):
        raise JiraError("Unexpected Jira search payload")
    compact: list[dict[str, Any]] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        fields: Any = issue.get("fields") if isinstance(issue.get("fields"), dict) else {}
        status: Any = fields.get("status")
        assignee: Any = fields.get("assignee")
        compact.append(
            {
                "key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": status.get("name") if isinstance(status, dict) else None,
                "assignee": assignee.get("displayName") if isinstance(assignee, dict) else None,
                "updated": fields.get("updated"),
            }
        )
    print(json.dumps({"count": len(compact), "issues": compact}, indent=2))
    return 0


def cmd_get(args: argparse.Namespace, config: JiraConfig) -> int:
    issue_key: str = parse_issue_key(config.project_key, args.issue_key)
    account_id: str = current_account_id(config)
    issue: dict[str, Any] = issue_by_key(config, issue_key)
    ensure_assigned_issue(issue, config.project_key, account_id)
    fields: Any = issue.get("fields") if isinstance(issue.get("fields"), dict) else {}
    status: Any = fields.get("status")
    assignee: Any = fields.get("assignee")
    output: dict[str, Any] = {
        "key": issue.get("key"),
        "summary": fields.get("summary"),
        "status": status.get("name") if isinstance(status, dict) else None,
        "assignee": assignee.get("displayName") if isinstance(assignee, dict) else None,
        "updated": fields.get("updated"),
        "description": adf_to_text(fields.get("description")),
    }
    print(json.dumps(output, indent=2))
    return 0


def cmd_transition(args: argparse.Namespace, config: JiraConfig) -> int:
    issue_key: str = parse_issue_key(config.project_key, args.issue_key)
    account_id: str = current_account_id(config)
    issue: dict[str, Any] = issue_by_key(config, issue_key)
    ensure_assigned_issue(issue, config.project_key, account_id)
    response: Any = jira_request(config, "GET", f"/rest/api/3/issue/{issue_key}/transitions")
    transitions: Any = response.get("transitions", []) if isinstance(response, dict) else []
    if not isinstance(transitions, list):
        raise JiraError("Unexpected Jira transitions payload")
    requested: str = args.transition.strip()
    selected: dict[str, Any] | None = None
    for item in transitions:
        if not isinstance(item, dict):
            continue
        item_id: Any = item.get("id")
        item_name: Any = item.get("name")
        if isinstance(item_id, str) and requested == item_id:
            selected = item
            break
        if isinstance(item_name, str) and requested.casefold() == item_name.casefold():
            selected = item
            break
    if selected is None:
        names: list[str] = []
        for item in transitions:
            if not isinstance(item, dict):
                continue
            value: Any = item.get("name")
            if isinstance(value, str):
                names.append(value)
        raise JiraError(f"Transition '{requested}' not available. Available: {', '.join(names) or 'none'}")
    transition_id: Any = selected.get("id")
    if not isinstance(transition_id, str):
        raise JiraError("Unexpected transition payload: missing id")
    jira_request(config, "POST", f"/rest/api/3/issue/{issue_key}/transitions", {"transition": {"id": transition_id}})
    print(json.dumps({"key": issue_key, "transition": selected.get("name"), "result": "updated"}, indent=2))
    return 0


def cmd_update_description(args: argparse.Namespace, config: JiraConfig) -> int:
    issue_key: str = parse_issue_key(config.project_key, args.issue_key)
    account_id: str = current_account_id(config)
    issue: dict[str, Any] = issue_by_key(config, issue_key)
    ensure_assigned_issue(issue, config.project_key, account_id)
    text: str = sys.stdin.read() if args.text == "-" else args.text
    jira_request(config, "PUT", f"/rest/api/3/issue/{issue_key}", {"fields": {"description": adf_from_text(text)}})
    print(json.dumps({"key": issue_key, "field": "description", "result": "updated"}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Search and update your assigned Jira issues")
    parser.add_argument(
        "--jira-email",
        default=None,
        help="Jira account email fallback when JIRA_EMAIL is missing",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    search = subparsers.add_parser("search", help="Search assigned issues")
    search.add_argument("--jql", default=None, help="Extra JQL filter appended with AND")
    search.add_argument("--limit", type=int, default=20, help="Maximum issues to return")
    search.add_argument("--include-done", action="store_true", help="Include resolved issues")
    search.set_defaults(handler=cmd_search)
    get_cmd = subparsers.add_parser("get", help="Read one assigned issue")
    get_cmd.add_argument("issue_key", help="Issue key, for example TDT-123")
    get_cmd.set_defaults(handler=cmd_get)
    transition = subparsers.add_parser("transition", help="Transition one assigned issue")
    transition.add_argument("issue_key", help="Issue key, for example TDT-123")
    transition.add_argument("transition", help="Transition name or id")
    transition.set_defaults(handler=cmd_transition)
    update = subparsers.add_parser("update-description", help="Replace description")
    update.add_argument("issue_key", help="Issue key, for example TDT-123")
    update.add_argument("--text", required=True, help="New description text, or '-' from stdin")
    update.set_defaults(handler=cmd_update_description)
    return parser


def main() -> int:
    args: argparse.Namespace = build_parser().parse_args()
    try:
        return int(args.handler(args, load_config(args)))
    except JiraError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
