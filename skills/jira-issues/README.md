# jira-issues skill

OpenCode skill to search and update Jira issues in a configured project.

## Scope

- Reads only issues assigned to the authenticated user.
- Writes allowed:
  - transition status
  - replace description
- Writes denied for unassigned issues.

## Required environment variables

All required:
- `JIRA_BASE_URL` - Your Jira instance URL (e.g., `https://yourcompany.atlassian.net`)
- `JIRA_EMAIL` - Your Jira account email
- `JIRA_API_KEY` - Your Jira API key
- `JIRA_PROJECT_KEY` - The project key to operate within

Optional:
- `--jira-email` flag on commands when `JIRA_EMAIL` is not set

## Commands

```bash
python3 .opencode/skills/jira-issues/bin/jira_issue.py search --limit 20
python3 .opencode/skills/jira-issues/bin/jira_issue.py --jira-email "you@company.com" search --limit 20
python3 .opencode/skills/jira-issues/bin/jira_issue.py get PROJECTKEY-123
python3 .opencode/skills/jira-issues/bin/jira_issue.py transition PROJECTKEY-123 "In Progress"
python3 .opencode/skills/jira-issues/bin/jira_issue.py update-description PROJECTKEY-123 --text "New details"
```

Use `--text -` to read a long description from stdin.
