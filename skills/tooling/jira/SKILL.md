---
name: jira
description: Create, update, inspect, and comment on Jira work through the Atlassian MCP server. Use when the user mentions Jira, an issue key, a ticket, or Atlassian work.
license: MIT
---

# Jira

Use the configured Atlassian MCP server for Jira work when it is enabled. Do not
use direct HTTP requests or GitHub tools. If the server is disabled, report the
configuration gap instead of claiming that Jira work succeeded.

## Ticket Content

- The agent writes tickets directly.
- Describe the problem, the desired user-visible state, acceptance criteria, constraints, and out-of-scope work.
- Keep file paths, symbols, algorithms, implementation steps, and internal architecture out of tickets.
- Use ASD-STE100 technical English.
- Preserve identifiers, logs, and error messages verbatim when quoting them.

## Description Format

- Write ticket descriptions in Markdown, not Jira wiki format.
- Use ADF only when the tool explicitly requests or accepts ADF.
- Do not infer the MCP input format from Jira Cloud storage format.

## Workflow

1. Search for the issue or project before creating duplicates.
2. Confirm the issue key, project, summary, and requested operation.
3. Apply the smallest change that satisfies the request.
4. Report the issue key and the resulting user-visible state.
5. Surface MCP errors. Do not convert failed operations into success responses.

If the server is enabled and authentication is required, tell the user to run
`opencode mcp auth atlassian` and retry.
