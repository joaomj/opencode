---
description: Stage and commit recent changes with auto-generated conventional commit messages
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
   - Examples of atomic groupings:
     * All files related to a single feature
     * Test files for a specific fix
     * Documentation for a specific API change
   - If unrelated changes exist, create separate commits for each group

3. Stage files for ONE atomic commit at a time:
   - Stage only the files belonging to the current logical group
   - Use: !`git add [specific-files]` for each group
   - NEVER stage all files with `git add -A` or `git add .`
   
5. Check for planning/draft files in staged changes and unstage them:
   !`git diff --staged --name-only`
   
   Scan for files containing these semantic patterns (case-insensitive):
   - PLAN (e.g., implementation-PLAN.md, PLAN-auth.md)
   - TODO (e.g., TODO-list.md, fix-TODO.py)
   - DRAFT (e.g., DRAFT-specs.md)
   - WIP (e.g., WIP-feature.py)
   - TEMP (e.g., TEMP-fix.js)
   - BACKUP (e.g., backup-OLD-code.py)
   - OLD (e.g., OLD-implementation.md)
   
   For each matching file:
   - Unstage it: !`git reset HEAD [filename]`
   - Report: "Excluded [filename] - appears to be planning/draft file"
   
   If uncertain whether a file should be excluded, ask:
   "Should I exclude [filename] from commit? It appears to be a planning/draft file."

6. Analyze remaining staged changes to determine commit type by examining:
   - File types (test files, docs, source code)
   - Change statistics from !`git diff --staged --stat`
   - Content patterns in !`git diff --staged`
   
   Select appropriate type:
   - `feat:` - new features, added functionality, new endpoints, new components
   - `fix:` - bug fixes, corrections, patches
   - `docs:` - documentation changes (README, docs/, comments)
   - `style:` - formatting, whitespace, semicolons, quotes (no logic change)
   - `refactor:` - code restructuring without behavior change
   - `test:` - test files, testing infrastructure, test utilities
   - `chore:` - dependencies, build process, configuration, misc tasks

7. Generate a concise one-line commit message:
   - Maximum 72 characters
   - Format: `<type>: <description>`
   - No scope (no parentheses)
   - Use imperative mood ("Add" not "Added", "Fix" not "Fixed")
   - Examples:
     - "feat: add user authentication endpoints"
     - "fix: resolve null pointer in login flow"
     - "docs: update API reference for v2"
     - "test: add unit tests for auth service"

8. Check for pre-commit hooks and run if installed:
   - Check if `.pre-commit-config.yaml` exists in project root
   - If yes: Run !`pre-commit run --all-files`
   - If hooks fail: Fix issues or report failure and stop
   - If not installed: Ask user:
     "Pre-commit hooks not configured. Would you like me to install them?"
     (Proceed only if user confirms "yes")

9. Show summary and commit:
   - Display: "Committing with message: [generated-message]"
   - Show list of files being committed
   - Execute: !`git commit -m "[generated-message]"`
   - Report success or failure

10. If commit succeeds:
    - Show: "✓ Committed [hash] - [message]"
    - Display short stat of committed changes
    - Check if there are more unstaged files remaining
    - If yes: Ask "Found [N] more modified files. Create another atomic commit?"
    - Repeat process for remaining logical groups if user confirms

**Notes:**
- ATOMIC COMMITS ARE MANDATORY - never stage all files at once
- Each commit must represent a single logical change
- Multiple small commits are better than one large commit
- Always respects .gitignore - no need to manually exclude build artifacts, node_modules, etc.
- Only asks user when uncertain about file classification
- Generates commit messages automatically - user does not write them
- One-line messages only - no multi-line commit bodies
