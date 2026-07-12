---
description: Stage and commit recent changes with auto-generated conventional commit messages
model: opencode/deepseek-v4-flash-free
---

Commit recent changes. Do not fetch, rebase, or merge.

1. Check git status to see what files are modified:
   !`git status --porcelain`

2. Scan all changes for planning/draft files once:
   !`git diff --name-only` and !`git ls-files --others --exclude-standard`

   Check for files containing these patterns (case-insensitive):
   PLAN, TODO, DRAFT, WIP, TEMP, BACKUP, OLD

   For each matching file:
   - Exclude it: !`git reset HEAD [filename]` if staged, otherwise note it
   - Report: "Excluded [filename] - appears to be planning/draft file"

3. Stage all remaining changes:
   !`git add -A`

4. Analyze staged changes to determine commit type:
   - `feat:` - new features, added functionality
   - `fix:` - bug fixes, corrections
   - `docs:` - documentation changes
   - `style:` - formatting (no logic change)
   - `refactor:` - code restructuring without behavior change
   - `test:` - test files, testing infrastructure
   - `chore:` - dependencies, build process, configuration

5. Generate a concise one-line commit message:
   - Maximum 72 characters
   - Format: `<type>: <description>`
   - No scope (no parentheses)
   - Imperative mood ("Add" not "Added", "Fix" not "Fixed")
   - No body text (one-line only)

6. Show summary and commit:
   - Display: "Committing with message: [message]"
   - Show list of files being committed
   - Execute: !`git commit -S -m "[message]"`

7. If commit succeeds: "Committed [hash] - [message]"

   If unstaged changes remain after all above, ask user if they want a second commit.
