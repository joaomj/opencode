---
description: Create an implementation plan from the current repository state
---

Create an implementation plan for `$ARGUMENTS` using the
`implementation-planning` workflow.

This command is an explicit workflow selector. Do not use it for exploration,
research, specification, architecture discussion, or implementation.

1. Explain the strategy in plain terms for a product manager, including what will and will not be changed.
2. Inspect the current repository before making claims. Use deployed or remote behavior, local code, updated documentation, and Jira tickets in that evidence order.
3. Confirm that the desired behavior is clear enough for a plan. If it is not, stop and report the discovery work required.
4. A ticket ID is optional. Use one if `$ARGUMENTS` provides it, but do not ask for one just to continue.
5. Back every step with current files, symbols, and behavior. Mark unknown areas as discovery work.
6. Include acceptance criteria, risks, dependencies, open decisions, out-of-scope work, and verification for every step.
7. Recommend one established coding pattern for each task. Explain its rationale and trade-offs, and name at least one alternative.
8. Verify each step before moving to the next one. Stop if a verification fails.
9. Present the complete plan in the conversation and ask the user whether they approve it. Do not create a branch or write a file before the user approves the plan.
10. After plan approval, ask separately whether the user wants a planning branch. Create a branch from `origin/<default-branch>` using the repository naming convention only if the user agrees. Do not rebase or merge.
11. After plan approval, ask separately whether the user wants the plan written to a Markdown file. If the user agrees, choose a suitable filename: use `PLAN-<ticket-id>.md` when a ticket ID exists, otherwise ask for or suggest a filename. Write only that plan file at the repository root.
12. Do not implement code, create tickets, or modify files other than the plan file explicitly approved by the user.
