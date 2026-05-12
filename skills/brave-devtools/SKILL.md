---
name: brave-devtools
description: Control and inspect Brave Browser using Chrome DevTools Protocol for debugging web applications, analyzing network requests, monitoring console output, and inspecting DOM.
license: MIT
compatibility: universal
metadata:
  category: browser-debugging
  languages: [python, javascript]
  requires: python3.10+
---

# Brave DevTools CLI

A universal, zero-dependency toolkit for controlling Brave Browser via Chrome DevTools Protocol (CDP).

## Prerequisites

- Brave Browser must be installed
- Start Brave with remote debugging:
  ```bash
  # macOS
  open -a "Brave Browser" --args --remote-debugging-port=9222

  # Linux
  brave-browser --remote-debugging-port=9222

  # Windows
  "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port=9222
  ```
- Verify with `brave-connect`

## Available Tools

| Script | Purpose | Key Arguments |
|--------|---------|---------------|
| `brave-connect` | Test connectivity & list tabs | `--port 9222` |
| `brave-navigate` | Navigate to URL | `<url>` `--wait load\|domcontentloaded\|networkidle` |
| `brave-evaluate` | Execute JavaScript | `<expression>` `--return-by-value` |
| `brave-screenshot` | Capture screenshot | `--output file.png` `--full-page` `--selector '#id'` |
| `brave-console` | Inspect console logs | `--get` `--clear` `--monitor N` `--level error` |
| `brave-network` | Inspect network requests | `--enable` `--get` `--filter fetch\|xhr` |
| `brave-dom` | Inspect DOM tree | `--query '<selector>'` `--tree` `--depth 2` |

## Console Debugging Workflow

1. **Reproduce the issue** — navigate to the page
   ```bash
   brave-navigate https://example.com
   ```
2. **Clear old logs** — `brave-console --clear`
3. **Trigger the bug** — interact with page or `brave-evaluate` to trigger JS
4. **Capture logs** — `brave-console --get --level error`
5. **Inspect stack traces** — look for `stackTrace` in error entries
6. **Evaluate fixes** — `brave-evaluate "window.myFix()"`
7. **Verify** — `brave-console --get` to confirm no new errors

## Network Debugging Workflow

1. **Enable recording** — `brave-network --enable`
2. **Navigate or trigger request** — `brave-navigate <url>` or interact with page
3. **Capture requests** — `brave-network --get --since 10`
4. **Analyze failures** — filter by `--status` or look for `status: 0` (CORS/network failure)
5. **Inspect headers** — check `requestHeaders` and `responseHeaders`
6. **Check timing** — review `timing` object for slow phases (DNS, connect, TTFB)
7. **Reproduce with curl** — construct equivalent curl from captured request

## DOM Inspection Workflow

1. Navigate to page: `brave-navigate <url>`
2. Find element: `brave-dom --query '<selector>'`
3. Extract data: `brave-evaluate "document.querySelector('...').textContent"`
4. Capture visual state: `brave-screenshot --selector '...'`

## Common Multi-Step Patterns

### "Page is blank after login"
```bash
brave-navigate https://app.example.com/login
brave-evaluate "document.querySelector('#username').value = 'user'"
brave-evaluate "document.querySelector('#password').value = 'pass'"
brave-evaluate "document.querySelector('form').submit()"
sleep 3
brave-console --get --level error
brave-screenshot
```

### "API call returns 500"
```bash
brave-navigate https://example.com
brave-network --enable
brave-evaluate "fetch('/api/data').then(r => r.json())"
brave-network --get --filter fetch --status 500
```

### "CSS layout broken"
```bash
brave-navigate https://example.com
brave-dom --query '.broken-class' --outer-html
brave-screenshot --selector '.broken-class'
```

## Error Handling

Every script returns structured JSON:
- **Success:** Valid JSON to stdout
- **Error:** `{"error": "...", "hint": "..."}` to stdout, exit code > 0
- **Logs:** Plain text to stderr

Exit codes:
- `0` — Success
- `1` — Connection error / Brave not running
- `2` — No page targets found