---
name: create-pull-request
description: End-to-end PR creation with merge conflict detection and professional descriptions via GitHub CLI
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
git ls-remote --heads origin 2>/dev/null | awk '{print $2}' | sed 's|refs/heads/||' | sort | uniq
```

Present detected branches. **Ask user which remote branch to compare against:**
- If `main` exists, suggest as default
- If `master` exists, offer as alternative
- Allow custom branch input
- Default: compare current branch against `origin/main` (or `origin/master` if main doesn't exist)

Validate destination branch exists:

```bash
git ls-remote --heads origin <destination-branch>
```

### Phase 3: Merge Conflict Check

```bash
git fetch origin <destination-branch>
git merge-tree $(git merge-base HEAD origin/<destination-branch>) HEAD origin/<destination-branch> | grep -c "changed in both" || echo "0"
```

If conflicts found, present files and ask user how to proceed:
1. Resolve now (guide through each file)
2. Abort and resolve manually
3. Continue with PR creation

### Phase 4: PR Description

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

### Phase 5: Create the PR

```bash
git push -u origin <source-branch>
gh api user --jq '.login'
```

Generate title from commits (format: `type: description`, imperative mood, max 72 chars).

### Phase 5a: Code Review Gate

The `policy-gate` plugin blocks `gh pr create` unless a review receipt exists for HEAD.

- Run `/code-review` before creating the PR.
- If the review passes (or passes with no P0/P1), proceed.
- If the review fails with P0/P1 issues, fix them and re-review.

**Skip the gate** (review receipt not required):
- Add `[skip-review]` to the latest commit message: `git commit -S --amend -m "commit msg [skip-review]"`
- Or set `OPENCODE_SKIP_REVIEW=1` in the shell that runs `gh pr create`

Ask user if draft PR, then:

```bash
gh pr create \
  --base <destination-branch> \
  --head <source-branch> \
  --title "<title>" \
  --body "<description>" \
  --assignee "@me"
```

The `--assignee "@me"` automatically assigns the PR to the current authenticated user.

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

**Jira Issue:**
<!-- Asked from user, e.g.: [ML-123](https://company.atlassian.net/browse/ML-123) -->

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
- Never auto-fix without user permission
- Never leave placeholder text in description
- Never push to default branch without explicit confirmation
- Never use emojis in PR title or description
- Never include secrets in PR description
