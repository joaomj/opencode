# opencode-config

Personal [opencode](https://opencode.ai) configuration with development guidelines, custom agents, and skills for enhanced AI-assisted development.

## Overview

This configuration enhances opencode with:

- **Skill-based architecture** - 10 domain-specific skills loaded on-demand for Python, Docker, ML, workflows, daily standups, and code simplification
- **Decision-index approach** - AGENTS.md provides deterministic skill triggers (following Vercel's pattern)
- **Dual-agent code review** - Two independent AI reviewers cross-check code changes
- **Documentation maintenance** - Automated detection of outdated documentation
- **Lean GitHub CI skill** - Fast, secure CI pipelines for small Python repos
- **Optional pre-commit hooks** - Quality checks for any project (user must opt-in)
- **Anti-mock-abuse guardrail** - Optional hook flags internal/mock-heavy test patterns

## Prerequisites

- [opencode CLI](https://opencode.ai) installed
- API keys for your preferred model providers
- `websearch` support via OpenCode provider or Exa (`OPENCODE_ENABLE_EXA=1`)

## Installation

```bash
# Clone to opencode config directory
git clone https://github.com/joaomj/opencode.git ~/.config/opencode
```

## Commands

### `/review`

Performs dual-agent code review with severity classification (P0-P3).

```bash
/review                    # Review current changes
/review from X to Y        # Review specific branch range
```

Two independent reviewers analyze the same code and findings are consolidated into a review report.

### `/update-docs`

Identifies and removes obsolete documentation content.

```bash
/update-docs
```

### `/standup-prep`

Generates daily standup summaries from git activity for team meetings.

```bash
/standup-prep              # Generate standup summary for yesterday
```

Analyzes your git activity (GitHub CLI or local git), detects potential blockers (failed CI, stale PRs, TODOs), and creates a markdown report at `docs/activity-log/activities-YYYY-MM-DD.md`.

## Skills

| Skill | Purpose |
|-------|---------|
| `python-best-practices` | Type hints, error handling, Pydantic patterns, testing, logging, security, dependency management |
| `docker-best-practices` | Dockerfile patterns, Docker Compose, runtime security, network isolation, secrets handling |
| `ml-best-practices` | CRISP-DM phases, data quality (test set rules), evaluation metrics, MLflow tracking |
| `workflow-development` | TDD-driven development, chronological document order (PRD→Design→Specs→Plan), approval gates |
| `code-review-expert` | Dual-agent code review with P0-P3 severity classification |
| `doc-maintenance` | Guidelines for identifying and pruning outdated documentation |
| `github-cicd-lite` | Lean GitHub Actions CI pattern (Python-first, speed + security, deploy optional) |
| `firecrawl-web-scraper` | Single-URL web scraping with dynamic-page actions and structured JSON output |
| `standup-prep` | Generate daily standup summaries from git activity |
| `code-simplifier` | Pre-commit code simplification with project standards enforcement |
| `jira-issues` | Search assigned Jira issues and update status or description |

## Pre-Commit Hooks (Optional)

Install quality checks in any project:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash
```

**Important:** Pre-commit hooks are optional. The installer will ask for confirmation before proceeding.

Checks include:
- **Secrets** - Detects hardcoded secrets
- **File length** - Limits Python files to 300 lines
- **Test mock policy** - Flags internal/mock-heavy test patterns unless justified
- **Formatting** - Ensures proper code style (ruff)
- **Dockerfile** - Validates Dockerfile best practices (hadolint)
- **Branch protection** - Prevents direct commits to main/master

Mock policy customization:
- Add `.test-mock-external-allowlist` in your repo to allow external module prefixes (one per line)
- Start from `.test-mock-external-allowlist.example` for Python-heavy repos
- Use `mock-allow-internal: <reason>` only for rare exceptions

## Development Guidelines

The `skills/` directory contains domain-specific skills loaded on-demand based on deterministic triggers in `AGENTS.md`:

| Domain | Skill | Topics |
|--------|-------|--------|
| Python | `python-best-practices` | Type hints, error handling, Pydantic patterns, testing (pytest), logging, Ruff rules, security, dependency management (pdm) |
| Docker | `docker-best-practices` | Dockerfile patterns (non-root USER), Docker Compose (read_only), runtime security, network isolation, secrets handling |
| Machine Learning | `ml-best-practices` | CRISP-DM phases with STAR documentation, data quality (test set ONCE), preprocessing in Pipeline, evaluation metrics, MLflow tracking |
| Workflow | `workflow-development` | Test-first where it fits (verify-first always), chronological document order (PRD→Design→Specs→Plan), approval gates, todo tracking |
| Standup | `standup-prep` | Daily standup summaries from git activity, blocker detection, markdown report generation |
| Code Quality | `code-simplifier` | Pre-commit simplification with type hints, no raw dicts, explicit code enforcement |

**Key Features:**
- **Retrieval-led reasoning** - Skills loaded based on explicit triggers, not model decisions
- **Decision-index format** - AGENTS.md provides clear IF-THEN rules for skill loading (following Vercel's pattern)
- **Compressed context** - AGENTS.md uses pipe-delimited tables for fast scanning and deterministic routing
- **Optional hooks** - Pre-commit hooks require user confirmation before installation

## Multi-Machine Setup

Clone to `~/.config/opencode/` on each machine for consistent configuration. Update with:

```bash
cd ~/.config/opencode && git pull
```

## Disclaimer
This is not built by the [OpenCode](https://github.com/anomalyco/opencode) team and is not affiliated with them in any way.

## License

MIT - see [LICENSE](LICENSE) for details.
