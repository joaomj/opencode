# AGENTS.md

## Core Principles

- **no-assumptions**: read code first, no hedging ("likely", "probably", "might"). investigate if uncertain
- **branch-sync-before-pr**: `git fetch && git rebase origin/<base>` (or `--ff-only`) before pushing or creating PRs (commit command skips this)
- **infra-code-separation**: separate commits+PRs from app code changes. exception if deeply intertwined, call out in PR description
- **no-silent-failures**: every failure must surface. logged, raised, or classified recoverable
- **gh-cli-only**: all GitHub via `gh` CLI only (PRs, issues, releases, code, refs). no curl/wget/WebFetch against github.com
- **signed-commits**: every commit signed with SSH key from `~/.gitconfig`. always `-S`, never `--no-gpg-sign`
- **no-api-commits**: never use GitHub Contents API or `gh api --method PUT`
- **never-read-env**: never read/inspect `.env` values. use `os.getenv()` only
- **no-privileged-containers**: never run privileged containers

## Opencode Map

- **Config**: `opencode.json`, `local.json`
- **Skills**: `skills/*/SKILL.md` — load when the description matches the task
- **Google Drive files**: use `skills/google-drive-files/SKILL.md` for uploading, downloading, and listing files on personal Google Drive via rclone
- **Teams messaging**: use `skills/teams-brave-cli/SKILL.md` with the local Python CLI for Teams message access via Brave session token extraction; never use Playwright MCP or personal browser profiles
- **Commands**: `commands/*.md`
- **Linter**: `opencode_lint/`
- **Linter rules**: `opencode_lint/rules/`

## Quality

- Substantial features or architecture work: write a spec for user approval before code
- Bug fixes: write a failing test before the fix (TDD)
- Mutations must be safe to retry
- Multi-step or long-running work needs checkpointing and error handling
- Prefer Python for non-trivial automation; bash for one-liners

## Skills Workflow (Matt Pocock)

The standard flow for feature work:

```
/grill-with-docs  →  /to-spec  →  /to-tickets  →  /implement  →  /code-review
```

| Step | Skill | Purpose |
|------|-------|---------|
| 1 | `/grill-with-docs` | Agent grills you on goals, builds domain glossary + ADRs |
| 2 | `/to-spec` | Synthesizes conversation into a spec on the issue tracker |
| 3 | `/to-tickets` | Breaks spec into vertical-slice tickets with blocking edges, asks approval, publishes |
| 4 | `/implement` | One ticket per session using TDD at agreed seams, typechecks, runs tests |
| 5 | `/code-review` | Two-axis review: Standards (coding standards + Fowler smells + P0-P3 checklists) and Spec (correctness). FAIL-CLOSED on P0/P1. |

### Wayfinder

For work too large for one agent session, use `/wayfinder` before the standard flow. It charts a shared map of investigation tickets (research, prototype, grilling, task) on the issue tracker with blocking relationships, resolved one per session until the route is clear. Then feed the result into the standard flow above.
