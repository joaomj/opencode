---
name: to-prd
description: Synthesize resolved conversation and codebase context into a product requirements document without re-interviewing the user. Use after grill-with-docs or when the plan is settled.
license: MIT
---

# to-prd

`to-prd` turns the current conversation context and codebase understanding into a PRD without asking new questions. It synthesizes what is already known.

## What the PRD includes

- Problem statement
- Solution
- Numbered user stories (extensive)
- Implementation decisions
- Testing decisions
- Out-of-scope items
- Further notes
- Sketch of major modules to build or modify

## Deep modules

`to-prd` actively looks for deep module opportunities — modules that hide meaningful complexity behind a small, stable, testable interface.

## Workflow position

```
grill-with-docs → to-prd → to-issues → implement/tdd
```

Use after domain language and plan are resolved, before breaking into issues.
