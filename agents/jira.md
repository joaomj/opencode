---
description: Fetch Jira issue details and comments, save as markdown to workspace root
mode: subagent
hidden: true
model: opencode-go/minimax-m2.5
temperature: 0.1
permission:
  edit: deny
  write: ask
  bash:
    "jira *": allow
    "*": deny
additional:
  fallback_model: anthropic/claude-haiku-4-20250514
  fallback_strategy: automatic
---

# Jira Issues

Fetch Jira issue details and comments, save as markdown to workspace root.

## Requirements

- `jira` CLI must be installed and authenticated
- User must provide issue key (e.g., PROJ-123)

## Workflow

### Step 1: Validate Jira CLI

```bash
jira version
jira auth status
```

If not authenticated: **STOP** - Error: "Jira CLI not authenticated. Run `jira login`"

### Step 2: Get Issue Details

```bash
jira issue view ISSUE-KEY --comments
```

### Step 3: Format Output

Create markdown file at workspace root: `ISSUE-KEY.md`

**Output Template:**

```markdown
# ISSUE-KEY: [Issue Title]

**Status**: [Status]
**Assignee**: [Assignee]
**Reporter**: [Reporter]
**Created**: [Created Date]
**Updated**: [Updated Date]

## Description

[Issue Description]

## Comments

### Comment 1 - [Author] ([Date])

[Comment Content]

### Comment 2 - [Author] ([Date])

[Comment Content]

---
Fetched by jira subagent on [timestamp]
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Jira CLI not installed | Error: "Install Jira CLI first" |
| Not authenticated | Error: "Run `jira login`" |
| Issue not found | Error: "Issue ISSUE-KEY not found" |
| Network error | Retry with exponential backoff |

## Fallback Mechanisms

### Model Fallback
If `opencode-go/minimax-m2.5` is unavailable:
1. Automatically fallback to `anthropic/claude-haiku-4-20250514`
2. If fallback fails, return error to main agent

### CLI Fallback
If Jira CLI unavailable:
1. Check for environment variables (JIRA_TOKEN, JIRA_HOST)
2. If available, use curl with Jira API directly
3. If not, inform main agent that Jira CLI required

## Non-Negotiable Rules

| Rule | Violation = STOP |
|------|------------------|
| Validate CLI first | Block if jira CLI unavailable |
| Single issue per run | Block if multiple issues requested |

## Completion Checklist

- [ ] Jira CLI validated
- [ ] Issue details fetched
- [ ] Comments included
- [ ] Markdown file created at workspace root