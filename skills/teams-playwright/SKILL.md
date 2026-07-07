---
name: teams-playwright
description: Read Microsoft Teams web messages through Playwright MCP. Use when the user asks to open Teams, find a chat or channel, fetch latest messages, read message history, or inspect Teams web UI. Use only for reading messages, not sending or modifying content.
license: MIT
compatibility: opencode
---

# Teams Playwright

Use Playwright MCP to read Microsoft Teams Web through the authenticated browser UI.

This skill is for read-only Teams message access. Do not send messages, react, edit, delete, upload files, start calls, change settings, or modify Teams state.

## Preconditions

- The `playwright` MCP server must be connected.
- Teams must be opened in the Playwright-controlled browser profile.
- If Teams asks for login, pause and let the user complete authentication.
- Do not include real names, emails, group names, or message text in documentation, examples, logs, or reusable skill content.

## Basic Workflow

1. Navigate to Teams:

```text
browser_navigate({ "url": "https://teams.microsoft.com" })
```

2. Wait for Teams to load:

```text
browser_wait_for({ "time": 3 })
```

3. Capture a snapshot:

```text
browser_snapshot({ "depth": 5 })
```

4. If Teams shows a login screen, stop and ask the user to log in.

5. Locate the global search box or the visible chat tree.

6. Search for the requested chat or channel name using the global search box:

```text
browser_click({ "target": "<search-box-ref>" })
browser_type({ "target": "<search-box-ref>", "text": "<chat-or-channel-query>", "slowly": true })
browser_wait_for({ "time": 2 })
browser_snapshot({ "depth": 7 })
```

7. If the requested chat appears in the left chat tree, click it directly:

```text
browser_click({ "target": "<chat-treeitem-ref>" })
browser_wait_for({ "time": 3 })
```

8. Confirm the page title or header matches the requested chat or channel.

9. Capture a message-list snapshot:

```text
browser_snapshot({ "depth": 8 })
```

10. Read the latest visible message from the bottom of the message list.

## Robust Message Extraction

Teams sometimes truncates message text in the accessibility snapshot. If the snapshot does not contain the full message body, use `browser_evaluate` to inspect rendered message nodes.

Use this pattern to extract the last visible message without relying on private Teams APIs:

```text
browser_evaluate({
  "function": "() => {\n  const headings = Array.from(document.querySelectorAll('h4, [role=\"heading\"][aria-level=\"4\"], [aria-level=\"4\"]'));\n  const heading = headings[headings.length - 1];\n  if (!heading) return null;\n  let node = heading;\n  for (let depth = 0; depth < 3 && node?.parentElement; depth++) node = node.parentElement;\n  return { text: node?.innerText || '', aria: node?.getAttribute('aria-label') || '' };\n}"
})
```

If that returns too much text, inspect ancestors around the last heading and choose the smallest ancestor containing sender, timestamp, and message body:

```text
browser_evaluate({
  "function": "() => {\n  const headings = Array.from(document.querySelectorAll('h4, [role=\"heading\"][aria-level=\"4\"], [aria-level=\"4\"]'));\n  const heading = headings[headings.length - 1];\n  const out = [];\n  let node = heading;\n  for (let depth = 0; node && depth < 8; depth++, node = node.parentElement) {\n    out.push({\n      depth,\n      tag: node.tagName,\n      role: node.getAttribute('role'),\n      text: (node.innerText || node.textContent || '').slice(0, 3000),\n      textLength: (node.innerText || node.textContent || '').length\n    });\n  }\n  return out;\n}"
})
```

Prefer the smallest ancestor whose text contains:

- Sender display label
- Timestamp
- Full message body
- Link preview or attachment title, if present

## Reading More Than One Message

To fetch recent visible messages:

1. Use the message-list snapshot to identify the visible message headings.
2. Use `browser_evaluate` to collect heading elements and nearby message containers.
3. Return only the requested number of messages.
4. Preserve chronological order if the user asks for a history window.
5. For “latest message”, return only the bottom-most visible message.

Example extraction shape:

```text
browser_evaluate({
  "function": "() => {\n  const headings = Array.from(document.querySelectorAll('h4, [role=\"heading\"][aria-level=\"4\"], [aria-level=\"4\"]'));\n  return headings.slice(-5).map((heading) => {\n    let node = heading;\n    for (let depth = 0; depth < 3 && node?.parentElement; depth++) node = node.parentElement;\n    return (node?.innerText || '').trim();\n  }).filter(Boolean);\n}"
})
```

## Scrolling Older Messages

If the requested messages are not visible:

1. Click inside the message list.
2. Press `PageUp` or scroll upward with a Playwright code snippet only if needed.
3. Wait after each scroll.
4. Capture a new snapshot.
5. Stop once the requested message range is visible or when Teams stops loading older messages.

Use conservative scrolling. Avoid opening unrelated chats by accident.

## Safety Rules

- Never send or type into the message composer unless the user explicitly asks to send a message. This skill is read-only, so default response is to refuse sending.
- Never click buttons for calls, reactions, attachments, forwarding, sharing, deleting, editing, or settings.
- Never expose authentication tokens, cookies, localStorage, IndexedDB, or request headers.
- Never use Teams private APIs or internal auth tokens.
- Do not save extracted message content to durable files unless the user explicitly asks.
- If `browser_evaluate` writes output to a file, delete or avoid retaining files containing message content unless the user requests persistence.
- Keep responses minimal: chat name, sender, timestamp, and requested message text.
- Do not include unrelated visible messages.

## Failure Handling

- If Teams is not authenticated, ask the user to log in.
- If the chat is not found, say the chat was not visible or not found and ask for a more exact name.
- If the latest message is truncated, use DOM extraction before answering.
- If multiple chats match, ask the user to choose.
- If a UI action would modify Teams state, stop and ask for confirmation or refuse if outside read-only scope.
