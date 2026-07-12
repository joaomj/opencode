---
name: tdd
description: Reference material for test-driven development. Red-green loop for agentic coding — one failing test, then just enough code to pass, repeat. Refactoring is handled separately in code review.
metadata:
  credit: Matt Pocock (https://github.com/mattpocock/skills)
---

# tdd

Reference-only skill for test-driven development. TDD is reserved for bug fixes. The red-green loop uses e2e tests against a running instance.

1. **Red** — Write a failing e2e test against a running instance
2. **Green** — Make the test pass with minimal code
3. **Repeat** — Move to the next behaviour

Refactoring is no longer part of the TDD loop. It is handled in the **code review** phase, which keeps implementation focused.

## Rules

- Never writes all tests up front — one test, then code, then the next test
- Tests target user-facing interfaces (API, CLI, UI), so internals can change without breaking tests
- Expected values come from independent sources (spec literals, worked examples) — never recomputed the same way as the code
- Tests stay green throughout; refactoring happens only after the diff is complete

## Tracer bullet

The first cycle is a tracer bullet: one e2e test proving a single user-visible path end-to-end before building outward.

## Workflow position

```
grill-with-docs → to-spec → to-tickets → implement
```

`tdd` is the engine inside the implement step. It can also be invoked directly via `/tdd` when there's concrete behaviour to build. After implementation, `/code-review` handles refactoring concerns.
