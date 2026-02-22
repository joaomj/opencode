# opencode-config

Personal [opencode](https://opencode.ai) configuration with development guidelines, custom agents, and skills for enhanced AI-assisted development.

## Overview

This configuration enhances opencode with:

- **Development Guidelines** - Best practices for Python, Docker, ML, and general workflows
- **Dual-agent code review** - Two independent AI reviewers cross-check code changes
- **Documentation maintenance** - Automated detection of outdated documentation
- **Pre-commit hooks** - Quality checks for any project

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
├── AGENTS.md              # Main guidelines and rules
├── opencode.json          # Configuration (agents, permissions)
├── instructions/          # Domain-specific guidelines
│   ├── python/            # Python best practices
│   ├── docker/            # Docker security patterns
│   ├── ml/                # Machine learning methodology
│   ├── workflow/          # Development workflows
│   └── tools/             # External tool usage
├── skills/                # Reusable skill definitions
│   ├── code-review-expert/
│   └── doc-maintenance/
├── agents/                # Subagent configurations
└── commands/              # Custom commands
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
| `code-review-expert` | Checklists for SOLID principles, security, performance, code quality |
| `doc-maintenance` | Guidelines for identifying and pruning outdated documentation |

## Pre-Commit Hooks

Install quality checks in any project:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash
```

Checks include:
- **Secrets** - Detects hardcoded secrets
- **File length** - Limits Python files to 300 lines
- **Formatting** - Ensures proper code style
- **Dockerfile** - Validates Dockerfile best practices
- **Branch protection** - Prevents direct commits to main/master

## Development Guidelines

The `instructions/` directory contains domain-specific guidelines:

| Domain | Topics |
|--------|--------|
| Python | Type hints, error handling, logging, testing |
| Docker | Security best practices, compose templates |
| Machine Learning | Data splitting, leakage prevention, evaluation |
| Workflow | Planning, task management, PR descriptions |
| Tools | External documentation APIs |

## Multi-Machine Setup

Clone to `~/.config/opencode/` on each machine for consistent configuration. Update with:

```bash
cd ~/.config/opencode && git pull
```

## License

MIT - see [LICENSE](LICENSE) for details.
