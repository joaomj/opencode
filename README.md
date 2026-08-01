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

Restart OpenCode after changing `opencode.jsonc`, plugins, commands, or skills.

## Delivery Workflow

Use the smallest route that matches the change risk:

```text
clear and small: inspect -> implement -> verify
complex implementation: ticket -> plan -> approve -> implement -> review -> PR
unclear behavior: discover -> specify -> decide -> plan -> implement -> review -> PR
confirmed bug: reproduce -> regression test -> diagnose -> fix -> review -> PR
```

Use `/specification` only when behavior needs more detail than the ticket. Use
`/implementation-plan` when repository-specific implementation steps are needed.
Use `/implement` only with approved work. Use `/code-review` before a PR. Use
`/create-pr` only after review and branch verification.

## Decision Records

- Tickets record problems and desired user-visible outcomes.
- Specifications record required behavior and scope.
- `PLAN-<ticket-id>.md` records repository-specific implementation steps.
- `docs/adr/` records hard-to-reverse architecture decisions.
- `tech-context.md` records the current system and links to ADRs.
- Pull requests record delivered changes and verification evidence.

## Linter

Run the linter and its focused tests through `uv`:

```bash
uv run --project opencode_lint pytest opencode_lint/tests -q
uv run --no-project python -m opencode_lint.cli
```

## License

[MIT](LICENSE)
