---
description: Stage and commit recent changes with auto-generated conventional commit messages
---

Commit recent changes following these rules:

1. Check git status to see what files are modified:
   !`git status --porcelain`

2. Stage all modified files (git automatically respects .gitignore):
   !`git add -A`

3. Check for planning/draft files in staged changes and unstage them:
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

4. Analyze remaining staged changes to determine commit type by examining:
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

5. Generate a concise one-line commit message:
   - Maximum 72 characters
   - Format: `<type>: <description>`
   - No scope (no parentheses)
   - Use imperative mood ("Add" not "Added", "Fix" not "Fixed")
   - Examples:
     - "feat: add user authentication endpoints"
     - "fix: resolve null pointer in login flow"
     - "docs: update API reference for v2"
     - "test: add unit tests for auth service"

6. Check for pre-commit hooks and run if installed:
   - Check if `.pre-commit-config.yaml` exists in project root
   - If yes: Run !`pre-commit run --all-files`
   - If hooks fail: Fix issues or report failure and stop
   - If not installed: Ask user:
     "Pre-commit hooks not configured. Would you like me to install them?"
     (Proceed only if user confirms "yes")

7. Show summary and commit:
   - Display: "Committing with message: [generated-message]"
   - Show list of files being committed
   - Execute: !`git commit -m "[generated-message]"`
   - Report success or failure

8. If commit succeeds:
   - Show: "✓ Committed [hash] - [message]"
   - Display short stat of committed changes

**Notes:**
- Always respects .gitignore - no need to manually exclude build artifacts, node_modules, etc.
- Only asks user when uncertain about file classification
- Generates commit messages automatically - user does not write them
- One-line messages only - no multi-line commit bodies
