# opencode-config

Personal [opencode](https://opencode.ai) configuration with development guidelines, custom agents, and skills for enhanced AI-assisted development.

## Overview

This configuration enhances opencode with:

- **Skill-based architecture** - Domain-specific skills loaded on-demand for Python, Docker, ML, workflows, code review, and more
- **Decision-index approach** - AGENTS.md provides deterministic skill triggers
- **Dual-agent code review** - Two independent AI reviewers cross-check code changes
- **Documentation maintenance** - Automated detection of outdated documentation
- **Optional pre-commit hooks** - Quality checks for any project (user must opt-in)

## Prerequisites

- [opencode CLI](https://opencode.ai) installed
- API keys for your preferred model providers
- `websearch` support via OpenCode provider or Exa (`OPENCODE_ENABLE_EXA=1`)

## Installation

```bash
# Clone to opencode config directory
git clone https://github.com/joaomj/opencode.git ~/.config/opencode
```

## Quick Start

Once installed, the following commands are available:

- `/review` - Dual-agent code review with severity classification
- `/update-docs` - Identify and remove obsolete documentation
- `/standup-prep` - Generate daily standup summaries from git activity

## Pre-Commit Hooks (Optional)

Install quality checks in any project:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash
```

The installer will ask for confirmation before proceeding.

## Technical Documentation

For detailed information about skills, commands, development guidelines, and architecture decisions, see [tech-context.md](tech-context.md).

## Multi-Machine Setup

Clone to `~/.config/opencode/` on each machine for consistent configuration. Update with:

```bash
cd ~/.config/opencode && git pull
```

## Disclaimer

This is not built by the [OpenCode](https://github.com/anomalyco/opencode) team and is not affiliated with them in any way.

## License

MIT - see [LICENSE](LICENSE) for details.
