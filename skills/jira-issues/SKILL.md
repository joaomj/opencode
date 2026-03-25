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
2. Fetch issue details and comments from Jira API v3
3. Convert Atlassian Document Format (ADF) description and comments to markdown
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
- Metadata table (type, status, priority, assignee, dates, labels, components)
- Description with full ADF to markdown conversion
- Comments (if any) with author and date

## ADF to Markdown Conversion

The converter supports:

**Text Marks:**
- Bold (`**text**`)
- Italic (`*text*`)
- Strikethrough (`~~text~~`)
- Inline code (`` `text` ``)
- Underline (`<u>text</u>`)
- Links (`[text](url)`)

**Block Nodes:**
- Headings (H1-H6)
- Paragraphs
- Bullet lists
- Numbered lists
- Code blocks with language support
- Blockquotes
- Horizontal rules
- Tables
- Panels (info/warning/error)
- Expandable sections

**Inline Nodes:**
- Mentions (@username)
- Emojis
- Status badges
- Dates

## Error Handling

If script fails:
- Check `.env` exists in current directory
- Verify all three JIRA_* variables are set
- Ensure issue key is valid and accessible
- Raw curl errors displayed for debugging
