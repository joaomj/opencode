# opencode-config

Personal [opencode](https://opencode.ai) configuration with development guidelines and custom agents for enhanced AI-assisted development.

## Overview

This configuration keeps opencode focused on a few core ideas:

- A hierarchical config model where local `AGENTS.md` overrides remote defaults
- Clear development rules for safer, more consistent AI-assisted changes
- Lightweight optional tooling for validation and repo hygiene

## Prerequisites

- [opencode CLI](https://opencode.ai) installed
- API keys for your preferred model providers
- `websearch` support via OpenCode provider or Exa (`OPENCODE_ENABLE_EXA=1`)

## Installation

```bash
# Clone to opencode config directory
git clone https://github.com/joaomj/opencode.git ~/.config/opencode
```

## Configuration Note

`opencode.json` includes opinionated model and provider settings, including a small model, provider-specific limits, and a fast read-only `explore` agent pinned to `openai/gpt-5.4-mini`. They work in my setup, but other users may need to adjust them if they do not have the same API keys, subscriptions, or model access.

## Pre-Commit Hooks (Optional)

Install quality checks in any project:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/opencode/master/setup-hooks.sh | bash
```

The installer will ask for confirmation before proceeding.

## Technical Documentation

For detailed architecture and workflow notes, see [tech-context.md](tech-context.md).

## Multi-Machine Setup

Clone to `~/.config/opencode/` on each machine for consistent configuration. Update with:

```bash
cd ~/.config/opencode && git pull
```

## Disclaimer

This is not built by the [OpenCode](https://github.com/anomalyco/opencode) team and is not affiliated with them in any way.

## License

MIT - see [LICENSE](LICENSE) for details.
