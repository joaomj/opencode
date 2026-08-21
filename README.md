# OpenCode Config

A personal [OpenCode](https://opencode.ai) setup for planning, building, and
reviewing software with a consistent and safety-focused workflow.

Use this repository as a ready-to-use global configuration or as a starting
point for your own setup.

## What You Get

- Guided workflows for requests from discovery through delivery.
- Reusable commands for plans, reviews, pull requests, releases, and more.
- Skills for research, debugging, testing, and documentation.
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

## Update

Use `/update-opencode` when you want to update this setup from `origin/main`.
The command uses preview mode by default. Preview fetches the remote branch and
creates a backup without merging or committing.

Apply an approved update with:

```text
/update-opencode --apply
```

Restart OpenCode after you change `opencode.jsonc`, plugins, commands, or
skills.

For a manual checkout update, use:

```bash
git -C ~/.config/opencode pull --ff-only
```

Review local changes before updating if you have customized the configuration.

## Releases

Use semantic version tags for releases:

- Increase the patch number for backward-compatible fixes.
- Increase the minor number for backward-compatible features.
- Increase the major number when command, skill, or permission behavior breaks.

Use `/release <version>` to publish a GitHub release with GitHub-generated
release notes.

## Disclaimer

This is a personal configuration. It is not built by the OpenCode team and is
not affiliated with OpenCode or Anomaly.

## License

[MIT](LICENSE)
