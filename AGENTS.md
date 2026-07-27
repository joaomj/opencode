# AGENTS.md

## Core Principles

- **no-assumptions**: read code first, no hedging ("likely", "probably", "might"). investigate if uncertain
- **branch-sync-before-pr**: before creating a PR, check the current branch against the destination branch for conflicts. Do not rebase or merge automatically just to create the PR
- **infra-code-separation**: separate commits+PRs from app code changes. exception if deeply intertwined, call out in PR description
- **no-silent-failures**: every failure must surface. logged, raised, or classified recoverable
- **gh-cli-only**: all GitHub via `gh` CLI only (PRs, issues, releases, code, refs). no curl/wget/WebFetch against github.com
- **signed-commits**: every commit signed with SSH key from `~/.gitconfig`. always `-S`, never `--no-gpg-sign`
- **no-api-commits**: never use GitHub Contents API or `gh api --method PUT`
- **never-read-env**: never read/inspect `.env` values. use `os.getenv()` only
- **no-privileged-containers**: never run privileged containers

## Opencode Map

- **Config**: `opencode.json`
- **Skills**: `skills/**/SKILL.md`: load when the description matches the task
- **Teams messaging**: use `skills/tooling/teams-brave-cli/SKILL.md` with the local Python CLI for Teams message access via Brave session token extraction; never use Playwright MCP or personal browser profiles
- **Commands**: `commands/*.md`
- **Linter**: `opencode_lint/`
- **Linter rules**: `opencode_lint/rules/`

## Quality

- Substantial features or architecture work: write a spec for user approval before code
- Bug fixes: write a failing e2e or blackbox regression test before the fix (TDD)
- Common coding: prioritize e2e and blackbox tests against user-visible behavior
- Mutations must be safe to retry
- Multi-step or long-running work needs checkpointing and error handling
- Prefer Python for non-trivial automation; bash for one-liners

## Skills Workflow (Matt Pocock)

### Incoming work gate

Raw issues and PRs enter through `/triage`, which sorts them through a state machine:

```
raw report  →  /triage  →  needs-triage  →  needs-info  →  ready-for-agent  →  /implement
                                                ↓                ↗
                                             wontfix         ready-for-human
```

`/triage` categorises (bug/enhancement), verifies claims (reproduce bugs, check out PRs), grills incomplete requests into shape, and produces agent-ready briefs. See `skills/matt-pocock/triage/SKILL.md`.

### Standard build chain

The standard flow for feature work:

```
/grill-with-docs  →  /to-spec  →  /to-tickets  →  /implement  →  /code-review
```

| Step | Skill | Purpose |
|------|-------|---------|
| 1 | `/grill-with-docs` | Agent grills you on goals, builds domain glossary + ADRs |
| 2 | `/to-spec` | Synthesizes conversation into a spec on the issue tracker |
| 3 | `/to-tickets` | Breaks spec into vertical-slice tickets with blocking edges, asks approval, publishes |
| 4 | `/implement` | One ticket per session using e2e and blackbox tests for user-visible behavior, typechecks, runs tests |
| 5 | `/code-review` | Two-axis review: Standards (coding standards + Fowler smells + P0-P3 checklists) and Spec (correctness). FAIL-CLOSED on P0/P1. |

### Supporting skills

These are model-invoked (reached automatically when the description matches) or user-invoked as needed:

| Skill | Invocation | Purpose |
|-------|-----------|---------|
| `/domain-modeling` | model | Maintain domain glossary (`CONTEXT.md`) and ADRs during any phase. Sharpen fuzzy terms, cross-reference code, offer ADRs sparingly. Called internally by `grill-with-docs`, `triage`, and `improve-codebase-architecture`. |
| `/codebase-design` | model | Shared vocabulary for deep modules: interface, seam, adapter, depth, leverage, locality. Design-it-twice sub-agent pattern for alternative interfaces. Called by `implement`, `code-review`, and `improve-codebase-architecture`. |
| `/wayfinder` | user | Plan oversized work as a shared map of investigation tickets on the issue tracker, resolved one per session until the route is clear. Runs before the standard flow. |
| `/improve-codebase-architecture` | user | Scan codebase for deepening opportunities (shallow modules), present as visual HTML report with Mermaid diagrams, grill through the chosen candidate. |
| `/diagnosing-bugs` | model | Disciplined diagnosis loop for hard bugs: build a feedback loop, reproduce, minimise, hypothesise, instrument, fix, regression-test, clean up, and record a postmortem. |
| `/prototype` | model | Throwaway code to answer a design question (logic or UI). |
| `/research` | model | Investigate a question against primary sources, write findings to a Markdown file. |

## Writing Style

- no emojis
- no em dashes. use comma, colon, or restructure
- professional tone
- concise, say it in fewer words
- no AI filler ("Certainly", "Of course", "Absolutely", "Great question", "Happy to help")
