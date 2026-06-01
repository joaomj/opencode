---
name: browser-readonly
description: Read-only browser inspection and debugging for frontend tasks. Use for screenshots, DOM extraction, JavaScript evaluation, console log capture, and network tracing via the local Brave or Chromium browser. No installation of Node, Puppeteer, or Playwright required. Loads when the user mentions browser, frontend, web page, screenshot, DOM, console logs, or network debugging.
license: MIT
compatibility: opencode
---

# Browser Read-Only (CDP)

Read-only browser operations via the **Chrome DevTools Protocol (CDP)** using the locally installed **Brave Browser** (macOS / Linux) or **Chromium** fallback.

## Setup (one-time)

Create a virtual environment inside the skill directory and install the single dependency:

```bash
cd ~/.config/opencode/skills/browser-readonly
python3 -m venv .venv
source .venv/bin/activate
pip install websockets
```

No other dependencies. No Node. No npm. No Playwright.

## Prerequisites

- **macOS**: Brave Browser installed at `/Applications/Brave Browser.app/Contents/MacOS/Brave Browser`
- **Linux**: `brave-browser`, `brave`, `chromium`, `chromium-browser`, or `google-chrome-stable` available in `$PATH`

## How it works

1. The script checks if a browser is already listening on `localhost:9222` (CDP remote debugging port).
2. If not, it launches Brave/Chromium in headless mode with `--remote-debugging-port=9222`.
3. It connects via WebSocket to the browser's CDP endpoint.
4. It sends CDP commands, collects results, prints JSON to stdout, and optionally saves files (screenshots).
5. **The browser stays running** between commands so you can chain operations (navigate → screenshot → eval). Use `browser_cdp.py stop` when finished.

## Commands

All commands output JSON to stdout.

### Activate venv before running

```bash
source ~/.config/opencode/skelines/browser-readonly/.venv/bin/activate
python ~/.config/opencode/skills/browser-readonly/browser_cdp.py <command> [args]
```

Or use the full Python path directly:

```bash
~/.config/opencode/skills/browser-readonly/.venv/bin/python \
  ~/.config/opencode/skills/browser-readonly/browser_cdp.py <command> [args]
```

### 1. Navigate

```bash
browser_cdp.py navigate https://example.com
```

### 2. Screenshot

```bash
browser_cdp.py screenshot                    # viewport screenshot
browser_cdp.py screenshot --full-page        # full page screenshot
browser_cdp.py screenshot -o ./shot.png      # custom output path
```

### 3. Evaluate JavaScript

```bash
browser_cdp.py eval "document.title"
browser_cdp.py eval "document.querySelector('h1').innerText"
```

### 4. Console Logs

```bash
browser_cdp.py console                       # collect current page logs
browser_cdp.py console --url https://example.com   # navigate then collect
```

### 5. Network Trace

```bash
browser_cdp.py network                       # trace current page
browser_cdp.py network --url https://example.com   # navigate then trace
```

### 6. DOM Inspection

```bash
browser_cdp.py dom                           # root document info
browser_cdp.py dom --selector "h1"           # find first <h1>
```

### 7. Stop Browser

```bash
browser_cdp.py stop                          # terminate headless browser
```

## Workflow Patterns

### Inspect a page quickly

1. Navigate: `browser_cdp.py navigate <url>`
2. Screenshot: `browser_cdp.py screenshot -o debug.png`
3. Eval: `browser_cdp.py eval "document.title"`

### Debug frontend errors

1. Navigate: `browser_cdp.py navigate <url>`
2. Console: `browser_cdp.py console --url <url>`
3. Network: `browser_cdp.py network --url <url>`

### Extract DOM content

1. Navigate: `browser_cdp.py navigate <url>`
2. DOM: `browser_cdp.py dom --selector "article"`
3. Eval: `browser_cdp.py eval "document.body.innerText"`

## Output Format

All commands emit a single JSON object to stdout:

```json
{"ok": true, "file": "screenshot-1234567890.png", "size": 48291}
{"ok": true, "result": "Example Domain"}
{"ok": true, "logs": [{"type": "log", "text": "hello"}]}
{"ok": true, "requests": [{"url": "https://example.com/favicon.ico", "method": "GET", "type": "Other"}]}
{"ok": true, "node": {"nodeName": "H1", "nodeValue": "Example Domain"}}
```

On error:

```json
{"error": "No browser found. Install Brave or Chromium."}
```

## Limitations

- **Read-only**: No click, fill, hover, or form submission. Use for inspection only.
- **No performance tracing**: No Lighthouse, no performance timeline, no heap snapshots. Extend the script if needed.
- **No accessibility tree snapshot**: DOM and screenshot only.
- **Console/Network are best-effort**: Logs and requests collected during a short sleep window (~1-3s). Increase sleep in script if pages are slow.
- **Single page per invocation**: Each command connects to one page target.

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| "No browser found" | Install Brave or Chromium. On Linux: `apt install brave-browser` or `snap install brave`. |
| "Browser did not start on port 9222" | Check if another process is using port 9222 (`lsof -i :9222`). Kill it or change `DEBUG_PORT` in script. |
| "ModuleNotFoundError: websockets" | Run the setup steps above to create `.venv` and install `websockets`. |
| Empty console/network results | Page may load slowly. Increase `await asyncio.sleep(N)` in `browser_cdp.py` for that command. |
| Screenshot is blank | Page may not have finished rendering. Navigate first, then screenshot in separate command. |
| Browser stays running after commands | By design — reuse the same session. Run `browser_cdp.py stop` when finished. |

## Extending

The script is a single file with no hidden dependencies. To add a new CDP command:

1. Add an `async def cmd_<name>(...)` function.
2. Add an argparse subparser in `main()`.
3. Route in the `run()` coroutine.

CDP reference: https://chromedevtools.github.io/devtools-protocol/
