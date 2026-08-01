---
description: Create an implementation plan from the current repository state
agent: build
---

Create an implementation plan for `$ARGUMENTS`.

This command is the planning writer for the planned route. It may create the
required branch and plan file, but it must not implement code or create tickets.

1. Explain the strategy in plain terms for a product manager.
2. Inspect the current repository before making claims. Use deployed or remote behavior, local code, updated documentation, and Jira tickets in that evidence order.
3. Confirm that the desired behavior is clear enough for a plan. If it is not, stop and report the discovery work required.
4. Identify the default branch and create a new branch from `origin/<default-branch>` using the repository naming convention. Do not rebase or merge.
5. Write only `PLAN-<ticket-id>.md` at the repository root. Ask for a ticket ID if `$ARGUMENTS` does not provide one.
6. Back every step with current files, symbols, and behavior. Mark unknown areas as discovery work.
7. Include acceptance criteria, risks, dependencies, open decisions, out-of-scope work, and verification for every step.
8. Recommend one established coding pattern for each task. Explain its rationale and trade-offs, and name at least one alternative.
9. Verify each step before moving to the next one. Stop if a verification fails.
10. Do not implement code, create tickets, or modify files other than the plan.
