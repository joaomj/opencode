from __future__ import annotations

import json
from typing import Annotated, TypedDict

import httpx
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from teams_cli.api_client import TeamsClient
from teams_cli.auth import AuthUnavailable, TeamsAuth
from teams_cli.cookie_extractor import extract_auth
from teams_cli.daemon_client import request_daemon_auth
from teams_cli.logging_utils import configure_logging, get_logger

app = typer.Typer(no_args_is_help=True)
console = Console()
logger = get_logger(__name__)


class CliState(TypedDict):
    auth_provider: str
    profile: str | None
    client: TeamsClient | None


state: CliState = {"auth_provider": "profile", "profile": None, "client": None}


@app.callback()
def cli_options(
    auth_provider: Annotated[
        str,
        typer.Option(
            "--auth-provider",
            help="Authentication provider: profile or dedicated CDP daemon.",
        ),
    ] = "profile",
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            help="Brave profile directory or profile name, for example 'Profile 1'.",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Write debug details to the persistent log."),
    ] = False,
) -> None:
    """Read and send Teams messages using a local Teams authentication provider."""
    if auth_provider not in {"profile", "daemon"}:
        raise typer.BadParameter("must be 'profile' or 'daemon'", param_hint="--auth-provider")
    state["auth_provider"] = auth_provider
    state["profile"] = profile
    configure_logging(verbose=verbose)


def get_client() -> TeamsClient:
    client = state["client"]
    if client is not None:
        return client

    try:
        auth = _get_auth()
    except AuthUnavailable as error:
        logger.error(
            "Teams authentication unavailable provider=%s: %s", state["auth_provider"], error
        )
        console.print(f"[red]{error}[/red]")
        _print_auth_recovery()
        raise typer.Exit(1) from error
    client = TeamsClient(auth.skypetoken, auth.authtoken, auth.tenant_id)
    state["client"] = client
    return client


@app.command()
def auth() -> None:
    """Verify the selected authentication provider and Teams connection."""
    client: TeamsClient | None = None
    try:
        auth_data = _get_auth()
        client = TeamsClient(auth_data.skypetoken, auth_data.authtoken, auth_data.tenant_id)
        probe = client.probe_auth()
        logger.info("Brave authentication probe completed status=%d", probe.status_code)
        console.print(f"  Region: {client.region}")
        console.print(f"  HTTP status: {probe.status_code}")
        if probe.status_code == 200:
            console.print("  Status: [green]authenticated[/green]")
        else:
            console.print("  Status: [red]authentication failed[/red]")
            raise typer.Exit(1)
    except typer.Exit:
        raise
    except (AuthUnavailable, httpx.HTTPError) as error:
        logger.exception("Teams authentication check failed provider=%s", state["auth_provider"])
        console.print(f"[red]{error}[/red]")
        _print_auth_recovery()
        raise typer.Exit(1) from error
    finally:
        if client is not None:
            client.close()


@app.command(name="list")
def list_conversations(
    limit: Annotated[int, typer.Option("-n", "--limit", help="Max conversations")] = 20,
) -> None:
    """List recent Teams conversations."""
    client = get_client()
    logger.info("Listing Teams conversations limit=%d", limit)
    with console.status("[dim]Fetching conversations...[/dim]"):
        conversations = client.list_conversations(limit=limit)

    if not conversations:
        console.print("[dim]No conversations found.[/dim]")
        return

    table = Table(box=box.SIMPLE)
    table.add_column("#", style="dim", width=4)
    table.add_column("Topic", width=30)
    table.add_column("Last Message", width=50)
    table.add_column("From", width=15)
    table.add_column("Conv ID", style="dim", width=30)

    for index, conversation in enumerate(conversations, 1):
        topic = conversation.topic or ""
        if conversation.chat_type == "oneOnOne" and not topic:
            topic = conversation.last_message_from or ""
        table.add_row(
            str(index),
            topic[:30],
            conversation.last_message_preview[:50],
            conversation.last_message_from[:15],
            conversation.id[:30],
        )

    console.print(table)
    console.print("\n[dim]Use the conversation ID with 'read', or paste a Teams message URL.[/dim]")


@app.command()
def read(
    conversation_id: Annotated[str, typer.Argument(help="Conversation ID or Teams message URL")],
    limit: Annotated[int, typer.Option("-n", "--limit", help="Max messages")] = 20,
    raw: Annotated[bool, typer.Option("--raw", help="Output raw JSON")] = False,
) -> None:
    """Read messages from a conversation."""
    conv_id = _parse_input_id(conversation_id)
    logger.info("Reading Teams messages limit=%d raw=%s", limit, raw)
    client = get_client()
    with console.status("[dim]Fetching messages...[/dim]"):
        messages = client.get_messages(conv_id, limit=limit)

    if not messages:
        console.print("[dim]No messages found.[/dim]")
        return

    if raw:
        console.print_json(json.dumps([message.raw for message in messages]))
        return

    for message in messages:
        time_str = message.timestamp[:19].replace("T", " ") if message.timestamp else ""
        console.print(f"[dim]{time_str}[/dim]  [bold cyan]{message.sender}[/bold cyan]")
        if message.is_deleted:
            console.print("  [dim italic](deleted)[/dim italic]")
        else:
            console.print(f"  {message.content}")
        console.print(f"  [dim]id: {message.id}[/dim]")
        console.print()


@app.command()
def send(
    conversation_id: Annotated[str, typer.Argument(help="Conversation ID")],
    content: Annotated[str, typer.Argument(help="Message text")],
    display_name: Annotated[str, typer.Option("--as", help="Display name override")] = "",
    confirm: Annotated[
        bool, typer.Option("--confirm", help="Confirm this exact write after user approval.")
    ] = False,
) -> None:
    """Send a message to a conversation."""
    _require_confirmation(confirm)
    conv_id = _parse_input_id(conversation_id)
    logger.info("Sending Teams message")
    client = get_client()
    try:
        with console.status("[dim]Sending...[/dim]"):
            client.send_message(conv_id, content, display_name=display_name)
        logger.info("Teams message sent successfully")
        console.print("[green]Message sent.[/green]")
    except httpx.HTTPError as error:
        logger.exception("Teams message send failed")
        console.print(f"[red]Send failed: {error}[/red]")
        raise typer.Exit(1) from error


@app.command()
def reply(
    conversation_id: Annotated[str, typer.Argument(help="Conversation ID")],
    message_id: Annotated[str, typer.Argument(help="Message ID to reply to")],
    content: Annotated[str, typer.Argument(help="Reply text")],
    confirm: Annotated[
        bool, typer.Option("--confirm", help="Confirm this exact write after user approval.")
    ] = False,
) -> None:
    """Reply to a specific message in a conversation."""
    _require_confirmation(confirm)
    conv_id = _parse_input_id(conversation_id)
    logger.info("Sending Teams reply")
    client = get_client()
    try:
        with console.status("[dim]Sending reply...[/dim]"):
            client.send_message(conv_id, content, reply_to=message_id)
        logger.info("Teams reply sent successfully")
        console.print("[green]Reply sent.[/green]")
    except httpx.HTTPError as error:
        logger.exception("Teams reply failed")
        console.print(f"[red]Reply failed: {error}[/red]")
        raise typer.Exit(1) from error


def _parse_input_id(input_str: str) -> str:
    """Parse a Teams URL into a conversation ID, or return as-is."""
    for marker in ("/l/message/", "/l/chat/"):
        if marker in input_str:
            rest = input_str.split(marker, 1)[1]
            query_start = rest.find("?")
            path = rest[:query_start] if query_start != -1 else rest
            parts = path.split("/")
            return parts[0] if parts else input_str
    return input_str


def _get_auth() -> TeamsAuth:
    if state["auth_provider"] == "daemon":
        auth = request_daemon_auth()
        logger.info("Daemon authentication retrieved successfully")
        return auth
    try:
        auth = extract_auth(profile=state["profile"])
    except (FileNotFoundError, RuntimeError) as error:
        raise AuthUnavailable(str(error)) from error
    if auth is None:
        raise AuthUnavailable("Required Teams cookies were not found in the local Brave profile.")
    logger.info("Brave profile authentication extracted successfully")
    return auth


def _print_auth_recovery() -> None:
    if state["auth_provider"] == "daemon":
        console.print(
            "[dim]Start teams-authd or use its documented browser recovery flow, then retry.[/dim]"
        )
        return
    console.print("[dim]Log into teams.microsoft.com in Brave, then retry.[/dim]")


def _require_confirmation(confirm: bool) -> None:
    if confirm:
        return
    console.print("[red]Write blocked. Re-run with --confirm after explicit user approval.[/red]")
    raise typer.Exit(2)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
