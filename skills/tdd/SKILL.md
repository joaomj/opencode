---
name: tdd
description: Red-green-refactor for agentic coding. Builds features or fixes bugs one behavior at a time via vertical test slices, writing one test then just enough code to pass it before the next cycle.
license: MIT
---

# tdd

`tdd` builds a feature or fixes a bug test-first, one behaviour at a time, via the red-green loop: write one failing test, add just enough code to pass it, repeat.

## Rules

- Never writes all tests up front — one test, then code, then the next test
- Tests target public interfaces only, so internals can change without breaking tests
- Expected values come from independent sources (spec literals, worked examples) — never recomputed the same way as the code
- Refactoring only happens when the suite is green; never while red

## Tracer bullet

The first cycle is a tracer bullet: one test proving a single path end-to-end before building outward.

## Workflow position

```
grill-with-docs → to-prd → to-issues → implement/tdd → code-review
```

`tdd` is the engine inside the implement step. It can also be invoked directly via `/tdd` when there's concrete behaviour to build.
