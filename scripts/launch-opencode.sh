#!/usr/bin/env bash
set -euo pipefail
CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Verify policy plugin loads before launching.
if ! bun "$CONFIG_DIR/scripts/verify-policy.ts"; then
  echo "error: policy verification failed. Fix the plugin before launching." >&2
  exit 1
fi

exec opencode "$@"
