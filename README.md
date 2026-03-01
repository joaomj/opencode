# opencode-config

Personal [opencode](https://opencode.ai) configuration with development guidelines, custom agents, and skills for enhanced AI-assisted development.

## Overview

This configuration enhances opencode with:

- **Skill-based architecture** - 8 domain-specific skills loaded on-demand for Python, Docker, ML, and workflows
- **Decision-index approach** - AGENTS.md provides deterministic skill triggers (following Vercel's pattern)
- **Dual-agent code review** - Two independent AI reviewers cross-check code changes
- **Documentation maintenance** - Automated detection of outdated documentation
- **Lean GitHub CI skill** - Fast, secure CI pipelines for small Python repos
- **Optional pre-commit hooks** - Quality checks for any project (user must opt-in)

## Prerequisites

- [opencode CLI](https://opencode.ai) installed
- API keys for your preferred model providers

## Installation

```bash
# Clone to opencode config directory
git clone https://github.com/joaomj/opencode.git ~/.config/opencode
```

## Project Structure

```
~/.config/opencode/
├── AGENTS.md              # Decision-index with skill triggers (v4.0)
├── opencode.json          # Configuration (agents, permissions)
├── skills/                # Domain-specific skills (load on-demand)
│   ├── python-best-practices/      # Type hints, error handling, testing, security
│   ├── docker-best-practices/      # Dockerfile, Compose, security, networking
│   ├── ml-best-practices/           # CRISP-DM, data quality, evaluation, MLflow
│   ├── workflow-development/          # TDD, document ordering, approval gates
│   ├── code-review-expert/          # Dual-agent code review
│   ├── doc-maintenance/             # Documentation pruning
│   ├── github-cicd-lite/            # Lean GitHub CI pipelines
│   └── firecrawl-web-scraper/       # Web scraping with Firecrawl
├── agents/                # Subagent configurations
├── commands/              # Custom commands
└── setup-hooks.sh        # Pre-commit hooks installer (optional)
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
| `firecrawl-web-scraper` | Web scraping to save blog posts, articles, Arxiv papers |

## Pre-Commit Hooks (Optional)

Install quality checks in any project:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash
```

**Important:** Pre-commit hooks are optional. The installer will ask for confirmation before proceeding.

Checks include:
- **Secrets** - Detects hardcoded secrets
- **File length** - Limits Python files to 300 lines
- **Formatting** - Ensures proper code style (ruff)
- **Dockerfile** - Validates Dockerfile best practices (hadolint)
- **Branch protection** - Prevents direct commits to main/master

## Development Guidelines

The `skills/` directory contains domain-specific skills loaded on-demand based on deterministic triggers in `AGENTS.md`:

| Domain | Skill | Topics |
|--------|-------|--------|
| Python | `python-best-practices` | Type hints, error handling, Pydantic patterns, testing (pytest), logging, Ruff rules, security, dependency management (pdm) |
| Docker | `docker-best-practices` | Dockerfile patterns (non-root USER), Docker Compose (read_only), runtime security, network isolation, secrets handling |
| Machine Learning | `ml-best-practices` | CRISP-DM phases with STAR documentation, data quality (test set ONCE), preprocessing in Pipeline, evaluation metrics, MLflow tracking |
| Workflow | `workflow-development` | TDD (tests before implementation), chronological document order (PRD→Design→Specs→Plan), approval gates, todo tracking |

**Key Features:**
- **Retrieval-led reasoning** - Skills loaded based on explicit triggers, not model decisions
- **Decision-index format** - AGENTS.md provides clear IF-THEN rules for skill loading (following Vercel's pattern)
- **Compressed context** - AGENTS.md reduced to 177 lines with pipe-delimited tables for fast scanning
- **Optional hooks** - Pre-commit hooks require user confirmation before installation

## Multi-Machine Setup

Clone to `~/.config/opencode/` on each machine for consistent configuration. Update with:

```bash
cd ~/.config/opencode && git pull
```

## License

MIT - see [LICENSE](LICENSE) for details.
