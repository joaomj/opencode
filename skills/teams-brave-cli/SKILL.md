---
name: teams-brave-cli
description: Read and send Microsoft Teams messages via the teams-cli Python CLI, which extracts session tokens from Brave's on-disk cookie database. Use when the user provides a Teams URL or needs to read/send Teams messages.
license: MIT
compatibility: opencode
---

# teams-brave-cli

Use the local `tools/teams-brave-cli` Python CLI to read and send Microsoft Teams messages through the undocumented chatsvc API, using session tokens extracted from Brave's browser profile.

## Safety Boundary

- **NEVER send or reply to any message without explicit user confirmation.** Confirmation requires the user to say something like "yes, send it" or "go ahead" -- not just providing a message text to use.
- Never expose authentication tokens (skypetoken, authtoken) in output.
- Tokens are ephemeral; do not cache them to disk.
- Prefer reading to writing by default.

## Commands

Run from `tools/teams-brave-cli/`:

```bash
uv run teams-cli auth
uv run teams-cli list
uv run teams-cli read "<conversation-id>"
uv run teams-cli send "<conversation-id>" "<message text>"
uv run teams-cli reply "<conv-id>" "<message-id>" "<reply text>"
```

## Initial Setup

```bash
cd tools/teams-brave-cli
uv sync
```

Then verify auth:

```bash
uv run teams-cli auth
```

If auth fails, the user must be logged into teams.microsoft.com in Brave.

## Expected Output

`auth` prints tenant ID, region, and status. `list` prints a table of conversations with IDs. `read` prints messages with timestamps, sender, and content. `send`/`reply` print a confirmation.

## Failure Handling

- If auth fails, tell the user to check they are logged into teams.microsoft.com in Brave.
- If a conversation returns 404, it might be a channel (requires `@thread.tacv2`+CSA API) or the ID is stale.
- If read returns no messages, the conversation may be empty or inaccessible.

## Limitations

- Channel/team messages (CSA API) not yet implemented.
- Brave browser only; macOS only.
- Reply chains not supported in meeting threads.
