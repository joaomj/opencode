---
description: Implement approved work from a ticket, specification, or plan
agent: build
---

Implement `$ARGUMENTS` using the `implement` skill.

1. Read the ticket, approved specification, or `PLAN-<ticket-id>.md`.
2. Read relevant ADRs, `tech-context.md`, glossary, and current code.
3. Confirm the acceptance criteria and highest useful verification seam.
4. Stop and report any missing decision that blocks safe implementation.
5. Implement only the approved scope in small vertical slices where practical.
6. Use selective TDD for confirmed bugs. Do not write speculative tests for every function.
7. Load `coding-standards`, `error-handling`, `python-tooling`, and `testing-best-practices` when applicable.
8. Verify user-visible behavior and record failures or verification gaps.
9. Load `code-review` when the implementation is ready for the review phase.
10. Do not commit or create a pull request unless the user explicitly requests it.
