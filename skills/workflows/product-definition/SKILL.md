---
name: product-definition
description: Turn a product idea into an approved PRD, behavior specification, optional ADRs, and optional tickets before implementation planning. Use for substantial product work that needs a waterfall delivery route.
---

# Product Definition

Use this workflow before implementation planning when the work needs product
clarity. Small, clear, reversible changes can skip it.

## Artifact Boundaries

- **Brainstorm** clarifies the problem, users, constraints, and decision.
- **PRD** defines why the work matters, who it serves, and what success means.
- **Specification** defines observable behavior, rules, failures, and scope.
- **ADR** records only a hard-to-reverse technical choice with real alternatives.
- **Ticket** carries product context, acceptance criteria, and definition of done.
- **Implementation plan** defines repository paths, edits, and verification gates.

Do not copy the same decision into more than one artifact. Link to the owning
artifact instead.

## Ordered Steps

1. Clarify the product problem through focused questions and concrete scenarios.
2. Inspect current behavior, relevant code, documentation, and existing decisions.
3. Draft a PRD when the work has meaningful product scope.
4. Present the PRD and obtain approval before treating it as intent.
5. Draft a behavior specification from the approved product intent.
6. Present the specification and obtain approval before planning implementation.
7. Record an ADR only when the architecture decision meets all three conditions:
   - It is hard to reverse.
   - It is surprising without its context.
   - Real alternatives and trade-offs were assessed.
8. Ask whether tickets are useful for this work. Do not require tickets for a
   personal project when the user does not need them.
9. If the user wants tickets, draft product-focused ticket text with acceptance
   criteria and a definition of done. Ask for approval before publishing.
10. Check for an available Jira skill or MCP before publishing tickets. If no
    adapter exists, offer one root `TICKETS.md` file instead.
11. Hand the approved artifacts to `implementation-planning`.

## Ticket Publishing

Do not invent a Jira integration. Inspect the available skill and MCP catalog.
Use the approved adapter for ticket creation only after the user approves the
ticket drafts. If no adapter is available, write `TICKETS.md` only after the
user approves that fallback artifact.

## Completion

Return the approved PRD and specification, any accepted ADR references, the
ticket decision and result, unresolved questions, and the handoff to planning.

Do not create code, a branch, a commit, or a pull request in this workflow.
