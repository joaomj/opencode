---
description: Update and prune project documentation
---

# Update Documentation

Identify and remove obsolete documentation content from the project.

## Scan

Find all documentation files:
```bash
find . -name "*.md" -not -path "./.git/*" | sort
```

Focus on:
- `tech-context.md` (source of truth)
- `README.md`
- `docs/*.md`
- Command docs in `commands/`
- Agent docs in `agents/`
- Skill docs in `skills/*/SKILL.md`

## Audit Checklist

For each doc file:
- [ ] Check for references to removed/non-existent files
- [ ] Check for outdated commands, paths, or version numbers
- [ ] Check for deprecated features or removed functionality
- [ ] Verify architecture descriptions match actual code
- [ ] Verify all referenced skills/commands actually exist
- [ ] Cross-reference with actual implementation

## Prune Signs

| Sign | Action |
|------|--------|
| Old dates, stale version numbers | Update or remove |
| References to non-existent components | Remove |
| Deprecated patterns | Replace with current approach |
| Skills listed but not found | Remove from table |
| Skills missing from table | Add |

## Changes

- **Remove** obsolete sections (not rewriting history)
- **Update** stale sections to match current state
- **Keep** meaning intact -- don't rewrite, prune
- **Verify** data flows match implementation

## Report

Present findings as a list:
```
**File**: path/to/doc.md
**Issue**: [description]
**Action**: [remove/update]
```
