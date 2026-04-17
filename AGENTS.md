# AGENTS.md - Local Configuration

## Hierarchy

Remote AGENTS.md at `https://raw.githubusercontent.com/joaomj/skills/main/AGENTS.md` is the primary source of truth.
---

## Core Principles

| Principle | Description |
|-----------|-------------|
| sdd-first | Spec-Driven Design: specs before tests, tests before implementation. Bug fixes require spec + regression test. |
| no-hardcoding | All configurable values in config module using pydantic-settings. |
| no-test-skipping | Never use `# noqa`, `@pytest.mark.skip`, `@pytest.mark.xfail` in tests. Fix root cause. |
| intent-driven | Match user intent, not exact phrases. LLMs understand synonyms and indirect requests — act on meaning, not keyword triggers. |

---

## Intent-Driven Agent Routing

When the user's intent matches a category below, invoke the corresponding agent or load the skill. Do not require exact phrase matches.

| Intent Category | Action |
|-----------------|--------|
| Code review / feedback on code quality | `@code-reviewer` |
| Documentation cleanup / accuracy / pruning | `@doc-maintainer` |
| Code simplification / reducing complexity | `@simplifier` |
| CI/CD pipelines / GitHub Actions / workflows | Load `github-cicd-lite` or `docker-best-practices` skill as appropriate |
| Pull request creation | Load `create-pull-request` skill |
| Web scraping / extracting content from URLs | Load `firecrawl-web-scraper` skill |
| Jira issue management | Load `jira-issues` skill |
| Notion search / fetch notion docs / read notion page | Load `notion-reader` skill |
| Planning a feature or implementation | Switch to `@plan` agent (or press Tab to select Plan) |
| Bug fixing | Write a regression test that reproduces the bug before fixing |
| Architecture / infrastructure / system diagram | Load `architecture-diagram` skill |

---

## Context-Aware Skill Loading

Load relevant skills when the context matches, regardless of whether it's a file pattern, import, or conversation topic.

### Domain Skills

| Context | Skill |
|---------|-------|
| Docker / containers / Dockerfile / docker-compose | `docker-best-practices` |
| Machine learning / training / model pipelines / pandas / numpy / sklearn / torch | `ml-best-practices` |
| Python project setup / pydantic / pytest / fastapi / flask / django | `python-best-practices` |
| New or unfamiliar library import (`import X`) | `context7` (fetch up-to-date docs) |
| Notion / notion API / fetch notion content | `notion-reader` |
| Architecture diagram / system diagram / infrastructure visualization | `architecture-diagram` |
| `.env.example` file | STOP — see env-files rule (never read `.env`) |

When a skill fetch fails, ask the user: "Proceed without docs?"

### Skill Loading Protocol

1. Ask the user before loading a skill (unless they directly requested it).
2. Example: when opening a Dockerfile, ask "Load Docker best practices?" before invoking the skill.
3. If the user's request already implies the domain (e.g., "help me write a Dockerfile"), load without asking.

---

## Workflow Triggers

| Condition | Action |
|-----------|--------|
| After code changes that affect public API or user-facing behavior | Suggest documentation updates |
| Phase gate passed | Ask whether to commit |
| User requests commit | Commit changes (no push unless requested) |
| Task completed | Ask: "Update daily activity log?" |

---

## NON-NEGOTIABLE RULES

| Rule ID | Domain | Rule |
|---------|--------|------|
| OC001 | Type Safety | No raw dicts for API schemas — use Pydantic models |
| OC002 | Security | Never view `.env` content (use `.env.example` for schema only) |
| OC003 | Security | No privileged containers |
| OC004 | Grep-ability | Absolute imports preferred over relative |
| OC005 | Type Safety | Strict type hints for all functions |
| OC006 | Process | SDD: specs before tests, tests before implementation |
| OC007 | Quality | 80% test coverage minimum |
| OC008 | Test Integrity | Zero `# noqa` or skip in tests — fix root cause |
| OC009 | Supply Chain | Lockfile required and committed |
| OC010 | Supply Chain | Delayed ingestion with 7-day buffer recommended |

---

## SUBAGENT INDEX

| Subagent | Invoke | Description |
|----------|--------|-------------|
| code-reviewer | `@code-reviewer` | Expert code review with P0-P3 severity |
| simplifier | `@simplifier` | Apply project standards to simplify code |
| doc-maintainer | `@doc-maintainer` | Update and prune documentation |
