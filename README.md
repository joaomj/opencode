# OpenCode Skills

Skills, commands, and agents for [OpenCode](https://opencode.ai).

## Install

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/install.sh | bash
```

## What's Included

| Type | Count | Examples |
|------|-------|----------|
| Skills | 12 | architecture diagrams, CI/CD, Jira, Notion, ML |
| Commands | 6 | `/commit`, `/plan`, `/review`, `/deslop` |
| Agents | 3 | `@code-reviewer`, `@doc-maintainer`, `@simplifier` |

## After Install

- `AGENTS.md` — customize rules and routing for your project
- `opencode.json` — add your model providers and API keys

## Update

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/install.sh | bash -s -- --update
```

## Docs

Each component is self-documenting — read the `.md` files in `skills/`, `commands/`, and `agents/`.

## License

MIT