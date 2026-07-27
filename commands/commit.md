---
description: Stage and commit recent changes with auto-generated conventional commit messages
model: opencode/deepseek-v4-flash-free
---

Commit recent changes. Do not fetch, rebase, or merge.

1. Check git status to see changed files:
   !`git status --porcelain`

2. Categorize all changes (modified, staged, untracked) into:

   - **Allowed** - source files, tests, configs, infrastructure code
   - **Planning/temp** - files whose names contain (case-insensitive):
     PLAN, TODO, DRAFT, WIP, TEMP, BACKUP, OLD
     Also exclude dotfiles at root level, .env files, and local configs.
   - **Uncertain** - anything that doesn't clearly fit either category

3. Show the user the full file list split by category:
   "Planning/temp files (will be excluded):
    - file1, file2
   Allowed files (will be committed):
    - file3, file4
   Uncertain files:
    - file5"

4. If there are uncertain files, ask the user: "Should I exclude or include [file]?"
   Let the user decide for each uncertain file.

5. Also ask: "Any files from the allowed list you want to keep out of this commit?"

6. Stage all remaining allowed files:
   !`git add [file1 file2 ...]`

7. Analyze staged changes to determine commit type:
   - `feat:` - new features, added functionality
   - `fix:` - bug fixes, corrections
   - `docs:` - documentation changes
   - `style:` - formatting (no logic change)
   - `refactor:` - code restructuring without behavior change
   - `test:` - test files, testing infrastructure
   - `chore:` - dependencies, build process, configuration

8. Generate a concise one-line commit message:
   - Maximum 72 characters
   - Format: `<type>: <description>`
   - No scope (no parentheses)
   - Imperative mood ("Add" not "Added", "Fix" not "Fixed")
   - No body text (one-line only)

9. Show summary and commit:
   - Display: "Committing with message: [message]"
   - Show list of files being committed
   - Execute: !`git commit -S -m "[message]"`

10. If commit succeeds: "Committed [hash] - [message]"

    If unstaged changes remain, ask the user if they want a second commit.
