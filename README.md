# OpenCode Config

Personal [OpenCode](https://opencode.ai) configuration: skill-tilted workflows, commands, model tiers, and a custom linter.

## Quick Start

```bash
git clone git@github.com:joaomj/skills.git ~/.config/opencode
pip install -e ~/.config/opencode/opencode_lint
```

Edit `~/.config/opencode/opencode.json` for your provider and model choices, then restart OpenCode.

## What's Inside

- **Skills** — Domain-specific procedures for coding, architecture, docs, research, diagrams, Jira, Docker, ML, and more. See [`AGENTS.md`](AGENTS.md) for the full routing table.
- **Commands** — `/commit` and `/review` for repeatable workflows.
- **Linter** — `opencode-lint` enforces rules from `AGENTS.md` (env access, Docker safety, typing, hardcoded config, etc.).

## License

[MIT](LICENSE)
