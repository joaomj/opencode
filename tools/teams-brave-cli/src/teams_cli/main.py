from __future__ import annotations

import json
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from .cookie_extractor import extract_auth
from .api_client import TeamsClient

app = typer.Typer(no_args_is_help=True)
console = Console()
state = {"auth": None, "client": None}


def get_client() -> TeamsClient:
    if state["client"] is None:
        auth = extract_auth()
        if auth is None:
            console.print(
                "[red]Could not extract auth tokens from Brave.[/red]\n"
                "[dim]Make sure you are logged into Teams in Brave browser.[/dim]"
            )
            raise typer.Exit(1)
        state["auth"] = auth
        state["client"] = TeamsClient(auth.skypetoken, auth.authtoken, auth.tenant_id)
    return state["client"]


@app.command()
def auth():
    """Test authentication by extracting tokens and verifying with Teams."""
    try:
        auth = extract_auth()
        if auth is None:
            console.print("[red]No Teams auth cookies found in Brave.[/red]")
            console.print("[dim]Log into teams.microsoft.com in Brave first.[/dim]")
            raise typer.Exit(1)
        console.print(f"[green]Extracted tokens[/green]")
        console.print(f"  Tenant: {auth.tenant_id}")

        client = TeamsClient(auth.skypetoken, auth.authtoken, auth.tenant_id)
        if client.test_auth():
            console.print(f"  Region: [green]{client.region}[/green]")
            console.print(f"  Status: [green]authenticated[/green]")
        else:
            console.print("  Status: [red]auth failed - tokens may be expired[/red]")
        client.close()
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)


@app.command()
def list(
    limit: Annotated[int, typer.Option("-n", "--limit", help="Max conversations")] = 20,
):
    """List recent Teams conversations."""
    client = get_client()
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

    for i, c in enumerate(conversations, 1):
        topic = c.topic or ""
        if c.chat_type == "oneOnOne" and not topic:
            topic = c.last_message_from or ""
        table.add_row(
            str(i),
            topic[:30],
            c.last_message_preview[:50],
            c.last_message_from[:15],
            c.id[:30],
        )

    console.print(table)
    console.print("\n[dim]Use the conv id with 'read', or paste a Teams message URL.[/dim]")


@app.command()
def read(
    conversation_id: Annotated[str, typer.Argument(help="Conversation ID or Teams message URL")],
    limit: Annotated[int, typer.Option("-n", "--limit", help="Max messages")] = 20,
    raw: Annotated[bool, typer.Option("--raw", help="Output raw JSON")] = False,
):
    """Read messages from a conversation."""
    conv_id = _parse_input_id(conversation_id)

    client = get_client()
    with console.status("[dim]Fetching messages...[/dim]"):
        messages = client.get_messages(conv_id, limit=limit)

    if not messages:
        console.print("[dim]No messages found.[/dim]")
        return

    if raw:
        console.print_json(json.dumps([m.raw for m in messages]))
        return

    for m in messages:
        time_str = m.timestamp[:19].replace("T", " ") if m.timestamp else ""
        sender_style = "bold cyan"
        console.print(
            f"[dim]{time_str}[/dim]  [{sender_style}]{m.sender}[/{sender_style}]"
        )
        if m.is_deleted:
            console.print("  [dim italic](deleted)[/dim italic]")
        else:
            console.print(f"  {m.content}")
        console.print(f"  [dim]id: {m.id}[/dim]")
        console.print()


@app.command()
def send(
    conversation_id: Annotated[str, typer.Argument(help="Conversation ID")],
    content: Annotated[str, typer.Argument(help="Message text")],
    display_name: Annotated[str, typer.Option("--as", help="Display name override")] = "",
):
    """Send a message to a conversation."""
    conv_id = _parse_input_id(conversation_id)
    client = get_client()
    try:
        with console.status("[dim]Sending...[/dim]"):
            result = client.send_message(conv_id, content, display_name=display_name)
        console.print("[green]Message sent.[/green]")
    except Exception as e:
        console.print(f"[red]Send failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def reply(
    conversation_id: Annotated[str, typer.Argument(help="Conversation ID")],
    message_id: Annotated[str, typer.Argument(help="Message ID to reply to")],
    content: Annotated[str, typer.Argument(help="Reply text")],
):
    """Reply to a specific message in a conversation."""
    conv_id = _parse_input_id(conversation_id)
    client = get_client()
    try:
        with console.status("[dim]Sending reply...[/dim]"):
            result = client.send_message(conv_id, content, reply_to=message_id)
        console.print("[green]Reply sent.[/green]")
    except Exception as e:
        console.print(f"[red]Reply failed: {e}[/red]")
        raise typer.Exit(1)


def _parse_input_id(input_str: str) -> str:
    """Parse a Teams URL into a conversation ID, or return as-is."""
    marker = "/l/message/"
    if marker in input_str:
        rest = input_str.split(marker, 1)[1]
        query_start = rest.find("?")
        path = rest[:query_start] if query_start != -1 else rest
        parts = path.split("/")
        return parts[0] if parts else input_str
    marker = "/l/chat/"
    if marker in input_str:
        rest = input_str.split(marker, 1)[1]
        query_start = rest.find("?")
        path = rest[:query_start] if query_start != -1 else rest
        parts = path.split("/")
        return parts[0] if parts else input_str
    return input_str


def main():
    app()


if __name__ == "__main__":
    main()
