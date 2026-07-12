---
name: doc-maintenance
description: Audit and update project documentation for accuracy and relevance. Use when the user asks to update docs, clean up documentation, or after code changes that affect public APIs.
---

# Documentation Maintenance

Update and prune project documentation to maintain accuracy and relevance.

## Scope

- Update outdated information
- Remove obsolete documentation
- Ensure consistency across documents
- Keep documentation aligned with code

## Domain glossary and ADRs

Where the project has a `CONTEXT.md` glossary or ADRs under `docs/adr/`, keep them consistent:

- When a term in `CONTEXT.md` conflicts with how the code actually uses it, surface the conflict
- When a decision documented in an ADR is contradicted by newer code, note the discrepancy
- Keep the glossary vocabulary-only — no implementation details, spec content, or scratch notes

## Workflow

### Step 1: Find Documentation Files

Use `glob` to find markdown files, excluding `.git/` and generated directories.

### Step 2: Audit Each Document

For each document:
- Check for references to removed files
- Check for outdated commands/paths
- Check for stale version numbers
- Check for deprecated features
- Verify referenced components actually exist

### Step 3: Identify Issues

| Issue Type | Detection |
|------------|-----------|
| Dead links | References to non-existent files |
| Outdated commands | Commands that no longer work |
| Stale versions | Version numbers that don't match current |
| Obsolete features | References to removed functionality |
| Missing skills | Table entries for skills that don't exist |
| Inconsistent naming | Different terms for same concept |

### Step 4: Propose Changes

For each issue found, present:
- **File**: path/to/doc.md
- **Line**: N
- **Issue**: description of problem
- **Current**: original content
- **Proposed**: updated content
- **Reasoning**: why this change

### Step 5: Get User Approval

Ask: "Apply these documentation updates? (yes/no/selective)"

- If "yes": Apply all updates
- If "no": Do nothing
- If "selective": Apply user-selected changes only

## Non-Negotiable Rules

| Rule | Violation = STOP |
|------|------------------|
| Preserve intent | Do not change meaning of documentation |
| Ask before edit | Request permission before each change |
| Check git history | Verify what changed recently before removing |
