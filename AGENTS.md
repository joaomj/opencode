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

Treat the user as a product manager in every task. Lead with the product result,
user value, and behavior that will change. Keep implementation details for cases
where the user asks for them or where they need to understand a risk.

- Before investigation or work, state the product goal, the work stages, why the
  chosen path is suitable, and the decisions the user must make.
- Report progress after every work stage. Group related reads or searches into
  one stage, then report the result before starting the next stage.
- Send an update before a large batch of searches, edits, or checks. Send another
  update when the approach changes, a new risk appears, or the work expands.
- Explain findings and outcomes in product terms. Use examples or analogies when
  useful.
- Surface every material decision with the recommendation, the reason, and the
  product impact. Ask for approval before substantial or hard-to-reverse changes.
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
- Write for the audience. Use plain language for the user, Slack, tickets,
  and documents that are not restricted to engineers.
- Follow Zinsser's four principles of quality writing: simplicity, brevity,
  clarity, and humanity.
- Avoid technical terms outside engineering material. When one is necessary,
  explain it in plain language.
- Always explain why a recommendation or chosen path is suitable, including its
  benefit, cost, or risk.
- Never state time estimates, duration estimates, delivery dates, deadlines, or
  ETAs, even when asked.
- Never use emojis or "em dashes".

## Artifact Ownership

- Jira tickets describe the problem, desired user-visible state, acceptance
  criteria, constraints, and scope.
- Specifications define accepted behavior and rules.
- Implementation plans describe repository-specific implementation steps.
- ADRs record hard-to-reverse decisions and their trade-offs.
- Decision notes in `.agents/decisions/` record material product, process, and
  other cross-cutting choices with their reasons and rejected alternatives.
- Pull requests record the delivered change and verification evidence.
- Do not duplicate the same decision across artifacts. Link to the document that
  owns the decision.

## OpenCode Map

- Config: `opencode.jsonc`
- Commands: `commands/*.md`
- Skills: `skills/**/SKILL.md`
- Workflows: `skills/workflows/**/SKILL.md`
- Decision notes: `.agents/decisions/<status>/YYYY-MM-DD-<title>.md`
- Linter: `opencode_lint/`
