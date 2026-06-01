# OpenCode Config

Personal configuration for [OpenCode](https://opencode.ai) — agents, skills, commands, and a custom linter.

> **Disclaimer:** Not affiliated with OpenCode. Personal configuration using OpenCode as a platform.

## Setup

1. **Clone the repository:**

   ```bash
   git clone git@github.com:joaomj/skills.git ~/.config/opencode
   ```

2. **Install the custom linter (optional, used by AGENTS.md rules):**

   ```bash
   pip install -e ~/.config/opencode/opencode_lint
   ```

3. **Configure OpenCode:**

   Copy the example config and edit as needed (change models, providers etc):

   ```bash
   cp ~/.config/opencode/opencode.json ~/.config/opencode.json
   ```

   The config sets up provider models, permission rules, and agent settings.

## Updating

```bash
cd ~/.config/opencode && git pull
```

## What's Inside

- **18 skills** — architecture diagrams, browser inspection, coding standards, docs, Docker, e2e testing, issue writing, Jira, ML, Notion, research, simplification, and more
- **3 agents** — `code-reviewer`, `ml-engineer`, `swe-engineer`
- **3 commands** — `commit`, `standup-prep`, `update-opencode`
- **Custom linter** (`opencode-lint`) — enforces AGENTS.md rules (OC001–OC014 + OC-MOCK)

## License

[MIT](LICENSE)
