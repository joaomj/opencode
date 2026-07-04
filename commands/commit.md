---
description: Stage and commit recent changes with auto-generated conventional commit messages
model: opencode/deepseek-v4-flash-free
---

Commit recent changes following these rules:

**CRITICAL: ATOMIC COMMITS ONLY**
- NEVER use `git add -A` or stage all files at once
- Each commit must represent ONE logical change
- Group related files by purpose, not by timing
- Multiple commits are preferred over one large commit

1. Check git status to see what files are modified:
   !`git status --porcelain`

2. Analyze changes and group them into logical atomic units:
   - Review each modified file to understand its purpose
   - Group files that belong to the same logical change
   - If unrelated changes exist, create separate commits for each group

3. Stage files for ONE atomic commit at a time:
   - Stage only the files belonging to the current logical group
   - Use: !`git add [specific-files]` for each group
   - NEVER stage all files with `git add -A` or `git add .`

4. Check for planning/draft files in staged changes and unstage them:
   !`git diff --staged --name-only`

   Scan for files containing these patterns (case-insensitive):
   PLAN, TODO, DRAFT, WIP, TEMP, BACKUP, OLD

   For each matching file:
   - Unstage it: !`git reset HEAD [filename]`
   - Report: "Excluded [filename] - appears to be planning/draft file"

5. Analyze remaining staged changes to determine commit type:
   - `feat:` - new features, added functionality
   - `fix:` - bug fixes, corrections
   - `docs:` - documentation changes
   - `style:` - formatting (no logic change)
   - `refactor:` - code restructuring without behavior change
   - `test:` - test files, testing infrastructure
   - `chore:` - dependencies, build process, configuration

6. Generate a concise one-line commit message:
   - Maximum 72 characters
   - Format: `<type>: <description>`
   - No scope (no parentheses)
   - Imperative mood ("Add" not "Added", "Fix" not "Fixed")
   - No body text (one-line only)

7. Show summary and commit:
   - Display: "Committing with message: [message]"
   - Show list of files being committed
   - Execute: !`git commit -S -m "[message]"`

8. If commit succeeds:
   - Show: "Committed [hash] - [message]"
   - Check if there are more unstaged files remaining
   - Repeat for remaining logical groups if user confirms
