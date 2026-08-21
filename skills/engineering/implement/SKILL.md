---
name: implement
description: Implement approved work from a ticket, specification, or implementation plan. Use when the required preparation and approval gates are complete.
---

# Implement

Implement only the approved scope. The input can be a Jira ticket, approved
specification, or `PLAN-<ticket-id>.md`.

## Before editing

1. Read the input and related ADRs, glossary, and `tech-context.md`.
2. Inspect current code and existing patterns.
3. Confirm the acceptance criteria and verification seam.
4. State any missing decision or contradiction. Stop when it blocks safe work.

## During implementation

- Execute approved plan steps in their numbered order. Do not run steps in
  parallel, skip a step, or begin the next step before its gate passes.
- Work in the small scope stated by the current step. If the step needs an
  unstated design decision, stop and report it instead of guessing.
- Use an established pattern. State its rationale and alternative when the plan
  did not already decide it.
- For confirmed bugs, use one failing black-box regression test before the fix.
- For features, do not write tests for every function or require test-first work
  without a strong regression reason.
- Surface every failure. Do not convert unexpected failures into empty results.
- Record the exact command and result for each mandatory gate. A passing status
  must come from the specified behavior or artifact, not from a changed file
  existing alone.
- Use `uv` for Python commands and `rg` for searches.
- Do not create a large test harness without approval.

## Completion

Verify acceptance criteria and the highest useful test seam. Record failures and
verification gaps. Update current-state documentation when behavior or
architecture changed. Leave commits and pull requests to their explicit
commands or user requests.
