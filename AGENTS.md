# AGENTS.md

## Core Principles

- **sdd-by-default**: spec before code for all non-bug work. TDD for bug fixes only
- **docker-by-default**: prefer Docker over local installs, clean up after
- **no-assumptions**: read code first, no hedging ("likely", "probably", "might"). investigate if uncertain
- **remote-first-code**: prefer remote GitHub via `gh` over local clones (may be stale). verify before asserting current behavior
- **branch-sync-before-work**: `git fetch && git rebase origin/<base>` (or `--ff-only`) before any write. do not skip
- **infra-code-separation**: separate commits+PRs from app code changes. exception if deeply intertwined, call out in PR description
- **no-silent-failures**: every failure must surface. logged, raised, or classified recoverable. silent failures = P1 defect (OC021)
- **gh-cli-only**: all GitHub via `gh` CLI only (PRs, issues, releases, code, refs). no curl/wget/WebFetch against github.com
- **signed-commits**: every commit signed with SSH key from `~/.gitconfig`. always `-S`, never `--no-gpg-sign`
- **no-api-commits**: never use GitHub Contents API or `gh api --method PUT`. bypasses signing, hooks, identity. use local: clone -> edit -> `git add` -> `git commit -S` -> `git push`. no exceptions
- **never-read-env**: never read/inspect `.env` values. use `dotenv.load_dotenv()` or `os.getenv()` only (OC002)
- **no-privileged-containers**: never run privileged containers (OC003)

## Output Style

- no em dashes in output, code, commits, or docs. use comma, colon, or restructure
- no emojis
- no AI filler ("Certainly", "Of course", "Absolutely", "Great question", "Happy to help")

## Skill Routing

| Intent | Action |
|--------|--------|
| Any coding activity | Load `coding-best-practices` skill |
| SWE: feature, bug fix, refactor, AI feature | Load `coding-best-practices` |
| ML/data: analysis, experiment, model training | Load `ml-best-practices` |
| Jira ticket (any domain) | Load `jira-issues` skill, classify intent, then load `coding-best-practices` or `ml-best-practices` |
| Code review | Load `code-reviewer` skill |
| Research libraries/APIs | Load `context7` skill |
| ML: experiments, eval, training, production code | Load `ml-best-practices` |
| README, API docs, technical reports | Load `technical-writing` |
| Documentation maintenance, cleanup | Load `doc-maintenance` |
| System architecture/design/ADRs | Include the Architecture and Design Gate; load `technical-writing` |
| Simplify code | Load `simplify` skill (only on explicit user request) |
| Write or record an issue | Load `issue-writing` skill, create `docs/issues/<slug>.md` |
| E2E/integration testing | Load `e2e-testing` skill |
| CI/CD | Load `github-cicd-lite` or `docker-best-practices` |
| Architecture diagram | Load `architecture-diagram` or `c4-diagram` |
| Browser debugging | Load `browser-readonly` skill and use `browser_cdp.py` for screenshots, DOM, JS eval, console, and network via local Brave/Chromium CDP |
| Planning | Use `/plan` |
| Create a pull request | Load `create-pull-request` |
| Fetch X/Twitter posts | Load `fetch-x-posts` skill, run the CLI script |

## Routing Determinism

Incompatible routes: ask user to choose with concrete options. Compatible+mandatory routes: load all.

Explicit intent > semantic inference:
- named skill -> load it
- review request -> don't edit
- impl request -> follow coding gates

Always ask user with options for:
- review vs impl same diff
- planning vs editing same task
- skill-based work vs git-based workflow
- destructive vs non-destructive
- ambiguous command routing
- simplify vs broader refactor

## Coding Standards

Always load `coding-best-practices` skill for any coding activity. Enforces quality, idempotency, error treatment, logging, async safety, hardcoding avoidance.

- **linter before commit**: `ruff check .` before `git commit` when Python involved, block if errors
- **no hardcoded values**: config only (URLs, ports, timeouts, thresholds). OC014. extract before writing
- **idempotent mutations**: all state changes safe to retry (upserts, if-not-exists, dedup keys)
- **failure-resilient execution**: multi-step/long-running code needs retries, checkpointing, durable logs, batching, concurrency guards
- **python over bash**: prefer Python for non-trivial automation. bash ok for one-liners
- **no test artifacts in git**: test output, reports, scratch files.

## Architecture and Design Gate

For substantial coding tasks, `plan` must include architecture+design discussion before implementation.

Must cover:
- problem boundaries, core use cases, non-goals
- module/component boundaries and ownership
- data flow, control flow, external integrations
- key abstractions, interfaces, dependency direction
- state mgmt, persistence, idempotency, retry
- error handling, observability, security
- tradeoffs between >=2 viable designs
- risks, unknowns, validation steps

Final plan names chosen design, explains why, and calls out what forces revisiting it.

## Workflow

| Condition | Action |
|-----------|--------|
| Code changes affect public API | Suggest documentation updates |
| Phase gate passed | Ask to commit directly to `main` |
| User requests commit | Commit changes and push to `main` |
| User requests release | Create a semver tag (`git tag -a v<major>.<minor>.<patch>`) and push tags (`git push origin --tags`) |
| Review finds P0 or P1 | Block merge (FAIL-CLOSED). Fix and re-review. |

## Rules

Enforced by the `opencode-lint` linter (`opencode_lint/`). Run with `opencode-lint` or via the CLI.

| ID | Rule | File |
|----|------|------|
| OC001 | No raw dicts for API schemas | `no_raw_dict_api.py` |
| OC004 | Absolute imports preferred | `absolute_imports.py` |
| OC005 | Strict type hints required | `strict_type_hints.py` |
| OC008 | No skipped, xfailed, or suppressed failing tests | testing/process rule |
| OC009 | Lockfile must exist and be committed | `lockfile_required.py` |
| OC010 | `exclude-newer` with 7-day buffer in pyproject.toml | `exclude_newer_configured.py` |
| OC011 | No blind `--upgrade` — use `--upgrade-package` | `no_blind_upgrade.py` |
| OC012 | No unsafe `curl \| bash` downloads | `no_unsafe_downloads.py` |
| OC014 | No hardcoded configurable values | `no_hardcoded_config.py` |
| OC015 | Research unfamiliar APIs before use | documentation/process rule |
| OC016 | E2E/integration tests for user-visible behavior | testing/process rule |
| OC020 | Failing test before bug fix (TDD). Non-bug work uses SDD (spec before code). | testing/process rule |
| OC-MOCK | Mock external boundaries only | `no_test_mock_abuse.py` |
| OC-ROUTING | AGENTS.md routing table consistency | `routing_consistency.py` |
| OC-REGISTRY | AGENTS.md rules table sync with filesystem | `registry_sync.py` |
| OC-SKILL-CHECK | Skill description quality and trigger language | `skill_descriptions.py` |

Each implemented rule lives in `opencode_lint/rules/`. See the docstring in each file for details.
