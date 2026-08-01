# OpenCode Config

Personal configuration for [OpenCode](https://opencode.ai).

## Quick Start

```bash
git clone git@github.com:joaomj/opencode.git ~/.config/opencode
uv sync --locked --project ~/.config/opencode/opencode_lint
```

## Atlassian MCP

If the Atlassian MCP block is enabled in `opencode.jsonc`, authenticate it when
Jira work needs access:

```bash
opencode mcp auth atlassian
```

Restart OpenCode after changing `opencode.jsonc`, plugins, commands, or skills.

## Delivery Workflow

See `AGENTS.md` and the `workflow` skill for intent-based routing. Every
substantial request selects one workflow before execution and reports it as
`Selected workflow: <name>`.

Workflow skills define ordered steps, deliverables, allowed side effects, and
completion conditions. Capability skills such as research, testing, and error
handling are invoked by workflows. An exploration or investigation workflow
does not become a plan unless the user explicitly requests that handoff.

Use `/implementation-plan` for repository-specific plans, conversational
`specification` and `implement` skills for approved work, `/write-postmortem`
for medium or high complexity bug fixes, `/code-review` before a PR, and
`/create-pr` only after review and branch verification.

## Agent Improvement

Run `/improve-agent` to audit the global OpenCode setup and session history.
The audit checks for recurring agent friction, overlapping or redundant
instructions, conflicts, stale artifacts, unsafe tools or plugins, and missing
capabilities.

The command is proposal-only. It does not modify skills, commands, plugins,
tools, configuration, or session records.

## Decision Records

See the artifact ownership rules in `AGENTS.md`. Do not duplicate the same
decision across a ticket, specification, plan, ADR, technical context, or PR.

## Linter

Run the linter and its focused tests through `uv`:

```bash
uv run --project opencode_lint pytest opencode_lint/tests -q
uv run --no-project python -m opencode_lint.cli
```

## License

[MIT](LICENSE)
