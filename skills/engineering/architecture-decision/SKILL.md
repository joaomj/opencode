---
name: architecture-decision
description: Record a hard-to-reverse architectural choice, its alternatives, and accepted trade-offs. Use when a durable design decision needs future explanation.
disable-model-invocation: true
---

# Architecture Decision

Use an ADR only when all three conditions apply:

1. The decision is hard to reverse.
2. The choice is surprising without its context.
3. Real alternatives and trade-offs were assessed.

Do not create ADRs for routine implementation choices or temporary plans.

## Record

Use `docs/adr/NNNN-<short-title>.md` in the target repository:

```markdown
# <Decision title>

## Status

Accepted

## Context

What problem and constraints forced this decision?

## Decision

What option was selected?

## Alternatives

What reasonable alternatives were assessed, and why were they not selected?

## Consequences

What benefits, costs, risks, and constraints are accepted?
```

Keep product requirements in the ticket or specification. Keep current system
facts in `tech-context.md`. Link this ADR from the technical context index.
