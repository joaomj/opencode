---
name: jira-issues
description: Fetch Jira issue details and comments, save as markdown to workspace root
compatibility: opencode
---

## Trigger
When user asks to fetch a Jira issue (e.g., "get Jira issue ML-502" or "fetch TDT-2558")

## Workflow

Run the helper script with the issue key:

```bash
$HOME/.config/opencode/skills/jira-issues/bin/jira_fetch.sh TDT-2554
```

This script will:
1. Load `.env` from current directory (which contains JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_KEY)
2. Fetch issue details and comments from Jira API
3. Convert ADF description to markdown
4. Save to `{lowercase-issue-key}.md` in current directory

## Requirements

- `.env` file in current directory with:
  ```
  JIRA_BASE_URL=https://yourcompany.atlassian.net
  JIRA_EMAIL=your.email@company.com
  JIRA_API_KEY=your_api_token_here
  ```
- curl and jq installed

## Output

Creates `{issue-key}.md` with:
- Issue key and summary (H1)
- Status, assignee, created/updated dates
- Description (basic ADF to markdown conversion)
- Comments (if any)

## Error Handling

If script fails:
- Check `.env` exists in current directory
- Verify all three JIRA_* variables are set
- Ensure issue key is valid and accessible
- Raw curl errors displayed for debugging
