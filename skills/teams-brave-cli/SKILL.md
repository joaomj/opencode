---
name: teams-brave-cli
description: Read and send Microsoft Teams messages through either local Brave profile cookies or a dedicated headless Brave CDP daemon. Use when the user asks to read, list, send, or reply to Teams messages on macOS or Linux.
license: MIT
compatibility: opencode, macOS, Linux
---

# Teams CLI

Read and send Microsoft Teams messages through the Teams chatsvc API. The CLI has
two explicit local authentication providers. It never uses environment tokens,
synced token files, MSAL, host scripts, or remote MCP servers.

## Safety Boundary

- Never send or reply without explicit user confirmation of the exact destination and text.
- `send` and `reply` require the CLI `--confirm` flag after that approval.
- Never expose or log cookies, tokens, authorization headers, or token-derived data.
- Prefer reads by default.
- The daemon profile is dedicated to this skill. Never point it at an interactive Brave profile.

## Providers

### `profile` (default)

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
web-session cookie rotation can occur without daily browser interaction.

```bash
uv run teams-cli --auth-provider daemon auth
```

## Requirements

- macOS or Linux.
- Python 3.11 or newer and `uv`.
- For `profile`: Brave Browser with an active Teams login.
- For `profile` on macOS: access to `Brave Safe Storage` in Keychain.
- For `profile` on Linux: an unlocked Secret Service keyring.
- For `daemon`: Brave, Chromium, or Google Chrome. macOS defaults to Brave when installed.

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

## Daemon Setup (macOS)

Install the launchd agent after `uv sync --locked`:

```bash
install -D -m 600 launchd/com.opencode.teams-authd.plist "$HOME/Library/LaunchAgents/com.opencode.teams-authd.plist"
launchctl bootout "gui/$(id -u)"/com.opencode.teams-authd 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.opencode.teams-authd.plist"
```

Verify its health and Teams API access:

```bash
uv run teams-authd-status
uv run teams-cli --auth-provider daemon auth
```

The daemon owns only these private paths:

```text
~/.config/teams-cli/teams-authd-profile
~/.config/teams-cli/run/teams-authd.sock
```

Set `TEAMS_CDP_BROWSER` only when the default browser path is unsuitable. For a
launchd-managed daemon, set it before bootstrapping the agent:

```bash
launchctl setenv TEAMS_CDP_BROWSER "/path/to/browser"
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.opencode.teams-authd.plist"
```

## Daemon Setup (Linux)

Install the systemd user service after `uv sync --locked`:

```bash
install -D -m 600 systemd/user/teams-authd.service "$HOME/.config/systemd/user/teams-authd.service"
install -D -m 600 systemd/user/teams-authd.service.d/snap.conf "$HOME/.config/systemd/user/teams-authd.service.d/snap.conf"
systemctl --user daemon-reload
systemctl --user enable --now teams-authd.service
```

Verify its health and Teams API access:

```bash
uv run teams-authd-status
uv run teams-cli --auth-provider daemon auth
```

The service file includes `TEAMS_CDP_BROWSER` and `TEAMS_CDP_PROFILE` environment
variables configured for Snap Chromium. Override them when your setup differs:

```bash
mkdir -p "$HOME/.config/systemd/user/teams-authd.service.d"
cat > "$HOME/.config/systemd/user/teams-authd.service.d/env.conf" << 'EOF'
[Service]
Environment=TEAMS_CDP_BROWSER=/usr/bin/google-chrome
Environment=TEAMS_CDP_PROFILE=%h/.config/teams-cli/teams-authd-profile
EOF
systemctl --user daemon-reload
systemctl --user restart teams-authd
```

The daemon owns only these private paths (configurable via `TEAMS_CDP_PROFILE`):

```text
~/.config/teams-cli/teams-authd-profile  (default)
~/.config/teams-cli/run/teams-authd.sock (fixed)
```

## Reading Messages

```bash
uv run teams-cli list -n 20
uv run teams-cli read "<conversation-id-or-teams-url>" -n 20
uv run teams-cli read --raw "<conversation-id-or-teams-url>" -n 20
```

Pass `--auth-provider daemon` before the command when using the daemon.

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

### macOS

1. Stop the daemon:

```bash
launchctl bootout "gui/$(id -u)"/com.opencode.teams-authd
```

2. Open its dedicated profile in the normal graphical Brave browser and complete
Teams sign-in or MFA:

```bash
"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser" --user-data-dir="$HOME/.config/teams-cli/teams-authd-profile" --password-store=basic https://teams.microsoft.com/v2
```

3. Close that Brave window, restart the agent, and verify:

```bash
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.opencode.teams-authd.plist"
uv run teams-cli --auth-provider daemon auth
```

### Linux

1. Stop the daemon:

```bash
systemctl --user stop teams-authd
```

2. Open the profile directory in a graphical browser and complete Teams sign-in
or MFA. Adjust the browser command and profile path to match your setup:

```bash
chromium --user-data-dir="$HOME/snap/chromium/common/teams-authd-profile" --password-store=basic https://teams.microsoft.com/v2
```

3. Close that browser window, restart the daemon, and verify:

```bash
systemctl --user start teams-authd
uv run teams-cli --auth-provider daemon auth
```

## Failure Handling

- **Profile database missing**: verify the Brave profile path and `--profile` value.
- **Keychain or keyring failure**: unlock the local keyring, then retry `profile` mode.
- **Daemon unavailable**: verify `teams-authd-status`, then bootstrap the launchd agent.
- **Daemon authentication unavailable**: use the last-resort reauthentication flow above.
- **Browser executable missing**: install Brave, Chromium, or Chrome, or set `TEAMS_CDP_BROWSER`.
- **Conversation returns 404**: the ID may be stale or an unsupported channel conversation.
- **No messages**: the conversation may be empty or inaccessible.

## Limitations

- The Teams chatsvc API is undocumented and may change.
- Channel and team messages are not implemented.
- Meeting reply chains are not supported.
- Microsoft identity policies can still require interactive reauthentication.
