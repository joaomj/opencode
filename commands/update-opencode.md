---
description: Safely update this OpenCode configuration from origin/main
---

Run the deterministic updater. It accepts `--preview` (the default) or
`--apply`. Preview fetches `origin/main` and creates a private backup, but does
not merge or commit. Do not run additional Git commands or edit files as part
of this command.

!uv run --no-project python tools/update_opencode.py $ARGUMENTS
