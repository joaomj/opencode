---
name: improve-codebase-architecture
description: Find evidence-based opportunities to deepen modules and improve locality, leverage, and test seams. Use when the user requests architecture maintenance or a clear structural hotspot exists.
disable-model-invocation: true
---

# Improve Codebase Architecture

This skill finds structural friction. It does not generate a general cleanup
list and does not implement speculative refactors.

## Scope

Prefer areas that:

- Changed often in recent history.
- Have repeated bugs or difficult verification.
- Force callers to repeat orchestration.
- Expose implementation details through a large interface.
- Require internal mocks to test important behavior.

Read the domain glossary and ADRs before proposing changes. Use
`codebase-design` vocabulary.

## Method

1. Select a scope from the user's direction or recent hotspots.
2. Inspect the code, tests, history, and current behavior.
3. Apply the deletion test to suspected shallow modules.
4. Produce a small set of candidates with evidence.
5. For each candidate, state the current interface, proposed seam, locality and
   leverage gains, risks, and an alternative.
6. Ask the user which candidate to explore.
7. Use `grill-with-docs` and `domain-modeling` for the selected candidate.
8. Write an ADR only when the decision meets the ADR threshold.

Do not propose interfaces before the user selects a candidate. Do not change
code during the scan.
