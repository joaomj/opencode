---
description: Generate daily standup summary from git activity
---

# Standup Prep

Generate daily standup summaries from git activity.

## Workflow

### Step 1: Verify Context

```bash
git rev-parse --is-inside-work-tree
git config user.name
date +%Y-%m-%d
```

If not in a git repo: STOP with error "Must run inside a git repository."

If today is Monday, ask: "Review Friday's work or the entire weekend?"

### Step 2: Collect Activity

```bash
# Commits today (current user)
git log --author="$(git config user.name)" \
  --since="YYYY-MM-DD 00:00:00" \
  --until="YYYY-MM-DD 23:59:59" \
  --pretty=format:"%h|%s|%ad" \
  --date=short

# All branches view
git log --all --author="$(git config user.name)" \
  --since="YYYY-MM-DD 00:00:00" \
  --pretty=format:"%h|%s|%ad|%D" \
  --date=short
```

If `gh` is available and repo has GitHub remote:

```bash
REPO=$(git remote get-url origin | sed -E 's|.*github.com[/:]||; s|\.git$||')
gh pr list --repo "$REPO" --author=@me --state all --search "updated:>=YYYY-MM-DD" --limit 20
gh issue list --repo "$REPO" --assignee=@me --state open --limit 20
```

GitHub CLI is optional. If unavailable, use local git only.

### Step 3: Categorize

| Category | Detection |
|----------|-----------|
| **Completed** | Merged PRs, closed issues, commits with fix/feat/close/resolve |
| **In Progress** | Draft PRs, open PRs, WIP commits |
| **Reviews** | PRs reviewed, review comments |

### Step 4: Ask User (one question at a time)

1. "I found these potential blockers: [list]. Any additional blockers?"
2. "What activities did you do that aren't in git? (meetings, planning, research, etc.)"
3. "What are you planning to work on next?"

### Step 5: Generate Output

```bash
mkdir -p docs/activity-log
```

File: `docs/activity-log/activities-YYYY-MM-DD.md`

```markdown
# Daily Activity - YYYY-MM-DD

## Completed
- [items from git/gh]

## In Progress
- [items]

## Reviews
- [items]

## Blockers
- [detected + user-provided]

## Other Activities
- [user-provided]

## Next Steps
- [user-provided]
```

If file exists: ask "Overwrite or append?"

## Error Handling

| Scenario | Action |
|----------|--------|
| Not in git repo | STOP |
| No activity found | Ask: "Check different date?" |
| gh not available | Use local git only |
| File exists | Ask: "Overwrite or append?" |
