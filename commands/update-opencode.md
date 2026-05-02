---
description: Sync skills, commands, and agents from remote repository with interactive conflict resolution
---

# Update OpenCode from Remote

Sync skills, commands, and agents from the remote repository.
Never touches AGENTS.md or opencode.json.

## Quick Update (Recommended)

If you used the installer script, the fastest way to update is:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/install.sh | bash -s -- --update
```

This re-downloads all components you previously selected using the manifest at `~/.config/opencode/.opencode-manifest`.

## Git-Based Update (Alternative)

If you cloned the repository manually, use the git-based approach below.

## Before You Start

If you previously set up the shell-based auto-update (the `opencode()` function in `.zshrc` or `.bashrc`), remove it now. This command replaces that entirely.

## Step 1: Verify Context

Run:
!`pwd`
!`git -C "$HOME/.config/opencode" remote -v`

If not in ~/.config/opencode or no remote configured:
STOP with error "Must run from ~/.config/opencode with a configured remote."

## Step 2: Fetch Latest

!`git -C "$HOME/.config/opencode" fetch origin master`

If fetch fails: STOP with error "Could not fetch from remote."

## Step 2.5: Verify Remote Integrity

Check if fetched commits are GPG-signed:
!`git -C "$HOME/.config/opencode" log --show-signature -1 origin/master`

If unsigned, show warning: "Remote HEAD is not GPG-signed. Proceed with caution."
Continue anyway (allow.sh override) — do not block, just warn.

## Step 3: Compare Remote vs Local

For each directory in scope (skills/, commands/, agents/), list remote files:
!`git -C "$HOME/.config/opencode" ls-tree -r --name-only origin/master -- skills/ commands/ agents/`

For each remote file, compare with local version:
!`git -C "$HOME/.config/opencode" diff --quiet HEAD origin/master -- <file>`

Categorize every file as:
- **unchanged**: local matches remote
- **modified**: content differs between local and remote
- **new**: exists on remote but not locally
- **deleted**: exists locally but not on remote (show as "new" since from local perspective it appears new)
- **local-only**: exists locally but not on remote (never flag these, leave untouched)

## Step 4: Present Summary

Show a table of ONLY files that differ:

| File | Status | Action needed |
|------|--------|---------------|
| skills/x/SKILL.md | modified | choose |
| commands/new.md | new | choose |

If no differences: "All skills, commands, and agents are up to date."
Then skip to Step 7 (opencode.json.example) and end.

## Step 5: Interactive Resolution (one file at a time)

For EACH file with status modified, new, or deleted:

Show the filename and a brief diff summary (first 10 lines of diff).

Ask the user:
"File: <path> (<status>)"
  1. **Overwrite** - replace local with remote version
  2. **Keep local** - ignore this remote change
  3. **Show both** - display full local and remote versions side by side, then let user decide

If user chose "Show both":
- Display the full remote version
- Display the full local version
- Ask again: overwrite, keep local, or manually specify what to keep

## Step 6: Apply Choices

For each "overwrite" choice:
!`git -C "$HOME/.config/opencode" checkout origin/master -- <file>`

For each "keep local": do nothing.

Report applied changes.

## Step 7: Download opencode.json Example

Always download the remote opencode.json as an example (never overwrites user config):
!`git -C "$HOME/.config/opencode" show origin/master:opencode.json > "$HOME/.config/opencode/opencode.json.example"`

Report: "Remote config saved as opencode.json.example"

## Step 8: Final Report

Show:
- Files overwritten: [count and list]
- Files kept local: [count and list]
- New files adopted: [count and list]
- Files deleted: [count and list]
- opencode.json.example: updated

## Important Rules

- NEVER modify AGENTS.md
- NEVER modify opencode.json
- NEVER modify files outside skills/, commands/, agents/
- NEVER proceed without user confirmation for each changed file
- NEVER run automatically - this command is user-triggered only
