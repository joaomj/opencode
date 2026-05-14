# Opencode Setup

Skills, commands, agents, and git hooks for [OpenCode](https://opencode.ai) — the AI coding assistant that lives in your terminal.

## Quick Start

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/install.sh | bash
```

Customize your setup via `AGENTS.md` (rules + routing) and `opencode.json` (models + permissions).

## What's Inside

- Skills for domain-specific workflows (architecture, CI/CD, issue tracking, docs, ML, Python, PRs, scraping, Docker, browser debugging)
- Slash commands for committing, standup prep, and updating
- Agent personas for Python/ML coding, frontend testing, research, code review, documentation, and simplification
- Git hooks for enforcing code quality
- Config templates with sensible defaults

## Updating

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/install.sh | bash -s -- --update
```

Or run `/update-opencode` from within OpenCode.

## License

MIT
