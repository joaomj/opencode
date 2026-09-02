---
description: Stage and commit recent changes using repository conventions
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

7. Read repository commit guidance and analyze staged changes to determine the
   repository-required commit type and scope:
   - `feat:` - new features, added functionality
   - `fix:` - bug fixes, corrections
   - `docs:` - documentation changes
   - `style:` - formatting (no logic change)
   - `refactor:` - code restructuring without behavior change
   - `test:` - test files, testing infrastructure
   - `chore:` - dependencies, build process, configuration

8. Generate a concise commit message that follows ASD-STE100 and the
    repository and organization conventions per `AGENTS.md` field table.
    Use an imperative subject and include a body only when the convention needs
    context. Do not replace repository rules with a global length or scope rule.

9. Show summary and commit:
   - Display: "Committing with message: [message]"
   - Show list of files being committed
   - Execute: !`git commit -S -m "[message]"`

10. If commit succeeds: "Committed [hash] - [message]". Treat the commit as
    complete. Do not run a post-commit status inspection.
