# OpenCode Config

Personal configuration for [OpenCode](https://opencode.ai).

## Quick Start

```bash
git clone git@github.com:joaomj/opencode.git ~/.config/opencode
uv sync --locked --project ~/.config/opencode/opencode_lint
```

## Atlassian MCP

Authenticate the configured Jira server when Jira work needs access:

```bash
opencode mcp auth atlassian
```

Restart OpenCode after changing `opencode.json`, plugins, commands, or skills.

## Linter

Run the linter and its focused tests through `uv`:

```bash
uv run --project opencode_lint pytest opencode_lint/tests -q
uv run --no-project python -m opencode_lint.cli
```

## License

[MIT](LICENSE)
