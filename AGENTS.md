# AGENTS.md

## Core Principles

- **intent-driven**: Match user intent, not exact phrases — act on meaning, not keyword triggers.
- **gdd-first**: Bug fixes require failing regression test that reproduces the bug.

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
| Python/ML coding | `@ml-engineer` + `coding-best-practices` |
| Frontend testing | `@frontend-tester` (when frontend assets detected) |
| Research libraries/APIs | `@researcher` (auto-triggered on unfamiliar topics) |
| Code review | `@code-reviewer` |
| Simplify code | `@simplifier` |
| Doc cleanup | `@doc-maintainer` |
| CI/CD | Load `github-cicd-lite` or `docker-best-practices` |
| Pull request | Load `create-pull-request` |
| Architecture diagram | Load `architecture-diagram` or `c4-diagram` |
| Browser debugging | Use `chrome-devtools` MCP tools (`list_console_messages`, `list_network_requests`, etc.) |
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