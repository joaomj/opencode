# AGENTS.md

## Core Principles

- **intent-driven**: Match user intent, not exact phrases — act on meaning, not keyword triggers.
- **sdd-first**: Spec-Driven Development — user must approve a spec before any code editing.
- **tdd-first**: Test-Driven Development — failing test before implementation. No production code without a failing test first (OC020).
- **docker-first**: Prefer Docker over local installs for development environments. Clean up containers and images after task completion.

## Critical Security

- **NEVER** read, print, echo, or inspect the contents of any `.env` file. Use environment variable loading mechanisms only.
- **NEVER** run privileged containers.

## Coding Standards

Always load the `coding-best-practices` skill when performing any coding activity (writing, modifying, reviewing, or refactoring code in any language). This skill enforces quality, idempotency, error treatment, logging, async safety, and hardcoding avoidance rules.

- **Linter before commit**: Run `ruff check .` before any `git commit`. Block if errors remain.
- **No hardcoded values**: App config, URLs, ports, timeouts, thresholds → centralized config only. OC014 enforces this.
- **Idempotent mutations**: All state changes must be safe to retry (upserts, if-not-exists, dedup keys).

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
| Pull request | Load `create-pull-request` |
| Architecture diagram | Load `architecture-diagram` or `c4-diagram` |
| Browser debugging | Load `browser-readonly` skill and use `browser_cdp.py` for screenshots, DOM, JS eval, console, and network via local Brave/Chromium CDP |
| Docker/containerization | Load `docker-best-practices` skill |
| Planning | Use `/plan` |

## Workflow

| Condition | Action |
|-----------|--------|
| Code changes affect public API | Suggest documentation updates |
| Phase gate passed | Ask to commit |
| User requests commit | Commit changes (no push unless requested) |
| Code staged | Run `ruff check .` first; block commit if errors |
| Dependency upgrade | Use `--upgrade-package`, not blind `--upgrade` |
| CI setup | Use `--locked` install to enforce lockfile integrity |
| Security | Run `pip-audit` on every commit to detect dependency vulnerabilities (supply chain) |
| Review finds P0 or P1 | Block merge (FAIL-CLOSED). Fix and re-review. |
| Docker used | Clean up containers and images after task completion |

## Testing

### E2E/Integration Tests (OC016)

User-visible behavior changes require e2e or integration tests.
Unit tests alone are insufficient for features that affect external interfaces,
APIs, or user workflows.

Load the `e2e-testing` skill when writing or reviewing integration tests.

- Every user-facing change must have at least one e2e/integration test
- E2E tests verify real system behavior, not mocked internals
- Use TestClient (FastAPI/Flask), Playwright, or HTTP requests for integration
- Prefer integration tests over heavy mocking at internal boundaries
- If mocking is required, add `mock-allow-internal: <reason>` marker