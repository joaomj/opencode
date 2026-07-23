---
name: teams-brave-cli
description: Read and send Microsoft Teams messages through either local Brave profile cookies or a dedicated headless Brave CDP daemon. Use when the user asks to read, list, send, or reply to Teams messages on macOS or Linux.
license: MIT
compatibility: opencode, macOS, Linux
---

# Teams CLI

Read and send Microsoft Teams messages through the Teams chatsvc API. The CLI
uses the installed Brave profile on graphical hosts and can use a dedicated
headless browser daemon on headless hosts. It never uses environment tokens,
synced token files, MSAL, host scripts, or remote MCP servers.

## Safety Boundary

- Never send or reply without explicit user confirmation of the exact destination and text.
- `send` and `reply` require the CLI `--confirm` flag after that approval.
- Never expose or log cookies, tokens, authorization headers, or token-derived data.
- Prefer reads by default.
- The daemon profile is dedicated to this skill. Never point it at an interactive Brave profile.

## Providers

### `auto` (default)

Selects `profile` when a graphical session is available. On a headless host, it
checks for an existing daemon and asks for confirmation before starting one.
It never starts a headless browser automatically.

```bash
uv run teams-cli auth
```

### `profile`

Reads Teams cookies from the existing local Brave profile and keeps decrypted values
in memory only for the CLI process. This is best for normal interactive host use.

```bash
uv run teams-cli --auth-provider profile auth
```

Use a non-default Brave profile when needed:

```bash
uv run teams-cli --profile "Profile 1" auth
uv run teams-cli --profile "$HOME/path/to/Brave/Profile 1" list
```

### `daemon`

Retrieves Teams credentials through a local Unix socket from `teams-authd`. The
daemon owns a dedicated, headless Brave profile and keeps Teams open so ordinary
web-session cookie rotation can occur without daily browser interaction. If it
is not already running, the CLI asks before starting it. It never starts in a
graphical session.

```bash
uv run teams-cli --auth-provider daemon auth
```

## Requirements

- macOS or Linux.
- Python 3.11 or newer and `uv`.
- For `profile`: Brave Browser with an active Teams login.
- For `profile` on macOS: access to `Brave Safe Storage` in Keychain.
- For `profile` on Linux: an unlocked Secret Service keyring.
- For `daemon`: Brave, Chromium, or Google Chrome on a headless host. macOS
  defaults to Brave when installed.

## Setup

From the skill directory:

```bash
cd "$HOME/.config/opencode/skills/teams-brave-cli"
uv sync --locked
```

The default Brave profile locations are:

```text
macOS: ~/Library/Application Support/BraveSoftware/Brave-Browser/Default
Linux: ~/.config/BraveSoftware/Brave-Browser/Default
Linux fallback: ~/.config/brave-browser/Default
```

## Daemon Startup

The skill does not install a launchd agent or systemd service. This prevents a
headless browser from starting at login. Use the default provider and answer
the prompt when a headless daemon is needed:

```bash
uv run teams-cli auth
```

Use `--auth-provider profile` to require the installed Brave profile, or
`--auth-provider daemon` to require the dedicated daemon. Both modes refuse to
start a headless browser in a graphical session.

For diagnostics:

```bash
uv run teams-authd-status
```

The daemon owns only these private paths:

```text
~/.config/teams-cli/teams-authd-profile
~/.config/teams-cli/run/teams-authd.sock
```

Set `TEAMS_CDP_BROWSER` only when the default browser path is unsuitable:

```bash
export TEAMS_CDP_BROWSER="/path/to/browser"
```

Set `TEAMS_CDP_HEADLESS=1` to force headless detection when running a headless
macOS session. Set `TEAMS_CDP_GUI=1` to force graphical detection for testing.

The profile location is configurable via `TEAMS_CDP_PROFILE`:

```text
~/.config/teams-cli/teams-authd-profile  (default)
~/.config/teams-cli/run/teams-authd.sock (fixed)
```

### Migration From Persistent Services

If an earlier version installed a persistent service, remove it once:

macOS:

```bash
launchctl bootout "gui/$(id -u)/com.opencode.teams-authd" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.opencode.teams-authd.plist"
```

Linux:

```bash
systemctl --user disable --now teams-authd.service 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/teams-authd.service"
rm -rf "$HOME/.config/systemd/user/teams-authd.service.d"
systemctl --user daemon-reload
```

## Reading Messages

```bash
uv run teams-cli list -n 20
uv run teams-cli read "<conversation-id-or-teams-url>" -n 20
uv run teams-cli read --raw "<conversation-id-or-teams-url>" -n 20
```

Pass `--auth-provider daemon` before the command when requiring the daemon.

## Sending and Replying

Only after explicit user confirmation:

```bash
uv run teams-cli send "<conversation-id>" "<message text>" --confirm
uv run teams-cli reply "<conversation-id>" "<message-id>" "<reply text>" --confirm
```

## Initial Login And Reauthentication (Last Resort)

Use this once to initialize the daemon profile. After that, do not use it for
daily access. Repeat it only when `teams-cli --auth-provider daemon auth` fails
because Microsoft expired the session, requires MFA, or applies Conditional Access.

1. Stop the daemon if it is running.

2. Open its dedicated profile in a graphical Brave browser and complete Teams
sign-in or MFA:

```bash
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" --user-data-dir="$HOME/.config/teams-cli/teams-authd-profile" --password-store=basic https://teams.microsoft.com/v2
```

3. Close that Brave window, run the CLI on the headless host, approve daemon
startup, and verify:

```bash
uv run teams-cli --auth-provider daemon auth
```

## Failure Handling

- **Profile database missing**: verify the Brave profile path and `--profile` value.
- **Keychain or keyring failure**: unlock the local keyring, then retry `profile` mode.
- **Daemon unavailable**: run the CLI again and approve the headless daemon prompt.
- **Daemon authentication unavailable**: use the last-resort reauthentication flow above.
- **Browser executable missing**: install Brave, Chromium, or Chrome, or set `TEAMS_CDP_BROWSER`.
- **Conversation returns 404**: the ID may be stale or an unsupported channel conversation.
- **No messages**: the conversation may be empty or inaccessible.

## Limitations

- The Teams chatsvc API is undocumented and may change.
- Channel and team messages are not implemented.
- Meeting reply chains are not supported.
- Microsoft identity policies can still require interactive reauthentication.
