---
description: Safely update this OpenCode configuration from origin/main
---

Run the deterministic updater. It accepts `--dry-run` (the default) or
`--apply`. Do not run additional Git commands or edit files as part of this
command.

!uv run --no-project python tools/update_opencode.py $ARGUMENTS
