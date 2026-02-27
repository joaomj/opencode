---
description: Perform dual-subagent code review with P0-P3 severity levels
---

## Execution Flow

1. **Invoke Both Subagents in Parallel**
   - code-reviewer-1 (GPT-5.3 Codex - high reasoning effort, or session model as fallback)
   - code-reviewer-2 (GLM 4.7, or session model as fallback)
   - Pass identical scope to both reviewers

2. **Handle Availability**
   - **Both succeed** → Proceed with dual-reviewer workflow
   - **Only one succeeds** → Continue with single reviewer
   - **Both fail** → Perform review yourself using session model

3. **Process Results**
   - Merge findings from successful reviewers (deduplicate by file, line, severity, issue)
   - Group by file, prioritize P0 > P1 > P2 > P3
   - Write CODE_REVIEW.md at project root with consolidated report

4. **Document Execution**
   - Include execution note in CODE_REVIEW.md (2 reviewers / 1 reviewer / main agent)

## Fallback Behavior

- Subagents automatically fall back to session model if primary is unavailable (no API key, quota exceeded, etc.)
- Main agent only performs review if BOTH subagents fail
- Review process never blocks - always completes with available reviewers

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
