---
name: to-issues
description: Break a PRD or plan into vertical-slice GitHub issues using tracer-bullet slices. Each issue is narrow but end-to-end complete. Prefers AFK (agent-compatible) slices over HITL.
license: MIT
---

# to-issues

`to-issues` breaks a plan, spec, or PRD into independently grabbable GitHub issues using tracer-bullet vertical slices.

## Vertical slices, not horizontal

Each issue cuts through the full stack (schema, API, UI, tests) rather than splitting by layer. Example:

```
1. User can create the simplest version end-to-end
2. User can edit one field end-to-end
3. User can see the first validation error end-to-end
```

## AFK vs HITL

Each slice is marked:
- **AFK** — agent can implement without more human input
- **HITL** — needs human checkpoint for design review or decision

Prefers AFK slices when possible.

## Workflow position

```
grill-with-docs → to-prd → to-issues → implement/tdd
```

Use after the PRD exists. Proposes issue breakdown, asks for approval on granularity and dependencies, then creates issues in dependency order.
