---
name: implementation-planning
description: Produce a repository-backed implementation plan when the user requests delivery steps for a clear change without implementing it.
---

# Implementation Planning

Use this workflow when the user wants repository-specific implementation steps.
Do not select it merely because the request is uncertain or technically
interesting.

## Ordered Steps

1. State the selected workflow, plan deliverable, and side-effect boundary.
2. Confirm that the user wants an implementation plan rather than exploration,
   research, a specification, an ADR, or implementation.
3. Identify the ticket or request identifier. Ask for one when the repository
   policy requires `PLAN-<ticket-id>.md` and none exists.
4. Inspect current code, tests, repository history, relevant documentation,
   glossary, ADRs, and remote behavior.
5. Confirm that the behavior is clear enough for a plan. Hand unresolved
   product or domain questions to the matching discovery workflow.
6. Create a branch from `origin/<default-branch>` only when the planning policy
   and user request permit it. Do not fetch, rebase, or merge automatically.
7. Write only `PLAN-<ticket-id>.md` at the repository root.
8. Back each step with current files, symbols, and behavior. Include acceptance
   criteria, risks, dependencies, open decisions, out-of-scope work, and
   verification.
9. Recommend one established pattern per task with rationale, trade-offs, and
   an alternative.
10. Verify each plan step before moving to the next. Stop on failure.

## Deliverable

Return the plain-language strategy and the approved repository-specific plan.
The plan is not implementation and does not create a commit or pull request.

## Side Effects

The only persistent project artifact is the requested plan. A planning branch
may be created when required by repository policy. Do not edit application code.
