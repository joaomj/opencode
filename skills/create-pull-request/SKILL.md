---
name: create-pull-request
description: End-to-end PR creation with code review, merge conflict detection, and professional descriptions via GitHub CLI
license: MIT
---

# Create Pull Request

End-to-end workflow to create a high-quality pull request.

## When to Use

- User says: "create PR", "open pull request", "make a PR", "/pr"
- User wants to submit current branch changes for review

## Workflow

### Phase 1: Pre-flight Checks

Run before anything else. Stop if any check fails.

```bash
gh --version && gh auth status
git rev-parse --is-inside-work-tree
git remote get-url origin
gh repo view --json url
git status --porcelain
```

- If `gh` not installed: guide user to install
- If not authenticated: ask user to run `gh auth login`
- If uncommitted changes: ask user to commit or stash first

### Phase 2: Branch Confirmation

**MANDATORY: Always confirm branches with user.**

```bash
git branch --show-current
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

Present detected branches and ask user to confirm or specify alternatives.

Validate destination branch exists:

```bash
git ls-remote --heads origin <destination-branch>
```

### Phase 3: Code Review

Collect diff data:

```bash
git diff origin/<destination-branch>...HEAD
git diff origin/<destination-branch>...HEAD --name-status
git log origin/<destination-branch>...HEAD --oneline
```

Run `@code-reviewer` subagent on the full diff. Present findings by severity:

| Severity | Meaning |
|----------|---------|
| P0 | Critical: security, data loss, breaking bugs |
| P1 | High: logic errors, performance issues |
| P2 | Medium: code quality, missing error handling |
| P3 | Low: minor improvements, naming |

If P0 issues found, strongly recommend fixing before creating the PR.

### Phase 4: Review & Fix

Ask user:

```
Would you like me to fix these issues before creating the PR?
1. Fix all issues
2. Fix P0 and P1 only
3. Fix specific issues
4. Skip fixes, proceed to PR
```

If fixing: apply fixes, run lint/test, commit.

### Phase 5: Merge Conflict Check

```bash
git fetch origin <destination-branch>
git merge-tree $(git merge-base HEAD origin/<destination-branch>) HEAD origin/<destination-branch> | grep -c "changed in both" || echo "0"
```

If conflicts found, present files and ask user how to proceed:
1. Resolve now (guide through each file)
2. Abort and resolve manually
3. Continue with PR creation

### Phase 6: PR Description

Collect git data and check for repo PR template:

```bash
ls .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md .github/PULL_REQUEST_TEMPLATE/*.md 2>/dev/null
```

**Auto-populate from git:**
- What: commit messages
- Changes: categorized by type (feat/fix/refactor/docs/chore)
- Related Work: parse `Fixes #`, `Closes #`, `Relates to #` from commits
- Files changed: from `--name-status`

**Ask user for:**
- Impact
- How to test
- Review focus
- Deployment notes

Present preview. Validate no placeholder text remains (`[TODO]`, empty sections).

### Phase 7: Create the PR

```bash
git push -u origin <source-branch>
```

Generate title from commits (format: `type: description`, imperative mood, max 72 chars).

Ask user if draft PR, then:

```bash
gh pr create \
  --base <destination-branch> \
  --head <source-branch> \
  --title "<title>" \
  --body "<description>"
```

Post-creation:

```bash
gh pr view <PR-NUMBER> --json url,title,state,mergeable
```

Display PR URL and any immediate issues.

## PR Description Template

Use when no repository-specific template exists. Remove unused sections before creating the PR.

```markdown
## Summary

**What:**
<!-- Auto-populated: List of changes from commits -->

**Why:**
<!-- Auto-populated from commit messages or asked from user -->

**Impact:**
<!-- Asked from user -->

## Related Work

<!-- Auto-populated from commit messages: Fixes #, Closes #, Relates to # -->

## Changes

<!-- Auto-populated and categorized from commit history -->

| Type | Description |
|------|-------------|
| Feature | |
| Fix | |
| Refactor | |
| Docs | |
| Config | |
| Chore | |

## Code Review

<!-- Populated from Phase 3 findings -->

- Issues found: <count> (P0: X, P1: Y, P2: Z, P3: W)
- Issues fixed: <count>
- Remaining: <list or "None">

## Testing

- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] Edge cases considered

**How to test:**
<!-- Asked from user -->

## Deployment Notes

<!-- Asked from user -->

- **Breaking changes:**
- **Database migrations:**
- **Config updates:**
- **Third-party API changes:**

## Review Focus

<!-- Asked from user: specific areas needing attention -->

## Checklist

- [ ] Code follows project style guidelines
- [ ] No secrets or sensitive data in diff
- [ ] Documentation updated (if applicable)
- [ ] Backwards compatible (or breaking changes documented above)
```

## Anti-Patterns

- Never skip branch confirmation
- Never create PR without code review
- Never auto-fix without user permission
- Never leave placeholder text in description
- Never push to default branch without explicit confirmation
- Never use emojis in PR title or description
- Never include secrets in PR description
