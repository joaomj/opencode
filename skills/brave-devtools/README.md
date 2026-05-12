# Brave DevTools CLI

A zero-dependency toolkit for controlling Brave Browser via Chrome DevTools Protocol (CDP). No npm, no pip — just Python 3.10+.

## Quick Start

### 1. Start Brave with Remote Debugging

```bash
# macOS
open -a "Brave Browser" --args --remote-debugging-port=9222

# Linux
brave-browser --remote-debugging-port=9222

# Windows
"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222
```

### 2. Verify Connection

```bash
python3 skills/brave-devtools/brave-connect
```

### 3. Use a Tool

```bash
python3 skills/brave-devtools/brave-navigate https://example.com
python3 skills/brave-devtools/brave-evaluate "document.title"
python3 skills/brave-devtools/brave-screenshot --output screenshot.png
python3 skills/brave-devtools/brave-console --get --level error
python3 skills/brave-devtools/brave-network --get --limit 50
python3 skills/brave-devtools/brave-dom --query 'h1' --outer-html
```

## Tools

| Tool | Description |
|------|-------------|
| `brave-connect` | Discover Brave CDP endpoint & list targets |
| `brave-navigate` | Navigate to URL |
| `brave-evaluate` | Execute JavaScript in page context |
| `brave-screenshot` | Capture viewport or full-page screenshot |
| `brave-console` | Get, clear, or monitor console messages |
| `brave-network` | Enable and retrieve network request log |
| `brave-dom` | DOM snapshot (outerHTML or tree) |

## Testing

```bash
# Unit tests (no browser required)
python3 skills/brave-devtools/tests/test_cdp_ws.py

# Integration tests (requires Brave running)
python3 skills/brave-devtools/tests/test_tools.py
```

## Architecture

Python stdlib only: `urllib.request` for discovery, `socket`/`ssl` for WebSocket, `struct` for frame encoding, `json` for CDP messages.
