---
description: Update and prune project documentation
---
Load the doc-maintenance skill and update all project documentation.

1. Load skill: `skill({name: "doc-maintenance"})`
2. Scan for documentation files:
   - `docs/tech-context.md` (source of truth)
   - `README.md`
   - Any other `.md` files in project root and `docs/`
3. For each documentation file:
   - Check for prune signs (old dates, non-existent components, deprecated patterns)
   - Cross-reference with actual implementation
   - Remove obsolete content
   - Update stale sections to match current state
4. Report findings and changes made

Focus on:
- Removing outdated sections (not rewriting history)
- Ensuring data flows match implementation
- Verifying architecture descriptions are current
- Checking that all referenced components exist
