# AGENTS.md

## Core Principles

- **intent-driven**: Match user intent, not exact phrases — act on meaning, not keyword triggers.
- **gdd-first**: Bug fixes require failing regression test that reproduces the bug.

## Critical Security

- **NEVER** read, print, echo, or inspect the contents of any `.env` file. Use environment variable loading mechanisms only.
- **NEVER** run privileged containers.

## Routing

| Intent | Action |
|--------|--------|
| Python/ML coding | `@ml-engineer` |
| Frontend testing | `@frontend-tester` (when frontend assets detected) |
| Research libraries/APIs | `@researcher` (auto-triggered on unfamiliar topics) |
| Code review | `@code-reviewer` |
| Simplify code | `@simplifier` |
| Doc cleanup | `@doc-maintainer` |
| CI/CD | Load `github-cicd-lite` or `docker-best-practices` |
| Pull request | Load `create-pull-request` |
| Architecture diagram | Load `architecture-diagram` or `c4-diagram` |
| Browser debugging | Load `brave-devtools` |
| Planning | Use `/plan` |

## Workflow

| Condition | Action |
|-----------|--------|
| Code changes affect public API | Suggest documentation updates |
| Phase gate passed | Ask to commit |
| User requests commit | Commit changes (no push unless requested) |
| Dependency upgrade | Use `--upgrade-package`, not blind `--upgrade` |
| CI setup | Use `--locked` install to enforce lockfile integrity |