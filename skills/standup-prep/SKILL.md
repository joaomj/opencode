---
name: standup-prep
description: Generate standup-ready summaries from git activity for daily team meetings
license: MIT
---

# Standup Prep

Generate daily standup summaries from git activity, analyzing your work to create concise reports for team meetings.

## Scope

- Platform: Local git (primary, current repo only) with GitHub CLI fallback (same repo)
- Output: Markdown files in `docs/activity-log/`
- Timeframe: Last 24 hours (configurable, handles weekends)
- Detection: Aggressive blocker detection + manual input

## Workflow

### Step 1: Date Range Detection

Always verify the date - NEVER assume.

```bash
# Get current date
date +%Y-%m-%d
```

**Weekend Handling:**
- If today is Monday, ask: "Review Friday's work or the entire weekend?"
- Default: last 24 hours
- User can specify custom date range if needed

**Date Calculation:**
```bash
# Yesterday (macOS)
date -v-1d +%Y-%m-%d

# Yesterday (Linux)
date -d "yesterday" +%Y-%m-%d

# Last 24 hours
date -d "1 day ago" +%Y-%m-%d
```

### Step 2: Git Activity Collection

**CRITICAL: Only analyze activity within the current repository.**

#### Pre-check: Repository Validation

Always verify repository context FIRST:

```bash
# Check if in a git repository
git rev-parse --is-inside-work-tree

# Get repository identifier (for GitHub scoping)
git remote get-url origin 2>/dev/null || echo "no-remote"
```

If not in a git repository: **STOP** - Error: "Must run inside a git repository"

#### Primary: Local Git (Current Repository)

Always collect local git data first:

```bash
# Get user name
git config user.name

# Commits in date range (current branch)
git log --author="$(git config user.name)" \
  --since="YYYY-MM-DD 00:00:00" \
  --until="YYYY-MM-DD 23:59:59" \
  --pretty=format:"%h|%s|%ad" \
  --date=short

# Commits across all branches (comprehensive view)
git log --all --author="$(git config user.name)" \
  --since="YYYY-MM-DD 00:00:00" \
  --pretty=format:"%h|%s|%ad|%D" \
  --date=short
```

#### Fallback: GitHub CLI (Current Repository Only)

If `gh` is available AND repository has GitHub remote:

```bash
# Check gh availability
gh --version && gh auth status

# Extract owner/repo from remote
REPO=$(git remote get-url origin | sed -E 's|.*github.com[/:]||; s|\.git$||')

# Commits (scoped to current repo)
gh search commits --repo="$REPO" --author=@me --committer-date=YYYY-MM-DD --limit 50

# Pull Requests authored (scoped to current repo)
gh pr list --repo "$REPO" --author=@me --state all --search "updated:>=YYYY-MM-DD" --limit 20

# Pull Requests reviewed (scoped to current repo)
gh pr list --repo "$REPO" --reviewer=@me --state all --search "updated:>=YYYY-MM-DD" --limit 20

# Issues assigned (scoped to current repo)
gh issue list --repo "$REPO" --assignee=@me --state open --limit 20
```

**Auto-enrichment**: When gh is available, automatically supplement local commit data with PR/review info from the same repository.

### Step 3: Work Categorization

Group activity into simple categories:

| Category | Detection Rules |
|----------|----------------|
| **Completed** | Merged PRs, closed issues, commits with keywords: `fix\|feat\|close\|resolve\|implement\|add\|update` |
| **In Progress** | Draft PRs, WIP commits, open PRs, commits with: `WIP\|wip\|work in progress\|in progress` |
| **Reviews** | PRs you reviewed, review comments submitted |

**Categorization Logic:**

1. Parse commit messages for keywords
2. Check PR status (merged = completed, draft = in progress, open = in progress)
3. Identify review activity
4. Group by project/feature if possible

### Step 4: Blocker Detection (Aggressive)

Scan for potential blockers:

| Blocker Type | Detection Pattern | Priority |
|--------------|-------------------|----------|
| **Failed CI** | PR checks with failed status | High |
| **Stale PRs** | PRs open >3 days with no activity | Medium |
| **TODOs/FIXMEs** | `TODO\|FIXME\|XXX\|HACK` in recent commits | Medium |
| **WIP Commits** | Commit messages with `WIP\|wip\|work in progress` | Low |
| **Draft PRs** | PRs in draft state >1 day | Medium |
| **Waiting for Review** | PRs waiting for review >1 day | Medium |
| **Blocked Issues** | Issues with `blocked\|waiting\|stuck` labels | High |

**Detection Commands:**

```bash
# Check for TODOs/FIXMEs in recent commits (GitHub CLI - scoped)
gh search code "TODO OR FIXME OR XXX" --repo="$REPO" --author=@me --committer-date=YYYY-MM-DD

# Check for TODOs/FIXMEs (local git)
git diff HEAD~10 HEAD | grep -E "^\+.*TODO|^\+.*FIXME|^\+.*XXX"

# Check PR checks status (GitHub CLI - scoped)
gh pr checks <pr-number> --repo "$REPO"

# List stale PRs (GitHub CLI - scoped)
gh pr list --repo "$REPO" --author=@me --state open --search "created:<$(date -v-3d +%Y-%m-%d)"

# Find WIP commits (local git)
git log --author="$(git config user.name)" --since="YYYY-MM-DD" --grep="WIP\|wip\|work in progress"
```

### Step 5: User Input Collection

Ask questions **one at a time** (conversational approach):

1. **Blockers Check:**
   ```
   "I found these blockers from your code:
   - [list detected blockers]
   
   Any additional blockers not captured here?"
   ```

2. **Other Activities:**
   ```
   "What activities did you do that aren't in git?
   (meetings, planning, research, mentoring, documentation, etc.)"
   ```

3. **Next Steps:**
   ```
   "What are you planning to work on next?"
   ```

**Important:** Wait for user response before moving to next question.

### Step 6: Output Generation

**Directory Setup:**

```bash
# Create directory if it doesn't exist
mkdir -p docs/activity-log
```

**File Naming:**
- Format: `activities-YYYY-MM-DD.md`
- Example: `activities-2026-03-05.md`

**Output Template:**

```markdown
# Daily Activity - YYYY-MM-DD

## Completed
- [item 1]
- [item 2]

## In Progress
- [item 1]
- [item 2]

## Reviews
- [item 1]
- [item 2]

## Blockers
- [blocker 1]
- [blocker 2]

## Other Activities
- [activity 1]
- [activity 2]

## Next Steps
- [plan 1]
- [plan 2]

---
Generated by standup-prep skill on [timestamp]
```

**File Handling:**
- If file exists: Ask user "File already exists. Overwrite or append?"
- If overwrite: Replace entire file
- If append: Add new section with timestamp

## Error Handling

| Scenario | Action |
|----------|--------|
| Not in git repository | Error: "Must run inside a git repository" |
| No remote configured | Use local git only (skip gh fallback), inform user |
| gh available but repo not on GitHub | Use local git only, inform user |
| Remote URL parse fails | Skip gh fallback, continue with local git |
| `gh` not installed | Use local git fallback, inform user |
| `gh` not authenticated | Use local git fallback, inform user |
| No git activity found | Ask: "No activity found for [date]. Check different date?" |
| `docs/activity-log/` doesn't exist | Create it automatically |
| File already exists | Ask: "Overwrite or append to existing file?" |

## Tool Permissions

Allowed tools:
- `Bash(gh:*)` - GitHub CLI commands
- `Bash(git:*)` - Git commands
- `Bash(date)` - Date operations
- `Bash(mkdir)` - Directory creation
- `Read` - Read existing files
- `Write` - Create new files
- `Edit` - Modify existing files
- `Glob` - Find files

## Example Session

```
User: /standup-prep

Agent: Analyzing your git activity from 2026-03-05...
[Collects commits, PRs, reviews]

Agent: I found these potential blockers:
- PR #42 has failing CI checks (tests failing)
- PR #45 has been waiting for review for 2 days
- 3 TODO comments in recent commits

Any additional blockers not captured here?

User: Yes, I'm also waiting for API credentials from DevOps.

Agent: Got it. What activities did you do that aren't in git?
(meetings, planning, research, mentoring, etc.)

User: Had a 1-hour architecture planning meeting and mentored a junior dev on testing.

Agent: Perfect. What are you planning to work on next?

User: Continue the password reset feature and review the outstanding PR from Sarah.

Agent: Generated your standup summary at docs/activity-log/activities-2026-03-05.md

[Shows preview of the file content]
```

## Non-Negotiable Rules

| Rule | Violation = STOP |
|------|------------------|
| Must be in git repository | Block if not in repo |
| Single repository scope only | Block if multi-repo aggregation detected |
| Local git is mandatory | Block if local git unavailable |
| GitHub CLI is optional | Never fail if gh unavailable |
| Always verify date | Block if date is assumed |
| Ask questions one at a time | Block if multiple questions asked |
| Create output directory if missing | Auto-create `docs/activity-log/` |
| Handle file exists gracefully | Ask before overwriting |

## Completion Checklist

- [ ] Repository validation passed (in git repo)
- [ ] Remote URL parsed (if gh available)
- [ ] Date verified (not assumed)
- [ ] Local git activity collected (mandatory)
- [ ] GitHub CLI data collected (if available, same repo only)
- [ ] Work categorized into Completed/In Progress/Reviews
- [ ] Blockers detected (aggressive scan)
- [ ] User asked about additional blockers
- [ ] User asked about other activities
- [ ] User asked about next steps
- [ ] Output file created at `docs/activity-log/activities-YYYY-MM-DD.md`
- [ ] File content shown to user for review
