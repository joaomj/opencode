---
description: Create an implementation plan from the current repository state
agent: plan
---

Create an implementation plan for `$ARGUMENTS`.

1. Explain the strategy in plain terms for a product manager.
2. Inspect the current repository before making claims. Use deployed or remote behavior, local code, updated documentation, and Jira tickets in that evidence order.
3. Identify the default branch and create a new branch from `origin/<default-branch>` using the repository naming convention. Do not rebase or merge.
4. Write only `PLAN-<ticket-id>.md` at the repository root. Ask for a ticket ID if `$ARGUMENTS` does not provide one.
5. Back every step with current files, symbols, and behavior. Mark unknown areas as discovery work.
6. Include acceptance criteria, risks, dependencies, open decisions, out-of-scope work, and verification for every step.
7. Recommend one established coding pattern for each task. Explain its rationale and trade-offs, and name at least one alternative.
8. Stop if a verification fails. Do not implement code, create tickets, or modify files other than the plan.
