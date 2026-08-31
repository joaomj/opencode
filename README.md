# OpenCode Config

A personal [OpenCode](https://opencode.ai) setup for planning, building, and
reviewing software with a consistent and safety-focused workflow.

Use this repository as a ready-to-use global configuration or as a starting
point for your own setup.

## What You Get

- Guided workflows for requests from discovery through delivery.
- Reusable commands for plans, reviews, pull requests, releases, and more.
- Skills for research, testing, delivery, and documentation.
- Safe defaults for file changes, shell commands, and local secrets.

## Quick Start

1. [Install OpenCode](https://opencode.ai/docs).
2. Clone this repository to OpenCode's global configuration directory (backup your own settings first!!):

   ```bash
   git clone https://github.com/joaomj/opencode.git ~/.config/opencode
   ```

3. Start OpenCode in any project:

   ```bash
   opencode
   ```

If `~/.config/opencode` already contains your configuration, back it up before
you clone this repository.

Restart OpenCode after you change `opencode.jsonc`, plugins, commands, or
skills.

Archived skills remain under `archive/skills/` for local recovery and are not
loaded by OpenCode.

## Policy Plugin

The policy gate (`plugins/policy-gate.ts`) protects credential paths and tracks
workflow ownership and verification. Native OpenCode permissions ask before
other protected actions.

`policy_health` reports `approvalMode: "native-permissions"`. The plugin does
not wrap native denials or provide a custom approval tool.

- Check health: `bun scripts/verify-policy.ts`
- Guarded launch: `bash scripts/launch-opencode.sh`

The guarded launch rejects `OPENCODE_PURE=1` because pure mode disables
credential protection. Use external Git to restore a known-good configuration.

## Releases

Use semantic version tags for releases:

- Increase the patch number for backward-compatible fixes.
- Increase the minor number for backward-compatible features.
- Increase the major number when command, skill, or permission behavior breaks.

Use `/release <version>` to publish a user-approved GitHub release with
GitHub-generated release notes.

## Disclaimer

This is a personal configuration. It is not built by the OpenCode team and is
not affiliated with OpenCode or Anomaly.

## License

[MIT](LICENSE)
