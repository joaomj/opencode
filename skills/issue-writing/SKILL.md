---
name: issue-writing
description: Template and procedure for writing project issues to docs/issues/. Use ONLY when the user explicitly asks to write or record an issue.
license: MIT
---

# Issue Writing

Create structured issue files in `docs/issues/` for project tracking.

## Location

Each issue is a single markdown file: `docs/issues/<slug>.md`

Slugs are lowercase, hyphen-separated, and descriptive (e.g., `login-race-condition.md`, `api-rate-limit-missing.md`).

## Frontmatter

Every issue file MUST start with YAML frontmatter:

```yaml
---
title: Short descriptive title
status: open
created: YYYY-MM-DD
---
```

Valid status values: `open`, `in_progress`, `resolved`, `closed`.

## Sections

After frontmatter, write these sections in order:

### Summary

Brief description of the issue (1-3 sentences).

### Steps to Reproduce

Numbered list of exact steps.

### Expected Behavior

What should happen.

### Actual Behavior

What actually happens.

### Environment

- Project version or commit
- Relevant configuration or dependencies

### Affected Areas

Which modules, features, or files are impacted.

### Possible Fixes

- Option A: short description
- Option B: short description
- (add more as relevant)

### Implemented Fix

Write this section only when the issue is resolved. Include:
- What was done
- Commit or PR reference
