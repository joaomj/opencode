---
description: Create an implementation plan from the current repository state
---

Create an implementation plan for `$ARGUMENTS` using the
`implementation-planning` workflow.

This command is an explicit workflow selector. Do not use it for exploration,
research, specification, architecture discussion, or implementation.

1. Explain the strategy in plain terms for a product manager, including what will
   and will not change.
2. Inspect the current repository before making claims. Use deployed or remote
   behavior, local code, updated documentation, and Jira tickets in that order.
3. Confirm that the desired behavior is clear enough for a plan. If it is not,
   stop and report the discovery work required.
4. A ticket ID is optional. Use one if `$ARGUMENTS` provides it, but do not ask
   for one just to continue.
5. Produce one ordered chain of numbered implementation steps. Do not present
   parallel work, optional work, branches, or unnumbered sub-plans.
6. Make every step small enough for a junior engineer to implement without
   further design help. Each step must have one clear outcome, exact edits,
   complete repository-relative code paths, and no hidden work.
7. Put every repository in its own `## Repository: ...` subsection. For multiple
   repositories, keep one global step number sequence across those subsections.
8. Add a mandatory gate to every step. The gate must name an exact command or
   independent observable check and an exact pass condition. Do not use gates
   such as "looks correct", "reviewed", or "tests if possible".
9. Do not start the next step until the previous gate passes. Stop the plan at a
   failed gate and state the required correction.
10. Back every step with current files, symbols, and behavior. Mark unknown areas
    as discovery work instead of inventing an implementation.
11. For every step, include acceptance criteria, dependencies, risks, the chosen
    established coding pattern, its rationale and trade-offs, one alternative,
    out-of-scope work, and verification evidence.
12. Format every step with: one outcome, repository, complete paths and symbols,
    exact change, acceptance criteria, preceding-step dependency, pattern and
    trade-off, alternative, risk and rollback, exact gate command or check,
    exact pass condition, and stop condition.
13. Present the complete plan in the conversation and ask the user whether they
    approve it. Do not create a branch or write a file before approval.
14. After plan approval, ask separately whether the user wants a planning branch.
    Create a branch from `origin/<default-branch>` using the repository naming
    convention only if the user agrees. Do not rebase or merge.
15. After plan approval, ask separately whether the user wants the plan written
    to Markdown. If yes, use `PLAN-<ticket-id>.md` when a ticket ID exists;
    otherwise ask for or suggest a filename. Write only that plan file at the
    repository root.
16. Do not implement code, create tickets, or modify files other than the plan
    file explicitly approved by the user.
