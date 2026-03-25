---
name: github-pr-workflow
description: Guide PR lifecycle management with automated context detection, PR description generation from templates, troubleshooting, and best practices for GitHub CLI operations
license: MIT
---

# GitHub PR Workflow

Automate and guide GitHub PR workflows with context detection, template-based PR descriptions, and comprehensive troubleshooting.

## What I Do

- Detect correct GitHub account/SSH context automatically
- Manage PR lifecycle (create, review, respond, merge)
- Generate PR descriptions from templates (repo-specific or fallback)
- Fetch PR data and persist to temporary workspace files
- Troubleshoot auth, SSH, merge conflicts, and workflow issues
- Enforce PR best practices (scope, size, clarity)

## When to Use Me

Use this skill when:
- User says: "create PR", "open pull request", "draft PR"
- User asks to: "check PR status", "view PR", "fetch PR comments"
- User mentions: "reply to PR comments", "address review feedback"
- User wants to: "merge PR", "check if PR is ready"
- User describes daily GitHub PR operations or review workflows
- User encounters GitHub auth/SSH issues during PR operations

## Workflow

### Phase 1: Context Verification (ALWAYS FIRST)

Before ANY GitHub operation:

1. **Verify GitHub CLI availability**
   ```bash
   gh --version
   ```
   - If missing: Guide installation (`brew install gh`, `apt install gh`, etc.)

2. **Check authentication status**
   ```bash
   gh auth status
   ```
   - If not logged in: Run `gh auth login`
   - If wrong account: Alert user and offer to switch

3. **Verify repository remote**
   ```bash
   git remote get-url origin
   gh repo view --json url
   ```
   - Ensure local repo matches GitHub remote
   - Check SSH vs HTTPS protocol

4. **SSH Key Alignment Check** (if SSH remote)
   ```bash
   ssh -G github.com | grep identityfile
   ssh-add -l
   ```
   - If key mismatch: Alert user before proceeding

5. **Detect current PR context**
   ```bash
   gh pr view --json number,title,state,headRefName
   ```
   - Cache PR number for session
   - Verify branch matches PR head ref

### Phase 2: PR Lifecycle Operations

#### Creating a PR

1. **Check branch status**
   - Uncommitted changes: Ask user to commit or stash
   - Unpushed commits: Offer to push

2. **Determine PR title**
   - Extract from commit messages if single commit
   - Ask user if multiple commits with different themes
   - Follow conventional commits format if repo uses it

3. **Generate PR Description** (see below)

4. **Create the PR**
   ```bash
   gh pr create --title "$TITLE" --body "$BODY"
   ```

5. **Capture PR context**
   - Save PR number, URL, and metadata
   - Create temp file `pr-{number}-created.md` with full details

#### Generating PR Description

1. **Check for repository PR template**
   - Look for: `.github/PULL_REQUEST_TEMPLATE.md`
   - Look for: `.github/pull_request_template.md`
   - Check `.github/PULL_REQUEST_TEMPLATE/` directory

2. **Select template source**
   - If repo template found: Use it
   - If no repo template: Use fallback template (see below)

3. **Populate template fields**

   **Auto-populate from git data:**
   - `## Summary > What`: List of changes from commits
   - `## Summary > Why`: Extract from commit messages
   - `## Changes`: Categorize commits (feat:, fix:, docs:, refactor:)
   - `## Related Work`: Parse "Fixes #XXX", "Closes #XXX"

   **Ask user for:**
   - `## Summary > Impact`: Business/technical impact
   - `## Testing > How to test`: Testing instructions
   - `## Review Focus`: Areas needing attention
   - `## Deployment Notes`: Breaking changes, migrations

4. **Present populated template**
   - Save to temp file: `pr-draft-description.md`
   - Show preview
   - Allow user to edit
   - Ask: "Edit description or proceed with PR creation?"

5. **Final description assembly**
   - Merge auto-populated + user-provided content
   - Validate no placeholder text remains

#### Fallback PR Template

Use this template when no repo template exists:

```markdown
# Pull Request

## Summary

**What:** 
**Why:** 
**Impact:** 

## Related Work

- Closes #
- Relates to #

## Changes

- **Feature** - 
- **Fix** - 
- **Refactor** - 
- **Docs** - 
- **Config** - 

## Testing

- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] Edge cases considered

**How to test:**

## Deployment Notes

- **Breaking changes:**
- **Database changes:**
- **Config updates needed:**
- **Third-party APIs:**

## Review Focus

## Checklist

- [ ] Code follows style guidelines
- [ ] No secrets or sensitive data committed
- [ ] Documentation updated
- [ ] CI/CD pipeline passes
- [ ] Ready for production deployment

## Notes
```

#### Fetching PR Data

1. Use cached PR number or auto-detect from branch
2. Fetch requested data (comments, status, files, checks)
3. Persist to temporary markdown file: `pr-{number}-{type}.md`
4. Provide summary + file location

#### Responding to Comments

1. Fetch unresolved comments
2. Present in structured format with reply templates
3. Accept replies via conversation OR file edits
4. Post replies via `gh pr comment` or `gh pr review`
5. Update temporary file with reply status

#### Checking PR Status

1. Fetch PR state, checks, reviews, mergeability
2. Detect merge conflicts
3. Report blocking issues
4. Offer next actions

### Phase 3: Temporary File Management

**File Format:** `pr-{number}-{type}.md` at repo root

**Structure:**
```markdown
# PR #{number}: {title}

## Metadata
- Branch: {branch}
- Author: {author}
- State: {state}
- Created: {date}
- Updated: {date}

## Status
- Checks: {passing/total}
- Reviews: {approvals} approval(s), {pending} pending
- Conflicts: {yes/no}
- Mergeable: {yes/no}

## Comments ({count})
### Unresolved ({count})
1. [@{user}] {location}: "{excerpt}"
   ID: {node_id}
   Reply: [PENDING]

## Quick Actions
- Reply: Edit "Reply: [PENDING]" lines above
- Refresh: Re-fetch PR data
- View in browser: `gh pr view --web`
```

**Cleanup:**
- Keep only last 5 PR temp files per workspace
- Auto-delete files older than 7 days

## Troubleshooting Guide

### Authentication Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| `gh auth status` fails | Not logged in | Run `gh auth login` |
| Wrong account shown | Multiple GitHub accounts | Run `gh auth switch` or logout/login |
| Token expired | Session timeout | Run `gh auth refresh` |
| `403 Resource not accessible` | Insufficient permissions | Check repo access, use `gh auth refresh` |
| SSO required | Organization requires SSO | Run `gh auth refresh --scopes read:org` |

### SSH Key Issues

| Symptom | Cause | Solution |
|---------|-------|----------|
| `Permission denied (publickey)` | Wrong SSH key loaded | `ssh-add -D && ssh-add ~/.ssh/correct_key` |
| `Could not resolve hostname` | SSH config issue | Check `~/.ssh/config` Host entries |
| Key mismatch between repos | Different GitHub accounts | Use `gh auth status` to verify per-repo context |

### Merge Conflicts

**Detection:**
```bash
gh pr view --json mergeable,mergeStateStatus
```

**Resolution Workflow:**
1. Fetch latest base branch: `git fetch origin main`
2. Checkout PR branch
3. Merge base branch: `git merge origin/main`
4. Resolve conflicts (guide user through each file)
5. Commit resolution: `git commit`
6. Push: `git push`
7. Verify mergeability: `gh pr view --json mergeable`

**Prevention:**
- Always check merge conflicts before starting review
- Recommend rebasing if PR is behind base branch
- Warn if PR has >10 files changed (higher conflict risk)

### PR Scope Issues

**Too Many Changes:**
- Threshold: >50 files OR >1000 lines changed
- Action: Suggest splitting into multiple PRs
- Template: "This PR appears large ({N} files). Consider:
  1. Split by feature area
  2. Separate refactoring from feature changes
  3. Create stacked PRs"

**Unclear Purpose:**
- Check PR title/description quality
- Action: Ask user to clarify or suggest improvements
- Ensure linked issues mentioned

### PR Description Issues

**Empty or Placeholder Content:**
- Check if template was properly filled
- Detect placeholder text like "ISSUE_ID", "[TODO]"
- Action: Ask user to complete missing sections

**Missing Related Issues:**
- Check commits for "Fixes #XXX" patterns
- If found but not in description: Auto-add to "Related Work"
- If none found: Ask user if there's a related issue

**Template Not Found:**
- If no repo template: Use fallback template provided above
- If gist fetch fails: Use minimal fallback template

### Check Failures

**Workflow:**
1. Fetch failed checks: `gh pr checks --json name,state`
2. Identify failure patterns
3. Guide user to:
   - View logs: `gh run view --job={job_id}`
   - Re-run checks: `gh pr checks --rerun-failed`
   - Fix issues locally and push

### Review Response Issues

**Reviewer Unresponsive:**
- Check last review date
- Action: Suggest gentle ping comment
- Template: "@reviewer friendly ping - this is ready for another look when you have time"

**Conflicting Feedback:**
- Identify reviewers with opposing views
- Action: Suggest discussion comment to align
- Template: "@reviewer1 @reviewer2 I see some conflicting feedback on [topic]. Could you help clarify the preferred approach?"

## Best Practices

### PR Creation
- Clear, descriptive titles (<72 chars)
- Reference related issues: "Fixes #123"
- Include context: what changed, why, how to test
- Add screenshots for UI changes
- Use PR template consistently

### PR Description Quality
- Fill all template sections (remove unused)
- Link all related issues
- Provide testing instructions
- Note breaking changes upfront
- Highlight areas needing review focus

### PR Size
- Ideal: <400 lines changed, <15 files
- Acceptable: <1000 lines, <30 files
- Warning: >1000 lines OR >30 files (suggest split)

### Review Response
- Reply to every comment
- Mark resolved when addressed
- Push fixes as separate commits
- Re-request review when ready

### Before Merge
- All checks passing
- Required reviews obtained
- No merge conflicts
- Up-to-date with base branch
- Commits squashed if requested

## Completion Checklist

After PR workflow assistance:
- [ ] GitHub context verified (auth, SSH, remote)
- [ ] PR description generated from template and user input
- [ ] PR data fetched and saved to temp file
- [ ] User informed of file location
- [ ] Any blocking issues identified (conflicts, failures)
- [ ] Next steps clearly communicated
- [ ] Old temp files cleaned up if needed
