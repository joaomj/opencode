---
name: create-pull-request
description: End-to-end PR creation workflow with automated code review, fix verification, merge conflict detection, and professional PR description generation via GitHub CLI
license: MIT
---

# Create Pull Request

End-to-end workflow to create a high-quality pull request: code review, fix issues, verify merge compatibility, generate a professional description, and open the PR on GitHub.

## What I Do

- Verify GitHub CLI, authentication, and repository context
- Detect source and destination branches (always confirm with user)
- Run automated code review via `@code-reviewer` subagent
- Ask user for permission to fix review findings, then fix and commit
- Check for merge conflicts against the remote destination branch
- Generate a professional-grade PR description from git data and user input
- Push the branch and create the PR via `gh pr create`

## When to Use Me

Use this skill when:

- User says: "create PR", "open pull request", "open a PR"
- User says: "create pull request", "make a PR", "submit a PR"
- User says: "/pr", "/create-pr", "/pull-request"
- User wants to submit current branch changes for review

## Workflow

### Phase 1: Pre-flight Checks

Run these verification steps before anything else. If any check fails, stop and inform the user.

**1.1 Verify GitHub CLI**

```bash
gh --version
```

If missing, guide user to install: `brew install gh` (macOS), `winget install GitHub.cli` (Windows), or see https://cli.github.com/

**1.2 Check authentication**

```bash
gh auth status
```

- If not logged in: Stop. Ask user to run `gh auth login`
- If wrong account: Alert user and offer to switch via `gh auth switch`

**1.3 Verify git repository**

```bash
git rev-parse --is-inside-work-tree
git remote get-url origin
gh repo view --json url
```

- Ensure we are inside a git repo with a GitHub remote

**1.4 Check for uncommitted changes**

```bash
git status --porcelain
```

- If uncommitted changes exist: Stop. Ask user to commit or stash before proceeding.

**1.5 Check for unpushed commits (informational)**

```bash
git log origin/$(git branch --show-current)..HEAD --oneline 2>/dev/null
```

- Note unpushed commits for later (will push in Phase 7)

### Phase 2: Branch Confirmation

**MANDATORY: Always ask the user to confirm branches before proceeding.**

**2.1 Detect source branch**

```bash
git branch --show-current
```

**2.2 Detect remote default branch (destination)**

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

This returns the actual default branch name (`main`, `master`, `develop`, etc.).

**2.3 Ask user for confirmation**

Present the detected branches and ask:

```
Source branch:      <current branch>
Destination branch: <detected default branch> (remote default)

Confirm these branches? Or specify a different destination:
```

Wait for explicit user confirmation. Accept alternatives if user wants to target a different branch.

**2.4 Validate destination branch exists on remote**

```bash
git ls-remote --heads origin <destination-branch>
```

If not found, ask user to specify a valid remote branch.

### Phase 3: Code Review

**3.1 Generate the diff for review**

```bash
git diff origin/<destination-branch>...HEAD
```

Also collect the list of changed files:

```bash
git diff origin/<destination-branch>...HEAD --name-status
```

And the commit log:

```bash
git log origin/<destination-branch>...HEAD --oneline
```

**3.2 Run code review via @code-reviewer subagent**

Invoke the `@code-reviewer` subagent on the full diff between the source and destination branch.

The code-reviewer will return findings classified by severity:

| Severity | Meaning |
|----------|---------|
| P0 | Critical: security vulnerabilities, data loss, breaking bugs |
| P1 | High: logic errors, significant performance issues |
| P2 | Medium: code quality, missing error handling, style violations |
| P3 | Low: minor improvements, naming, documentation gaps |

**3.3 Present review findings to user**

Display all findings in a structured format:

```
## Code Review Findings

### P0 (Critical)
- [file:line] description

### P1 (High)
- [file:line] description

### P2 (Medium)
- [file:line] description

### P3 (Low)
- [file:line] description

Summary: N issues found (P0: X, P1: Y, P2: Z, P3: W)
```

If P0 issues are found, strongly recommend fixing before creating the PR.

### Phase 4: Review & Fix

**4.1 Ask user for permission to fix**

```
Would you like me to fix these issues before creating the PR?

Options:
1. Fix all issues
2. Fix P0 and P1 only
3. Fix specific issues (tell me which)
4. Skip fixes, proceed to PR creation
```

Wait for user response.

**4.2 Apply fixes**

If user chose to fix issues:

1. Apply fixes for the selected severity levels
2. Run lint and typecheck commands (check project for `package.json` scripts, `Makefile`, `pyproject.toml` configs)
3. If any fix introduces new test failures, address them
4. Stage and commit the fixes:

```bash
git add -A
git commit -m "fix: address review findings (P0/P1)"
```

Use appropriate commit type based on nature of fixes.

**4.3 Re-run review on fixes (optional)**

If significant fixes were applied, offer to run a focused review on just the fix commit.

### Phase 5: Merge Conflict Check

**5.1 Fetch latest remote destination branch**

```bash
git fetch origin <destination-branch>
```

**5.2 Check for merge conflicts**

Use `git merge-tree` to check for conflicts without modifying the working tree:

```bash
git merge-tree $(git merge-base HEAD origin/<destination-branch>) HEAD origin/<destination-branch> | grep -c "changed in both" || echo "0"
```

Alternative (if `merge-tree` output is unclear):

```bash
git merge --no-commit --no-ff origin/<destination-branch>
# Check result, then abort
git merge --abort
```

**5.3 Handle conflicts if found**

If merge conflicts exist:

1. Present the conflicting files to the user
2. Ask user how to proceed:

```
Merge conflicts detected in:
  - path/to/file1
  - path/to/file2

Options:
1. Resolve conflicts now (I will guide you through each file)
2. Abort and resolve manually later
3. Continue with PR creation (resolve conflicts after PR is open)
```

If user chooses option 1, guide through conflict resolution:

```bash
git merge origin/<destination-branch>
# Resolve each conflict file
git add <resolved-files>
git commit -m "merge: resolve conflicts with <destination-branch>"
```

### Phase 6: PR Description Generation

**6.1 Collect git data**

Run in parallel:

```bash
git log origin/<destination-branch>...HEAD --oneline
git diff origin/<destination-branch>...HEAD --stat
git diff origin/<destination-branch>...HEAD --name-status
```

**6.2 Check for repository PR template**

Look for (in order):
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/pull_request_template.md`
- `.github/PULL_REQUEST_TEMPLATE/*.md`

If found, use that template structure.

**6.3 Auto-populate template fields**

**From git data:**
- **What**: Extract from commit messages (first line of each commit)
- **Why**: Extract from commit message bodies, or infer from scope
- **Changes**: Categorize commits by type (feat/fix/refactor/docs/chore)
- **Related Work**: Parse `Fixes #XXX`, `Closes #XXX`, `Relates to #XXX` from all commit messages
- **Files changed**: List from `--name-status`

**6.4 Ask user for remaining fields**

The following fields CANNOT be auto-populated. Ask the user for each:

- **Impact**: Business or technical impact of these changes
- **How to test**: Step-by-step testing instructions for reviewers
- **Review Focus**: Specific areas or files that need extra attention
- **Deployment Notes**: Any breaking changes, database migrations, config updates

Present the populated template as a preview. Ask:

```
Preview of PR description:

<rendered template>

Edit any section or approve to proceed.
```

Wait for user approval or edits.

**6.5 Validate description**

Before proceeding, verify:
- No placeholder text remains (`[TODO]`, `FILL IN`, empty required sections)
- `Related Work` section is populated (or explicitly confirmed as N/A)
- `How to test` section has actual instructions

If validation fails, ask user to complete missing sections.

### Phase 7: Create the PR

**7.1 Push the branch (if needed)**

```bash
git push -u origin <source-branch>
```

If the branch already tracks a remote, a plain `git push` is sufficient. Use `-u` for first push.

**7.2 Generate PR title**

PR title is derived from:
- If single commit: Use the commit message subject
- If multiple commits with same type: Use a summarized title
- If multiple commits with different types: Ask user for a summary title

Format: `type: description` (no scope parentheses). Imperative mood.

Examples:
- `feat: add user authentication flow`
- `fix: resolve null pointer in payment processing`
- `refactor: extract validation logic into shared module`

**7.3 Create the PR**

```bash
gh pr create \
  --base <destination-branch> \
  --head <source-branch> \
  --title "<title>" \
  --body "<description>"
```

For draft PRs, ask user first:
```
Create as draft PR? (y/n)
```

If yes, add `--draft` flag.

**7.4 Post-creation**

After successful creation:

1. Display the PR URL returned by `gh pr create`
2. Run a final status check:
   ```bash
   gh pr view <PR-NUMBER> --json url,title,state,mergeable
   ```
3. Inform user of any immediate issues (failed checks, merge conflicts detected post-creation)

## PR Description Template

Use this template when no repository-specific template exists. Remove unused sections before creating the PR.

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

## Error Handling

### Common Failures

| Error | Cause | Resolution |
|-------|-------|------------|
| `gh auth status` fails | Not logged in | Ask user to run `gh auth login` |
| `Permission denied (publickey)` | SSH key mismatch | Check `ssh-add -l`, load correct key |
| `remote branch not found` | Destination branch does not exist on remote | Ask user for valid branch name |
| `gh pr create` returns 422 | Branch already has a PR | Offer to update existing PR instead |
| `merge conflict` detected | Conflicts between branches | Guide user through resolution (Phase 5) |
| Push rejected | Remote has diverged | `git pull --rebase origin <branch>`, resolve, retry |
| PR creation rate limit | Too many PRs created recently | Wait and retry |

### Branch Protection

If the destination branch has protection rules:

```bash
gh api repos/{owner}/{repo}/branches/{branch}/protection
```

Inform user of any required checks, required reviews, or restrictions that may block merge.

## Anti-Patterns to Avoid

- Never skip the branch confirmation step (Phase 2)
- Never create a PR without running code review first (Phase 3)
- Never auto-fix issues without user permission (Phase 4)
- Never skip merge conflict check (Phase 5)
- Never leave placeholder text in the PR description (Phase 6)
- Never push to or target the default branch without explicit user confirmation
- Never use emojis in PR title or description
- Never include secrets, credentials, or tokens in the PR description

## Completion Checklist

After PR creation:

- [ ] Pre-flight checks passed (gh CLI, auth, repo)
- [ ] Branches confirmed by user
- [ ] Code review completed via @code-reviewer
- [ ] User approved fix decisions
- [ ] Merge conflict check performed
- [ ] PR description reviewed and approved by user
- [ ] PR created successfully via `gh pr create`
- [ ] PR URL provided to user
- [ ] Post-creation status verified
