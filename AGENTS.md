# AGENTS.md

## Core Principles

- **spec-before-code**: User must approve a spec before any code editing (SDD).
  - **test-before-code**: Failing test before implementation. No production code without a failing test first (OC020). Exempted for doc-only changes.
  - **docker-by-default**: Prefer Docker over local installs for development environments. Clean up containers and images after task completion.

## Critical Security

- **NEVER** read, print, echo, inspect, or otherwise access the contents of any `.env` file — not via the Read tool, bash commands (`cat`, `less`, `head`, `tail`, etc.), or scripts (Python, bash, or any other language that reads the file). Use environment variable loading mechanisms only (`dotenv.load_dotenv()`, `os.getenv()`, etc.).
- **NEVER** run privileged containers.

## Coding Standards

Always load the `coding-best-practices` skill when performing any coding activity (writing, modifying, reviewing, or refactoring code in any language). This skill enforces quality, idempotency, error treatment, logging, async safety, and hardcoding avoidance rules.

- **Linter before commit**: Run `ruff check .` before any `git commit` (only when Python files are involved). Block if errors remain.
- **No hardcoded values**: App config, URLs, ports, timeouts, thresholds → centralized config only. OC014 enforces this.
- **Idempotent mutations**: All state changes must be safe to retry (upserts, if-not-exists, dedup keys).

## Rules

Enforced by the `opencode-lint` linter (`opencode_lint/`). Run with `opencode-lint` or via the CLI.

| ID | Rule | File |
|----|------|------|
| OC001 | No raw dicts for API schemas | `no_raw_dict_api.py` |
| OC002 | Never inspect `.env` values | `no_env_file_access.py` |
| OC003 | No privileged containers | `no_privileged_containers.py` |
| OC004 | Absolute imports preferred | `absolute_imports.py` |
| OC005 | Strict type hints required | `strict_type_hints.py` |
| OC009 | Lockfile must exist and be committed | `lockfile_required.py` |
| OC010 | `exclude-newer` with 7-day buffer in pyproject.toml | `exclude_newer_configured.py` |
| OC011 | No blind `--upgrade` — use `--upgrade-package` | `no_blind_upgrade.py` |
| OC012 | No unsafe `curl \| bash` downloads | `no_unsafe_downloads.py` |
| OC014 | No hardcoded configurable values | `no_hardcoded_config.py` |
| OC-MOCK | Mock external boundaries only | `no_test_mock_abuse.py` |

Each rule lives in `opencode_lint/rules/`. See the docstring in each file for details.

## Routing

| Intent | Action |
|--------|--------|
| Any coding activity | Load `coding-best-practices` skill |
| SWE: feature, bug fix, refactor, AI feature | `@swe-engineer` + `coding-best-practices` |
| ML/data: analysis, experiment, model training | `@ml-engineer` + `coding-best-practices` |
| Jira ticket (any domain) | Load `jira-issues` skill, classify intent, then route to `@swe-engineer` or `@ml-engineer` |
| Code review | `@code-reviewer` |
| Research libraries/APIs | Load `research` skill |
| Simplify code | Load `simplify` skill (only on explicit user request) |
| Doc cleanup | Load `doc-maintenance` skill |
| Write or record an issue | Load `issue-writing` skill, create `docs/issues/<slug>.md` |
| E2E/integration testing | Load `e2e-testing` skill |
| CI/CD | Load `github-cicd-lite` or `docker-best-practices` |
| Architecture diagram | Load `architecture-diagram` or `c4-diagram` |
| Browser debugging | Load `browser-readonly` skill and use `browser_cdp.py` for screenshots, DOM, JS eval, console, and network via local Brave/Chromium CDP |
| Docker/containerization | Load `docker-best-practices` skill |
| dbt CLI | Load `dbt-cli` skill |
| Planning | Use `/plan` |

## Workflow

| Condition | Action |
|-----------|--------|
| Code changes affect public API | Suggest documentation updates |
| Phase gate passed | Ask to commit directly to `main` |
| User requests commit | Commit changes and push to `main` |
| User requests release | Create a semver tag (`git tag -a v<major>.<minor>.<patch>`) and push tags (`git push origin --tags`) |
| Review finds P0 or P1 | Block merge (FAIL-CLOSED). Fix and re-review. |

## Testing

E2E and integration testing patterns are defined in the `e2e-testing` skill.
