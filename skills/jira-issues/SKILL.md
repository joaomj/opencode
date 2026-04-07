---
name: jira-issues
description: Fetch, create, and search Jira issues - agnostic to Jira host (Cloud/Server)
compatibility: opencode
---

## Triggers

| User says | Command invoked |
|-----------|-----------------|
| "get issue ML-502" / "fetch PROJ-123" | `jira.py fetch <key>` |
| "create jira issue" / "/create-jira" | `jira.py create` (interactive) |
| "search jira" / "jira search" | `jira.py search <jql>` |

## Workflow

### Setup: Venv Detection

When first using the skill, the skill directory is checked for a Python virtual environment.

**Search order:**
1. `$HOME/.config/opencode/skills/jira-issues/.venv`
2. `.venv` in current directory
3. `venv` in current directory

If found → ask user: "Use existing venv or create new?"

If not found → create `.venv` in `$HOME/.config/opencode/skills/jira-issues/.venv`

**To activate venv before running scripts:**
```bash
source $HOME/.config/opencode/skills/jira-issues/.venv/bin/activate
```

---

### Fetch Issue

**Trigger:** "get issue ML-502" or "fetch PROJ-123"

**Command:**
```bash
$HOME/.config/opencode/skills/jira-issues/.venv/bin/python \
  $HOME/.config/opencode/skills/jira-issues/jira.py fetch <issue-key>
```

**What it does:**
1. Loads `.env` from current directory (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_KEY)
2. Fetches issue details and comments via Jira REST API v3
3. Converts ADF description and comments to markdown
4. Saves to `{lowercase-issue-key}.md` in current directory

---

### Create Issue

**Trigger:** "create jira issue" or "/create-jira"

**Command:**
```bash
$HOME/.config/opencode/skills/jira-issues/.venv/bin/python \
  $HOME/.config/opencode/skills/jira-issues/jira.py create \
  --project-key <KEY> --summary "Issue summary"
```

**Interactive mode (no args):**
```bash
$HOME/.config/opencode/skills/jira-issues/.venv/bin/python \
  $HOME/.config/opencode/skills/jira-issues/jira.py create
```
Prompts for: project_key, summary, description, issue_type, story_points, labels, assignee

**Options:**
| Flag | Description |
|------|-------------|
| `--project-key` | Jira project key (required) |
| `--summary` | Issue summary (required) |
| `--description` | Issue description text |
| `--issue-type` | Type name, default: Story |
| `--story-points` | Numeric story points |
| `--labels` | Comma-separated labels |
| `--assignee` | accountId, "self", or "none" |
| `--story-points-field` | Custom field ID (default: customfield_10016) |
| `--dry-run` | Show what would be created without creating |
| `--yes` | Skip confirmation prompt |

---

### Search Issues

**Trigger:** "search jira" or "jira search"

**Command:**
```bash
$HOME/.config/opencode/skills/jira-issues/.venv/bin/python \
  $HOME/.config/opencode/skills/jira-issues/jira.py search "project = MYPROJ AND status = Open"
```

**Options:**
| Flag | Description |
|------|-------------|
| `--max-results` | Max results (default: 50) |
| `--fields` | Comma-separated fields to include |

---

## Requirements

- `.env` file in current directory with:
  ```
  JIRA_BASE_URL=https://yourcompany.atlassian.net
  JIRA_EMAIL=your.email@company.com
  JIRA_API_KEY=your_api_token_here
  ```
- Python 3.11+
- curl (for API calls)

Note: Credentials are loaded from `.env` programmatically - never logged or displayed per OC002.

## Output Formats

### Fetch Output (`{key}.md`)
- Issue key and summary (H1)
- Metadata table (type, status, priority, assignee, dates, labels, components)
- Description with ADF→markdown conversion
- Comments section (if any)

### Create Output (stdout)
- Logs project, type, summary, assignee, story points, labels
- On success: `Created: PROJ-123`
- On dry-run: shows what would be created

### Search Output (stdout)
- One line per issue: `PROJ-123: Issue summary`

## ADF to Markdown

The Python converter handles:

**Text Marks:** bold, italic, strikethrough, inline code, underline, links

**Block Nodes:** headings, paragraphs, bullet/ordered lists, code blocks, blockquotes, horizontal rules, tables, panels, expandable sections

**Inline Nodes:** mentions, emojis, status badges, dates, hard breaks

## Error Handling

| Error | Resolution |
|-------|------------|
| "Missing Jira credentials" | Check `.env` exists with all JIRA_* vars |
| "Invalid issue key format" | Use format PROJ-123 (uppercase) |
| "curl failed" | Check network and Jira host accessibility |
| "Jira API 4xx/5xx" | Check permissions and issue key validity |
