#!/usr/bin/env bash
set -euo pipefail
CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Reject pure mode unless explicit narrow repair is requested.
if [[ "${OPENCODE_PURE:-}" == "1" && "${OPENCODE_POLICY_REPAIR:-}" != "1" ]]; then
  echo "error: OPENCODE_PURE=1 is blocked. The policy plugin is required." >&2
  echo "  Use OPENCODE_POLICY_REPAIR=1 for narrow self-repair of policy files," >&2
  echo "  or run: bun \"$CONFIG_DIR/scripts/verify-policy.ts\" to diagnose." >&2
  exit 1
fi

# Verify policy plugin loads before launching.
if ! bun "$CONFIG_DIR/scripts/verify-policy.ts"; then
  echo "error: policy verification failed. Fix the plugin before launching." >&2
  echo "  Narrow repair: OPENCODE_POLICY_REPAIR=1 opencode" >&2
  echo "  Full bypass (not recommended): OPENCODE_PURE=1 is blocked by default." >&2
  exit 1
fi

exec opencode "$@"
