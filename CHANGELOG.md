# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [7.0.0] - 2026-08-30

This release enforces policy rules through OpenCode, hardens credential protection,
and updates model defaults to Muse Spark.

### Added

- Policy enforcement through OpenCode plugin `plugins/policy-gate.ts` with verification scripts `scripts/launch-opencode.sh` and `scripts/verify-policy.ts` to block `OPENCODE_PURE=1` and require policy-gate validation before launch (`609d00b`).
- Lint rules `policy_checks` and `python_budgets` plus enhanced `no_env_file_access` and `no_privileged_containers` for policy and budget checks, with expanded test coverage (`609d00b`).
- Guarded launch documentation in `README.md` and `skills/workflows/direct-assistance/SKILL.md` (`609d00b`, `06d6e47`).
- Provider `opencode/muse-spark-1.2-contributor-free` with context 200k and `reasoningEffort: high` as first-class model option (`e86e601`, `77d366d`).
- Provider `openrouter/z-ai/glm-5.3-flash` with context 200k and `reasoningEffort: high` alongside opencode provider (`77d366d`).
- Dependency `package-lock.json` and `bun.lock` for reproducible installs of `@opencode-ai/plugin` 1.4.6 (`609d00b`).

### Changed

- Default `model` and `small_model` switched from `openai/gpt-5.6-luna-fast` / `openrouter/z-ai/glm-5.3-flash` to `opencode/muse-spark-1.2-contributor-free` (`e86e601`).
- `agent.explore` now uses `opencode/muse-spark-1.2-contributor-free` with `reasoningEffort: high` and `edit: deny` (`77d366d`).
- Cleaned provider list: removed `deepseek/deepseek-v4-flash` and temporary `gpt-5.6-terra-fast` entries, kept `openai/gpt-5.6-luna-fast` and `gpt-5.6-sol-fast` (`77d366d`).
- Permission policy now hard-denies only credential exposure (`*.env`, `.env*`, credential file reads/writes); all other previous `deny` rules for `bash`, `task`, `edit`, and `skill` are soft `ask` via native OpenCode permissions (`06d6e47`).
- `plugins/policy-gate.ts` adds `gist` to `gh` remote-write detection and soft-allows non-credential policy blocks to defer to native `ask` (`06d6e47`).
- `AGENTS.md` adds guidance for long-running commands via detached mode with `nohup`, redirected logs, and background execution (`7bc9adf`).

### Fixed

- Removed small-context `agent.compaction` model override that conflicted with `compaction.auto/prune` settings; compaction now uses auto prune only (`4094d59`).
- Reduced `agent.title` and `agent.compaction` reasoning effort from `none`/`xhigh` to `low` for faster utility execution (`5a2d40f`).
- Fixed plugin detection to keep credential file access hard-denied while allowing verified non-credential operations to prompt (`06d6e47`).

## [6.0.0] - 2026-08-23

- Waterfall delivery route as default; archived legacy skills; reduced linter to core checks; aligned README and workflow docs.

## [5.0.0] - 2026-08-21

- Policy hardening and safety improvements.

## [4.0.0] - 2026-08-01

- Intent-based workflow routing and workflow boundaries.

[Unreleased]: https://github.com/joaomj/opencode/compare/v7.0.0...HEAD
[7.0.0]: https://github.com/joaomj/opencode/compare/v6.0.0...v7.0.0
[6.0.0]: https://github.com/joaomj/opencode/compare/v5.0.0...v6.0.0
[5.0.0]: https://github.com/joaomj/opencode/compare/v4.0.0...v5.0.0
[4.0.0]: https://github.com/joaomj/opencode/releases/tag/v4.0.0
