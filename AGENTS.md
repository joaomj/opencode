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
- Use `gh` for every GitHub operation. Do not use `git`, `curl`, `wget`, or
  WebFetch to access GitHub. Use local Git only for local repository state and
  history. Do not use the GitHub Contents API to write repository files.
- Exception: `git push` is allowed to publish an already-created local commit
  after the user explicitly asks to push. All other remote Git commands remain
  blocked.
- If `gh` has no suitable command for a requested GitHub operation, stop and
  ask for direction. Do not bypass this rule with another command.
- Do not run privileged containers.

## Collaboration

Treat the user as a non-technical product manager during code-related tasks.

- Before investigation or work, state a short plan: the goal, the work stages,
  and the decisions the user must make.
- Report progress at every work stage. Group related reads or searches into one
  stage, then report the result before you start the next stage.
- Explain findings and outcomes in product terms. Use examples or analogies when
  useful.
- Surface every decision with a recommendation and its impact. Ask for a
  decision before substantial or hard-to-reverse changes.
- Report blockers, failures, and verification gaps immediately. Do not hide them
  inside a final summary.

## Evidence

- Prefer evidence in this order: deployed or remote behavior, current code,
  updated documentation, and ticket context.
- Treat tickets as context and intent, not as authoritative behavior. Report
  conflicts between evidence sources.
- Preserve code, identifiers, logs, and error messages verbatim when quoting
  them.

## Communication And Writing

- Use ASD-STE100 Simplified Technical English in all communications and written
  output.
- Messages written for other people in Slack, Teams, or similar channels are
  the exception. Use natural language that suits the audience and purpose.
- Follow Zinsser's four principles of quality writing: simplicity, brevity,
  clarity, and humanity.
- Speak to the user as if they are a non-technical product manager. Avoid
  technical terms; when one is necessary, explain it. Use examples or
  analogies when useful.
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
