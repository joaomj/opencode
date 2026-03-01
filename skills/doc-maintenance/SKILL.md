---
name: doc-maintenance
description: Update and prune project documentation for accuracy and relevance
license: MIT
---
# Documentation Maintenance

Maintain documentation accuracy by pruning obsolete content and updating stale sections.

## Non-Negotiable On Skill Load

Whenever this skill is loaded, the agent MUST:

1. Update `README.md` to match the current codebase behavior, setup, and usage.
2. Update `CHANGELOG` (if it exists, e.g. `CHANGELOG.md`) so it reflects the current code status.
3. Prune outdated, incorrect, or deprecated documentation content.

## When to Update Documentation

- After code reviews
- After major refactors or architectural changes
- When explicitly asked
- When implementation diverges from documented behavior
- After completing features that modify documented workflows

## Prune Signs - Remove Content With These Indicators

| Sign | Example | Action |
|------|---------|--------|
| Old date references | "As of Q3 2023" when current is 2025+ | Remove or update |
| Non-existent components | Documents `AuthService` that was removed | Delete section |
| Deprecated patterns | "We use API v2" when v3 is current | Update to current |
| Historical explanations | "How we migrated from X to Y in 2022" | Remove history, keep current |
| Data flow mismatch | Documented flow doesn't match implementation | Rewrite to match code |
| Accumulated TODOs | Old TODOs that are no longer relevant | Delete or convert to issues |

## Update Process

1. **Scan documentation files** - Find all `.md` files in `docs/` and project root
2. **Mandatory README update** - Refresh `README.md` so it aligns with current code behavior
3. **Mandatory changelog update (if present)** - Update existing `CHANGELOG` file(s) to match current code status
4. **Cross-reference implementation** - Compare docs against actual code
5. **Identify obsolete content** - Mark sections matching prune signs
6. **Remove outdated sections** - Delete obsolete content; do not keep stale references
7. **Update stale current state** - Rewrite to match implementation if changed
8. **Verify required sections** - Ensure tech-context.md has all 4 sections

## Required Sections for docs/tech-context.md

If project has `docs/tech-context.md`, verify it contains:

1. **Project Brief** - Core requirements, goals, business problem
2. **Product Context** - Why project exists, problems solved, UX goals
3. **System Patterns** - Architecture, design patterns, component relationships
4. **Tech Context** - Technologies, setup, constraints, dependencies

## Depth vs Bloat

| Good (Depth) | Bad (Bloat) |
|--------------|-------------|
| Detailed explanations of CURRENT state | Accumulated outdated content |
| Decisions and tradeoffs documented | Historical "how we got here" |
| Data flows matching implementation | Components that no longer exist |
| Metrics with HOW/WHY/WHAT/WHERE | Old examples with deprecated APIs |

## Output Format

After completing documentation review, report:

```
Documentation Update Report
- Files reviewed: X
- Obsolete sections removed: Y
- Stale sections updated: Z
- Files unchanged: W
```

## Important Rules

- NEVER create new documentation files proactively
- NEVER add "we used to do X" historical sections
- NEVER keep outdated examples "for reference"
- ALWAYS update `README.md` whenever this skill is loaded
- ALWAYS update existing `CHANGELOG` file(s) when present
- ALWAYS remove content that doesn't match current implementation
- ALWAYS prune outdated, deprecated, or misleading information
- ALWAYS explain decisions and tradeoffs, not just mechanics
