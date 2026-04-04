# AGENTS.md - Local Configuration

## Hierarchy

Remote AGENTS.md at `https://raw.githubusercontent.com/joaomj/skills/main/AGENTS.md` is the primary source of truth. This file contains local overrides and additions only. Where conflicts exist, this file takes precedence.

---

## OVERRIDES

| Remote Rule | Local Override | Reason |
|-------------|---------------|--------|
| Pre-commit hooks (enforced) | Optional. Install only on explicit request: "Install pre-commit hooks" or `/setup-hooks` | Lower friction |

### Additional Core Principles

| Principle | Description |
|-----------|-------------|
| sdd-first | Spec-Driven Design: specs before tests, tests before implementation. Bug fixes require spec + regression test. |
| no-hardcoding | All configurable values in config module using pydantic-settings. |
| no-test-skipping | Never use `# noqa`, `@pytest.mark.skip`, `@pytest.mark.xfail` in tests. Fix root cause. |

---

## TRIGGER TABLE

| User Says | Action |
|-----------|--------|
| "review" / "code review" / "review my changes" / "check my code" / "/review" / "PR review" | `@code-reviewer` |
| "update docs" / "prune docs" / "clean up docs" / "update documentation" | `@doc-maintainer` |
| "write a cicd pipeline" / "github actions pipeline" / "create github workflow" | `/skill github-cicd-lite` |
| "create PR" / "open pull request" / "open a PR" / "create pull request" / "make a PR" / "/pr" | `/skill create-pull-request` |
| "scrape this url/website/article" | `/skill firecrawl-web-scraper` |
| "implement" / "build feature" / "create endpoint" / "add feature" | Run `/plan` |
| "/plan" / "create a plan" | Run `/plan` |
| "fix bug" / "fix this bug" | Block: "Write regression test that reproduces bug first" |
| "standup" / "/standup" / "daily activity" | Run `/standup-prep` |
| "jira" / "fetch jira issue" | `/skill jira-issues` |
| "simplify code" / "simplify this" | `@simplifier` |
| "deslop" / "clean up AI code" / "remove slop" | Run `/deslop` |

### Automatic Triggers

| Condition | Action |
|-----------|--------|
| AFTER any code change | Run `/deslop` then ASK: "Update documentation?" |
| See `import X` (X not stdlib) | ASK: "Fetch up-to-date docs for X?" -> `/skill context7-docs` |
| Context7 fetch fails | Ask: "Proceed without docs?" |
| Task completed | ASK: "Update daily activity log?" |
| Phase gate passed | Run `/commit` |
| User says "commit" / "/commit" | Run `/commit` |

### File Pattern Triggers (BEFORE reading file)

| File Pattern | Action |
|-------------|--------|
| `Dockerfile` / `Dockerfile.*` / `docker-compose*.yml` | ASK: "Load Docker best practices?" |
| `train.py` / `model.py` / `pipeline.py` / `features.py` | ASK: "Load ML best practices?" |
| `*.env.example` | STOP - see env-files rule |
| `setup.py` / `pyproject.toml` | ASK: "Load Python best practices?" |

### Import Statement Triggers (WHILE reading file)

| Import Statement | Action |
|-----------------|--------|
| `import pandas` / `import numpy` / `from sklearn` / `import torch` | ASK: "Load ML best practices?" |
| `from pydantic` / `import pytest` | ASK: "Load Python best practices?" |
| `from fastapi` / `from flask` / `from django` | ASK: "Load Python best practices + fetch docs?" |

---

## NON-NEGOTIABLE RULES

| Rule ID | Domain | Rule |
|---------|--------|------|
| OC001 | Type Safety | No raw dicts for API schemas - use Pydantic models |
| OC002 | Security | Never view .env content (use .env.example for schema) |
| OC003 | Security | No privileged containers |
| OC004 | Grep-ability | Absolute imports preferred over relative |
| OC005 | Type Safety | Strict type hints for all functions |
| OC006 | Process | SDD: specs before tests, tests before implementation |
| OC007 | Quality | 80% test coverage minimum |
| OC008 | Test Integrity | Zero `# noqa` or skip in tests - fix root cause |
| OC009 | Supply Chain | Lockfile required and committed |
| OC010 | Supply Chain | Delayed ingestion with 7-day buffer recommended |

---

## SUBAGENT INDEX

| Subagent | Invoke | Description |
|----------|--------|-------------|
| code-reviewer | `@code-reviewer` | Expert code review with P0-P3 severity |
| simplifier | `@simplifier` | Apply project standards to simplify code |
| doc-maintainer | `@doc-maintainer` | Update and prune documentation |

## SKILL INDEX

| Domain | Command |
|--------|---------|
| Implementation planning | `/plan` |
| Python development | `/skill python-best-practices` |
| Docker/containerization | `/skill docker-best-practices` |
| Machine learning | `/skill ml-best-practices` |
| GitHub CI/CD | `/skill github-cicd-lite` |
| GitHub PR creation | `/skill create-pull-request` |
| Jira issues | `/skill jira-issues` |
| Web scraping | `/skill firecrawl-web-scraper` |
| Documentation lookup | `/skill context7-docs` |
