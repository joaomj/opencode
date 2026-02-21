---
description: Perform dual-subagent code review with P0-P3 severity levels
---
Use the Task tool to invoke BOTH subagents in parallel:
- code-reviewer-1 (GPT-5.3 Codex - high reasoning effort)
- code-reviewer-2 (GLM 4.7)

Pass identical scope to both reviewers.

Default scope: git diff origin/main...HEAD

Custom scopes available:
- "from feature-x to main" - branch comparison
- "commit abc123 vs def456" - commit comparison
- "PR #42" - pull request review

After both subagents complete:
1. Merge findings, deduplicating by (file, line, severity, issue title)
2. Group by file, prioritize P0 > P1 > P2 > P3
3. Write CODE_REVIEW.md at project root with consolidated report

Severity levels:
- P0: Critical (must block merge)
- P1: High (should fix before merge)
- P2: Medium (fix or follow-up)
- P3: Low (optional improvement)
