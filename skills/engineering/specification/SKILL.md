---
name: specification
description: Define approved user-visible behavior, rules, failure outcomes, acceptance criteria, and scope for work that is not clear enough for a plan. Use after discovery and before implementation planning.
---

# Specification

A specification answers: "What behavior must exist?" It does not describe the
repository implementation.

## Inputs

Read the ticket, current behavior, relevant domain glossary, ADRs, research,
and accepted prototype or grilling results. Report conflicts between them.

## Structure

Write only the sections that add value:

```markdown
# <Feature or behavior>

## Problem

## Desired behavior

## Actors and user flows

## Business rules

## Failure behavior

## Acceptance criteria

## Constraints

## Out of scope

## Open decisions
```

Acceptance criteria must describe observable behavior. Include successful,
invalid, unauthorized, and recovery outcomes when they matter.

Keep file paths, symbols, algorithms, and implementation steps out of the
specification. Those belong in the implementation plan.

## Approval

Present the draft for user approval before treating it as a delivery contract.
Do not publish it to Jira automatically. Store an approved specification under
`docs/specs/` only when it has value beyond the ticket and plan.
