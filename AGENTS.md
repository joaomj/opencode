# AGENTS.md

This file contains repository-wide guardrails. Detailed procedures belong in
the relevant skill or command; do not duplicate them here.

## Working Rules

- Read the current code and relevant documentation before making claims or
  edits. Investigate when uncertain.
- Before `apply_patch`, read every existing `Update File` or `Delete File` target
  in the same session. If a patch fails, read the target again before retrying.
- Preserve unrelated user changes. Never reset, check out, overwrite, or
  otherwise discard them.
- Keep side effects within the user's request. Do not create commits, branches,
  tickets, pull requests, or remote writes without explicit authorization.
- Request native approvals one at a time. State the exact action, target, and
  reason before each request.
- Preserve the exact native denial reason. If the API does not return a cause,
  state that the cause is unavailable and identify the permission layer.
- Surface failures and verification gaps. Do not silently skip them.
- Treat a successful Git operation as complete. Do not run a redundant
  post-operation status or diff inspection. Inspect again only after an error,
  or when the next action needs unresolved state.
- Run commands that may outlive the shell timeout in detached mode, such as with
  `nohup`, redirected logs, and background execution. Monitor the process and
  report its final status so the user can close the agent or shell safely.
- Do not inspect `.env` values or expose secrets. Use the application's
  supported configuration interface.
- Use native Git for local state, history, and remote transport operations such
  as clone, fetch, pull, and push.
- Use `gh` for GitHub write operations such as pull request, issue, release, and
  repository changes. Do not replace native Git transport with `gh`.
- Keep local branch operations such as merge and rebase in native Git when the
  task requires them. Do not treat a local branch operation as a GitHub write.
- If `gh` has no suitable command for a requested GitHub write, stop and ask for
  direction. Do not bypass this rule with another GitHub API or shell command.
- When you study a repository outside the current worktree, first use
  `git clone --depth 1 --single-branch <url> <approved-temp-path>`. This checks
  out the remote default branch without an API query. Study the local clone and
  use remote APIs only when the clone cannot provide the required evidence.
- Do not use the GitHub Contents API to write repository files.
- Python is blocked. Run all Python work through `uv` or `uvx`. Direct
  `python`, `python3`, `pip`, `pip3`, `pytest`, `ruff`, `mypy`, and similar
  commands are denied by the permission config; do not attempt them.
- Do not run privileged containers.

## Collaboration

Treat the user as a product manager in every task. Lead with the product result,
user value, and behavior that will change. Keep implementation details for cases
where the user asks for them or where they need to understand a risk.

- Before investigation or work, state the product goal, the work stages, why the
  chosen path is suitable, and the decisions the user must make.
- Report progress after every work stage. Group related reads or searches into
  one stage, then report the result before starting the next stage.
- If a stage has no result after five minutes, report that it is still running,
  give the latest evidence, and state the next check.
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

- Use field-matched voice. Select the style from the field table below. Code is never humanized.
- For artifacts marked STE in the table, follow ASD-STE100 Issue 9 and `skills/documentation/technical-writing/SKILL.md`. The `technical-writing` skill owns file artifacts only. It does not own chat.
- For artifacts marked Human in the table, use the prose of a typical person from that field. Use short active sentences and concrete references. Do not use AI tells such as delve, comprehensive, crucial, leverage, or it is important to note. Do not use em dashes. Do not impersonate a named person or sign as them.
- For chat, progress updates, and direct assistance, follow the Communication Contract below. When the contract and a skill conflict in chat, the contract wins.
- Follow Zinsser's four principles of quality writing for all artifacts: simplicity, brevity, clarity, and humanity.
- Always explain why a recommendation or chosen path is suitable, including its benefit, cost, or risk.
- Never state time estimates, duration estimates, delivery dates, deadlines, or ETAs, even when asked.
- Never use emojis or em dashes.

Field table, authoritative:

| Artifact | Voice | Note |
|---|---|---|
| Code and code comments | STE | Technical, not humanized |
| Reports, Tech Context, How-to, Reference, API docs, Safety instructions | STE | Per `technical-writing` skill, files only |
| Pull requests, title and body | STE | ASD-STE100 |
| Commit messages | STE | ASD-STE100 plus repo and org conventions |
| Code review comments | Human | Prose of a typical software engineer; chat explanations of reviews still follow the Communication Contract |
| Issue comments and PR comments | Human | Prose of a typical software engineer; chat explanations of issues still follow the Communication Contract |
| Slack, chat, and direct assistance | Human | Follows the Communication Contract, concise and direct |

### Communication Contract (chat and progress updates)

Lead with the product result. State what the user can see or do. Put implementation details last.

- Assume the reader does not know the internal system. Define an unfamiliar technical term before you use it. Reuse the exact term. Do not swap synonyms.
- When you introduce a new component or failure, explain what it is, where it lives, who uses it, why they use it, whether it runs automatically or manually, and what normal behavior looks like. Keep this to two or three sentences for known systems.
- Then explain the problem in this order: what is wrong, the exact trigger, a numbered example with real objects, the user-visible result, how likely the path is, the smallest permanent fix, and one focused check after the fix.
- Preserve code, commands, paths, identifiers, numbers, error messages, and quoted material verbatim. Never rewrite them for style.
- Use short active sentences. Use one idea per sentence. Target 15 to 20 words. Keep prose under 25 words per sentence. Code, paths, commands, errors, tables, and headings are exempt.
- Do not use hollow openers such as Great question, Let us dive in, When it comes to, In recent years, or In today’s fast paced world.
- Do not use filler such as delve, moreover, furthermore, robust, seamless, leverage as a verb, unlock, empower, game changer, cutting edge, deep dive, paradigm shift, synergy, holistic, tapestry, or a testament to.
- Do not use contrast frames such as it is not X, it is Y or not X but Y. State the one claim plainly.
- When prose stays abstract, use the smallest visual from the `show-me` skill. Prefer inline pseudocode, call trees, file trees, Mermaid, or diffs. Do not create HTML or SVG files for chat unless the user asks for a diagram file.
- Example. Avoid: The cache invalidation hook has a race during asynchronous compaction. Prefer: OpenCode keeps a short stored copy of earlier conversation details. This copy helps the agent continue after a long session. Two operations can update that copy at the same time. One update can replace newer information with older information.

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
