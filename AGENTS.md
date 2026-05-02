# AGENTS.md - Local Configuration

Remote AGENTS.md at `https://raw.githubusercontent.com/joaomj/skills/main/AGENTS.md` is primary source of truth.

## Core Principles

| Principle | Description |
|-----------|-------------|
| gdd-first | Bug fixes require failing test that reproduces the bug. |
| no-hardcoding | All configurable values in config module using pydantic-settings. |
| no-test-skipping | Never use `# noqa`, `@pytest.mark.skip`, `@pytest.mark.xfail` in tests. Fix root cause. |
| intent-driven | Match user intent, not exact phrases — act on meaning, not keyword triggers. |

## Routing

| Intent | Action |
|--------|--------|
| Code review | `@code-reviewer` |
| Doc cleanup | `@doc-maintainer` |
| Simplify code | `@simplifier` |
| CI/CD | Load `github-cicd-lite` or `docker-best-practices` |
| Pull request | Load `create-pull-request` |
| Web scraping | Load `firecrawl-web-scraper` |
| Jira issues | Load `jira-issues` |
| Notion docs | Load `notion-reader` |
| ML pipelines | Load `ml-best-practices` |
| Python project | Load `python-best-practices` |
| Architecture diagram | Load `architecture-diagram` or `c4-diagram` |
| Unfamiliar library | Load `context7` |
| Planning | Use `/plan` |
| Bug fix | Write regression test before fixing |

## Workflow

| Condition | Action |
|-----------|--------|
| Code changes affect public API | Suggest documentation updates |
| Phase gate passed | Ask to commit |
| User requests commit | Commit changes (no push unless requested) |
| Dependency upgrade | Use `--upgrade-package`, not blind `--upgrade` |
| CI setup | Use `--locked` install to enforce lockfile integrity |

## Rules

| ID | Domain | Rule |
|----|--------|------|
| OC001 | Type Safety | No raw dicts for API schemas — use Pydantic models |
| OC002 | Security | Don't read/print `.env` values. Scripts may use `.env` via loading. |
| OC003 | Security | No privileged containers |
| OC004 | Grep-ability | Absolute imports preferred over relative |
| OC005 | Type Safety | Strict type hints for all functions |
| OC006 | Process | GDD: define success criteria before implementation |
| OC007 | Quality | 80% test coverage minimum |
| OC008 | Test Integrity | Zero `# noqa` or skip in tests — fix root cause |
| OC009 | Supply Chain | Lockfile required and committed |
| OC010 | Supply Chain | `exclude-newer` with 7-day buffer required in `pyproject.toml` or env |
| OC011 | Supply Chain | CI must enforce lockfile integrity with `--locked` |
| OC012 | Supply Chain | No blind `--upgrade` — use targeted `--upgrade-package` only |