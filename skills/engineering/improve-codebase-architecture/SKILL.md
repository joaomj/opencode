---
name: improve-codebase-architecture
description: Find evidence-based opportunities to deepen modules and improve locality, leverage, and test seams. Use when the user requests architecture maintenance or a clear structural hotspot exists.
disable-model-invocation: true
---

# Improve Codebase Architecture

Find evidence-based structural friction. Do not create a general cleanup list
or implement a speculative refactor.

## Scope

Prefer areas that changed often, repeat bugs, force callers to repeat
orchestration, expose implementation details, or require internal mocks for
important behavior.

## Method

1. Select a scope from the user's direction or recent hotspots.
2. Inspect the code, tests, history, and current behavior.
3. Produce a small set of candidates with evidence.
4. For each candidate, state the current interface, locality and leverage gains,
   risks, and an alternative.
5. Ask the user which candidate to explore.
6. Load `codebase-design` for deletion, seam, depth, and test-surface analysis.
7. Load `grill-with-docs` or `domain-modeling` only when a decision or term is
   still unclear.
8. Write an ADR only when the decision is hard to reverse, surprising, and
   based on real trade-offs.

Do not propose interfaces before the user selects a candidate. Do not change
code during the scan. `codebase-design` owns detailed design analysis.
