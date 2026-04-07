---
description: Perform code review with P0-P3 severity levels
---

## Execution Flow

1. **Identify Task Context**
   - Ask user for task context (Jira issue, plan file, feature description)
   - Extract specific files/functions related to the task
   - Focus review scope on task-related code only

2. **Analyze Code Against Checklists**
   - Get git diff for the scope
   - Apply all checklists: SOLID, security, performance, code quality
   - Categorize findings by severity (P0-P3)
   - Filter findings to task scope only

3. **Ask User Before Writing Report**
   - Present summary of findings (P0/P1/P2/P3 counts)
   - Get approval before creating CODE_REVIEW.md

4. **Write Report (After Approval)**
   - Write CODE_REVIEW.md at project root
   - Include task context, scope, and iteration history

Default scope: git diff origin/master...HEAD

Custom scopes available:
- "from feature-x to master" - branch comparison
- "commit abc123 vs def456" - commit comparison
- "PR #42" - pull request review

Severity levels:
- P0: Critical (must block merge)
- P1: High (should fix before merge)
- P2: Medium (fix or follow-up)
- P3: Low (optional improvement)
