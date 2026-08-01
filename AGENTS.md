# AGENTS.md

This file contains repository-wide guardrails. Detailed procedures belong in
the relevant skill or command; do not duplicate them here.

## Working Rules

- Read the current code and relevant documentation before making claims or
  edits. Investigate when uncertain.
- Preserve unrelated user changes. Never reset, check out, overwrite, or
  otherwise discard them.
- Keep side effects within the user's request. Do not create commits, branches,
  tickets, pull requests, or remote writes without explicit authorization.
- Surface failures and verification gaps. Do not silently skip them.
- Do not inspect `.env` values or expose secrets. Use the application's
  supported configuration interface.
- Use `gh` for GitHub operations. Do not use the GitHub Contents API to write
  repository files.
- Do not run privileged containers.

## Evidence

- Prefer evidence in this order: deployed or remote behavior, current code,
  updated documentation, and ticket context.
- Treat tickets as context and intent, not as authoritative behavior. Report
  conflicts between evidence sources.
- Preserve code, identifiers, logs, and error messages verbatim when quoting
  them.

## Communication

- Use ASD-STE100 technical English.
- Speak to the user as if they are a non-technical product manager. Avoid
  technical terms; when one is necessary, explain it. Use examples or
  analogies when useful. This applies to direct user communication, not to
  technical writing such as documentation or reports.
- Do not mention time estimates unless asked.
- Never use emojis or "em dashes".

## Artifact Ownership

- Jira tickets describe the problem, desired user-visible state, acceptance
  criteria, constraints, and scope.
- Specifications define accepted behavior and rules.
- Implementation plans describe repository-specific implementation steps.
- ADRs record hard-to-reverse decisions and their trade-offs.
- Pull requests record the delivered change and verification evidence.
- Do not duplicate the same decision across artifacts. Link to its source.

## OpenCode Map

- Config: `opencode.jsonc`
- Commands: `commands/*.md`
- Skills: `skills/**/SKILL.md`
- Workflows: `skills/workflows/**/SKILL.md`
- Linter: `opencode_lint/`
