# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [8.0.0] - 2026-08-31

This release simplifies policy enforcement to a deterministic credential-only hard stop
with native OpenCode prompts for all other protected actions. Policy-gate moves to
`2.0.0` (`approvalMode: native-permissions`, `customApprovalTool: false`) and the
permission policy, documentation, and diagrams are synchronized to that behavior
(`4c32673`, `9484b09`, docs `ses_faa14d62fffeIPfKvAWhww8wgD`).

### Added

- Paired enforcement diagrams `docs/enforcement-flow.html` (interactive) and
  `docs/enforcement-flow.svg` (static) with deterministic three-checkpoint view
  and `policy_health` evidence (`ses_faa14d62fffeIPfKvAWhww8wgD · 4c32673 ·
  policy 2.0.0 native-permissions · opencode 1.18.25 · plugin 1.4.6`).
- Expanded `docs/enforcement-explained.md` to document `POLICY_VERSION 2.0.0`,
  credential regexes (`SAFE_ENV_PATH_RE`, `CREDENTIAL_PATH_RE`,
  `CREDENTIAL_CONFIG_PATH_RE`), workflow ownership (`select_workflow` before
  non-safe `bash`, `webfetch`/`websearch`, mutation tools), handoff terminal
  state, side-effect tracking, and `finish_workflow` `opencode_lint --profile
  coding` verification (`docs` sync).

### Changed

- `plugins/policy-gate.ts` reduced from ~874 to ~505 lines (`4c32673`): removed
  `effect` dependency and `PLUGIN_API_VERSION`/`SELF_REPAIR` logic, kept
  `POLICY_VERSION 2.0.0`, credential hard stop as the only blocking regex (all
  tokens checked), `select_workflow` lock after first side effect,
  `create_handoff`/`import_handoff` lifecycle, and `finish_workflow` linter gate.
  `policy_health` now reports `{ active: true, policyVersion: 2.0.0,
  approvalMode: native-permissions, customApprovalTool: false }`. No
  `approve_action` export; native prompts own approval.
- `opencode.jsonc` trimmed from ~352 permission lines to 72 (`4c32673`):
  removed fine-grained `git push --force`, `gh api --method`, `gh gist` etc.
  rules; kept `permission.bash."*": ask` with 17 exact safe allows (`pwd`,
  `date`, `whoami`, `id`, `uname -a`, `arch`, `hostname`, `ps`, `tty`,
  `uptime`, `git status`/`log`/`branch`, `gh auth status`, `gh status`,
  `docker images/info/ps/version`), `permission.read."*": allow` with credential
  deny, `permission.edit."*": ask`, and tmp allow for `external_directory`.
- `plugins/policy-gate.test.ts` expanded to verify credential hard deny (including
  `.env.example` allow), safe-env pass, workflow-selected defer to native `ask`,
  and `customApprovalTool: false`.
- `AGENTS.md` adds native approval guidance: request one native approval at a
  time with action/target/reason, preserve exact native denial reason or report
  `cause unavailable`, and report stage progress after 5 minutes.
- `README.md` updates Policy Plugin section to native permissions, `policy_health`
  example, and `OPENCODE_PURE=1` rejection via guarded launch.
- Commands `code-review`, `create-pr`, `implementation-plan`, `improve-agent`,
  `project-opportunities`, `write-postmortem` simplified to one-line workflow
  selectors (`Select and follow the … workflow`).
- `skills/engineering/workflow/SKILL.md` simplified to single-workflow selection,
  deterministic gates, and handoff rules.
- `bun.lock` upgrades `@opencode-ai/plugin` `1.3.13` → `1.4.6` and `@opencode-ai/sdk`
  `1.3.13` → `1.4.6` with `effect 4.0.0-beta.48` and `msgpackr` prebuilds.
- `scripts/launch-opencode.sh` and `scripts/verify-policy.ts` aligned to reject
  `OPENCODE_PURE=1` and validate `2.0.0` health without self-repair allowlist.

### Removed

- Removed `SELF_REPAIR_ENV`/`SELF_REPAIR_ACTION`/`SELF_REPAIR_ALLOWLIST`,
  `PLUGIN_API_VERSION`, and `Effect` import from policy-gate.
- Removed 250+ narrow `opencode.jsonc` permission entries for `git push`,
  `docker --privileged`, `curl`, and `gh api/agent-task/alias/auth` variants.

### Fixed

- Ensures `.env`, `.env.*`, `.npmrc`, `.pypirc`, `.git-credentials`, `.netrc`,
  `.authinfo`, `credentials*.json`, `*.pem`/`*.key`, `id_rsa`/`id_ed25519`,
  `.docker/config.json`, `.config/gh/hosts.yml` remain hard `deny` in both
  `opencode.jsonc` and policy-gate while `.env.example` stays `allow`.

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

[Unreleased]: https://github.com/joaomj/opencode/compare/v8.0.0...HEAD
[8.0.0]: https://github.com/joaomj/opencode/compare/v7.0.0...v8.0.0
[7.0.0]: https://github.com/joaomj/opencode/compare/v6.0.0...v7.0.0
[6.0.0]: https://github.com/joaomj/opencode/compare/v5.0.0...v6.0.0
[5.0.0]: https://github.com/joaomj/opencode/compare/v4.0.0...v5.0.0
[4.0.0]: https://github.com/joaomj/opencode/releases/tag/v4.0.0
