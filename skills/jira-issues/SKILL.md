---
name: jira-issues
description: Search assigned Jira issues and update only status or description
compatibility: opencode
metadata:
  write_scope: status-transition-and-description-only
---

## What I do
- Search Jira issues in the configured project assigned to the authenticated user.
- Read one assigned issue by key.
- Update assigned issues by either transitioning status or replacing description.

## Hard limits
- Only operate on issues in the project specified by `JIRA_PROJECT_KEY`.
- Only operate on issues assigned to `currentUser()`.
- Allowed writes are only:
  - status transitions
  - description updates
- Never create, delete, reassign, comment, or edit any other fields.

## Command runner
ALWAYS run this first to load environment variables:
```bash
(set -a; source .env; set +a)
```

Then use the helper script for every Jira action:

```bash
python3 ".opencode/skills/jira-issues/bin/jira_issue.py" search --limit 20
python3 ".opencode/skills/jira-issues/bin/jira_issue.py" search --jql "status = \"In Progress\""
python3 ".opencode/skills/jira-issues/bin/jira_issue.py" get PROJECTKEY-123
python3 ".opencode/skills/jira-issues/bin/jira_issue.py" transition PROJECTKEY-123 "In Progress"
python3 ".opencode/skills/jira-issues/bin/jira_issue.py" update-description PROJECTKEY-123 --text "Updated details"
```

## Usage workflow
1. If the issue key is unknown, run `search` first.
2. Run `get` for the target issue before any write operation.
3. Perform exactly one requested write operation.
4. Report the issue key and the applied change.

## Environment required
All variables are required:
- `JIRA_BASE_URL` - Your Jira instance URL (e.g., `https://yourcompany.atlassian.net`)
- `JIRA_EMAIL` - Your Jira account email (or pass `--jira-email` to the helper)
- `JIRA_API_KEY` - Your Jira API key
- `JIRA_PROJECT_KEY` - The project key to operate within (e.g., `PROJ`)

## Error handling
- If `JIRA_EMAIL` is missing, ask the user for their Jira email and rerun using `--jira-email`.
- If `JIRA_API_KEY` is missing, do not ask the user to share it in chat; ask them to set it in shell and retry.
- If an issue is not assigned to the authenticated user, stop and report access denied.
- If a transition name is not available, report available transition names.
- If auth fails, report missing/invalid Jira credentials.
