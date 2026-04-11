---
name: notion-reader
description: Search and fetch Notion content using the notion-cli. Designed for non-admin users who need read access to workspace docs, databases, and pages shared with their integration.
compatibility: opencode
---

# Notion Reader

Search and read Notion workspace content from the terminal. Uses `notion-cli` (single Go binary) for all API interactions. Read-focused: search, fetch, query, and list -- not CRUD.

## Triggers

| User says | Command invoked |
|-----------|-----------------|
| "search notion" / "find in notion" / "notion search" | `notion search "<query>"` |
| "read notion page" / "fetch notion page" / "get notion doc" | `notion page view <id\|url>` |
| "list notion pages" / "what's in notion" | `notion search ""` |
| "query notion database" / "notion db query" | `notion db query <id> [filters]` |
| "notion page properties" / "notion page props" | `notion page props <id>` |
| "read notion comments" | `notion comment list <page-id>` |

## Setup

### 1. Install notion-cli

```bash
brew install 4ier/tap/notion-cli
```

Alternatives:
- Go: `go install github.com/4ier/notion-cli@latest`
- npm: `npm install -g @4ier/notion-cli`
- Binary: download from https://github.com/4ier/notion-cli/releases

### 2. Create a Notion Integration (non-admin)

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it (e.g., "opencode-reader")
4. Select the workspace
5. Capabilities: enable **Read content**, **Read comments** (disable write capabilities)
6. Copy the token (`ntn_xxx...`)

### 3. Authenticate

```bash
echo "ntn_your_token_here" | notion auth login --with-token
```

Or use the environment variable:
```bash
export NOTION_TOKEN=ntn_your_token_here
```

### 4. Share pages with the integration (CRITICAL for non-admins)

The integration can ONLY access pages explicitly shared with it. For each page/database:

1. Open the page in Notion
2. Click the `...` menu (top right)
3. Scroll to **Add connections**
4. Search for and select your integration name

Sub-pages inherit access -- share a top-level page to grant access to all its children.

---

## Workflow

### Search for pages/databases

```bash
notion search "meeting notes"
notion search "Q1 roadmap" --type page
notion search "" --type database
```

Output shows title, type (page/database), and ID.

### Read a full page as Markdown

```bash
notion page view <page-id-or-url>
```

For deeply nested content with sub-blocks:

```bash
notion block list <page-id-or-url> --md --depth 3
```

The `--depth` flag controls recursion depth (default: 1, max: recommended 5 for large pages).

### Query a database

```bash
# List all rows
notion db query <database-id>

# With filters (human-friendly syntax)
notion db query <database-id> -F 'Status=Done' -s 'Date:desc'

# Only specific columns
notion db query <database-id> -F 'Priority=High' -F 'Status!=Done'

# Complex filters (JSON escape hatch)
notion db query <database-id> --filter-json '{"or":[{"property":"Status","status":{"equals":"Done"}}]}'

# Fetch all pages (auto-paginates)
notion db query <database-id> --all
```

### View database schema

```bash
notion db view <database-id>
```

### Read page properties

```bash
notion page props <page-id-or-url>
```

### Get specific property

```bash
notion page props <page-id-or-url> <property-id>
```

### Read comments on a page

```bash
notion comment list <page-id-or-url>
```

### Extract page content to a file

```bash
notion block list <page-id-or-url> --md --depth 3 > .notion/page-title.md
```

### Export a database

```bash
notion db export <database-id> --format csv -o report.csv
notion db export <database-id> --format json
notion db export <database-id> --format md -o report.md
```

### Raw API escape hatch

For anything the CLI doesn't cover:

```bash
notion api GET /v1/users/me
notion api POST /v1/search '{"query":"test","filter":{"property":"object","value":"page"}}'
```

---

## Non-Admin Limitations

These are Notion API constraints, not CLI limitations. Understanding them prevents frustration:

| Limitation | Explanation | Workaround |
|------------|-------------|------------|
| Pages must be shared | Integration only sees pages explicitly shared with it | Share top-level pages to inherit access to children |
| Search is incomplete | `/v1/search` does not guarantee exhaustive results | Use `notion page list` to discover pages; query specific databases instead of relying on search |
| No workspace-wide access | Cannot list all workspace pages without sharing | Share each root page/database individually |
| Search indexing delay | Newly shared pages may not appear in search immediately | Wait a few minutes, or use the page ID directly |
| 3 requests/second rate limit | Notion enforces strict rate limiting | The CLI handles this internally; for bulk operations, expect slower throughput |
| No content search | Search is title-based only, not full-text | Search by title, then fetch specific pages to read content |
| Read-only recommended | This skill uses read-only capabilities | Disable write capabilities in integration settings for safety |

---

## Common Patterns

### "Find me that doc about X"

```bash
notion search "X" --type page
```

Then read the result:
```bash
notion page view <id-from-search>
```

### "Get all tasks marked High Priority"

```bash
notion db query <tasks-db-id> -F 'Priority=High'
```

### "Read an entire knowledge base page with subsections"

```bash
notion block list <page-id> --md --depth 5 --all
```

### "What databases do I have access to?"

```bash
notion search "" --type database
```

### "Export a sprint board to CSV"

```bash
notion db export <sprint-db-id> --format csv -o sprint.csv
```

---

## Requirements

- `notion-cli` binary installed and in PATH
- Notion integration token authenticated via `notion auth login --with-token` or `NOTION_TOKEN` env var
- Pages/databases shared with the integration in Notion UI

Note: Credentials are stored in `~/.config/notion-cli/config.json` (mode 0600) or provided via `NOTION_TOKEN` env var. Never log or display the token per OC002.

---

## Error Handling

| Error | Resolution |
|-------|------------|
| `object_not_found` | Page/database not shared with integration. Share it via Notion UI: `...` > Add connections |
| `unauthorized` | Token invalid or revoked. Run `notion auth login --with-token` again |
| `rate_limited` | Too many requests. Wait and retry. The CLI retries automatically on 429s |
| `restricted_resource` | Integration lacks required capability. Enable "Read content" in integration settings |
| `command not found: notion` | Install notion-cli: `brew install 4ier/tap/notion-cli` |
| `notion auth status` shows no profile | Run `notion auth login --with-token` or set `NOTION_TOKEN` |
| Empty search results | Page may not be shared with integration, or search indexing is delayed. Try the page ID directly |

---

## Tips

- All commands accept Notion URLs OR UUIDs (e.g., `https://notion.so/My-Page-abc123...` or just `abc123...`)
- Use `--format json` on any command for machine-readable output (for piping to `jq`)
- Use `notion auth doctor` to diagnose connection issues
- Use `notion auth switch <profile>` to manage multiple workspaces
- Sub-pages inherit sharing from their parent -- share a root page to access all descendants