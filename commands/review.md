---
description: Perform dual-subagent code review with P0-P3 severity levels
agent: code-review
subtask: true
---
Perform code review of current changes using dual subagents for 85-95% issue coverage.

Default scope: git diff origin/main...HEAD

Custom scopes available:
- "from feature-x to main" - branch comparison
- "commit abc123 vs def456" - commit comparison
- "PR #42" - pull request review

Subagent models:
- Reviewer 1: GPT-5.3 Codex (high reasoning effort)
- Reviewer 2: Claude Opus 4.5 (fallback GLM 4.7)

Severity levels:
- P0: Critical (must block merge)
- P1: High (should fix before merge)
- P2: Medium (fix or follow-up)
- P3: Low (optional improvement)

Iterative loop continues until:
1. No P0 or P1 issues remain, OR
2. Max 3 iterations reached, OR
3. No progress between iterations

Output: CODE_REVIEW.md at project root with findings grouped by file.
