---
name: teams-playwright
description: Read Microsoft Teams web messages through the local Playwright CLI wrapper. Use when the user provides a Teams message URL or asks to fetch Teams message content. Use only for reading messages, not sending or modifying content.
license: MIT
compatibility: opencode
---

# Teams Playwright

Use the local `tools/teams-reader` CLI to read Microsoft Teams Web through an isolated Playwright browser profile.

This skill is read-only. Do not send messages, react, edit, delete, upload files, start calls, change settings, or modify Teams state.

## Safety Boundary

- Use only `tools/teams-reader/read-teams-message.js` through the explicit Node 22 command shown below.
- Do not use Playwright MCP for Teams reading.
- Do not use a personal Brave, Chrome, Chromium, or Edge browser profile.
- The CLI defaults to `/Users/joao/.config/opencode/tools/teams-reader/profile`, which is isolated from the user's browser profile.
- The CLI refuses common personal browser profile paths.
- Never expose authentication tokens, cookies, localStorage, IndexedDB, or request headers.
- Never use Teams private APIs or internal auth tokens.
- Do not save extracted message content to durable files unless the user explicitly asks.

## Commands

Show help:

```bash
/opt/homebrew/opt/node@22/bin/node /Users/joao/.config/opencode/tools/teams-reader/read-teams-message.js --help
```

Read a Teams message URL:

```bash
/opt/homebrew/opt/node@22/bin/node /Users/joao/.config/opencode/tools/teams-reader/read-teams-message.js --url "https://teams.microsoft.com/l/message/..." --around 3
```

Read only the permalink target message:

```bash
/opt/homebrew/opt/node@22/bin/node /Users/joao/.config/opencode/tools/teams-reader/read-teams-message.js --url "https://teams.microsoft.com/l/message/..." --message-only
```

Include raw DOM text only for debugging extraction:

```bash
/opt/homebrew/opt/node@22/bin/node /Users/joao/.config/opencode/tools/teams-reader/read-teams-message.js --url "https://teams.microsoft.com/l/message/..." --message-only --raw
```

Check whether the isolated profile is logged in:

```bash
/opt/homebrew/opt/node@22/bin/node /Users/joao/.config/opencode/tools/teams-reader/read-teams-message.js --status
```

First login in the isolated profile:

```bash
/opt/homebrew/opt/node@22/bin/node /Users/joao/.config/opencode/tools/teams-reader/read-teams-message.js --url "https://teams.microsoft.com/l/message/..." --around 3 --headed
```

## Expected Output

The CLI prints JSON to stdout:

```json
{
  "url": "https://teams.microsoft.com/l/message/...",
  "threadId": "...",
  "messageId": "...",
  "contextType": "chat",
  "messages": [
    {
      "index": 0,
      "sender": "...",
      "timestamp": "...",
      "text": "..."
    }
  ]
}
```

Return only the message content the user requested. Do not include unrelated visible messages unless the user asks for nearby context.

## Failure Handling

- If Teams is not authenticated, ask the user to run the same command with `--headed` and log in once.
- If extraction returns no messages, say that Teams opened but no visible message content was extracted.
- If the URL is invalid, ask for a Teams URL matching `https://teams.microsoft.com/l/message/<thread-id>/<message-id>`.
- If the command errors, report the JSON error message from stderr/stdout.
