# How Enforcement Works

Two layers control one agent action. Both layers must allow the action.
No AI judgment. Same input, same result. Policy version `2.0.0`.

## Policy Gate

`plugins/policy-gate.ts` (`POLICY_VERSION 2.0.0`) does two things: it locks
one workflow for the session and it hard-denies credential paths.

### Credential hard stop

The gate tests every file path and every shell token against:

- `SAFE_ENV_PATH_RE`: `/.env.example` never blocks
- `CREDENTIAL_PATH_RE`: `.env` and `.env.*`, `.npmrc`, `.pypirc`,
  `.git-credentials`, `.netrc`, `.authinfo`, `credentials` and
  `credentials*.json`, `*.credentials.json`, `*.pem`, `*.key`, `id_rsa`,
  `id_ed25519`
- `CREDENTIAL_CONFIG_PATH_RE`: `.docker/config.json`, `.config/gh/hosts.yml`

A match throws `policy-gate: protected credential path blocked` with the
base name. This is the only hard stop. The gate does not show a prompt and it
does not export `approve_action`. Check all command tokens, not only the
first word.

### Workflow ownership

One workflow per session. Request flow:

1. Call `select_workflow` with `workflow`, `reason`, `deliverable`,
   `sideEffectBoundary` (and optional `planPath`). The gate loads the
   workflow instructions and locks the owner.
2. Before the first side effect you can handoff to a different workflow
   with `create_handoff` and `import_handoff`. After the first side effect
   the owner locks. After `create_handoff` the source session becomes
   terminal.

The gate enforces `select_workflow` before:

- Any non-safe `bash` command (anything not in the 17 exact safe commands)
- `webfetch` and `websearch`
- Mutation tools (`apply_patch`, `edit`, `write`) and other non-read tools

Error when missing: `policy-gate: select_workflow before non-read shell
actions` or `select_workflow before external reads`. Read tools
(`read`, `glob`, `grep`, `list`) and `policy_health` run without a workflow.

The gate records side effects: mutation tools and any non-safe, non-verification
`bash` with `exit 0` set `changed=true` and `verification=stale`. Verification
commands (`test`, `check`, `lint`, `format`, `verify`, `typecheck`, `pytest`,
`ruff`, `pyright`, `mypy`) update `verification` to `passed` or `failed`.

### Health check

`policy_health` always returns:

```json
{
  "active": true,
  "policyVersion": "2.0.0",
  "approvalMode": "native-permissions",
  "customApprovalTool": false,
  "sessionID": "ses_..."
}
```

## Native Permissions

`opencode.jsonc` controls all other prompts. The policy gate does not catch or
replace native permission errors. OpenCode owns the Allow or Deny prompt.

- `permission.bash."*": "ask"` — default for shell is ask
- 17 exact safe commands run without a prompt: `pwd`, `date`, `whoami`, `id`,
  `uname -a`, `arch`, `hostname`, `ps`, `tty`, `uptime`, `git status`,
  `git status --short`, `git status --porcelain`, `git diff`,
  `git diff --cached`, `git log`, `git branch` variants, `gh auth status`,
  `gh status`, `docker images`, `docker info`, `docker ps`, `docker version`
- `permission.read."*": "allow"` — normal reads allow, credential reads deny
- `permission.edit."*": "ask"` — normal edits ask, credential edits deny
- `permission.glob`, `grep`, `todowrite`, `question`, `websearch`, `webfetch`,
  `skill` allow by default; `external_directory` asks except `/tmp` and
  `/var/folders` tmp

Ask for one protected action at a time. Include the exact action, target, and
reason. A chat instruction states intent. It does not replace the native
prompt. Preserve the exact native denial reason. If no cause is available,
report `cause unavailable` and identify `native permissions` as the source.

## Final Quality Check

`finish_workflow` is required only if `changed=true`. It excludes documentation
files (`.md`, `.mdx`, `.rst`, and `.txt`) from automatic coding lint. When all
recorded changes are documentation files, it skips the linter. For other known
changes it passes only non-document targets; unknown shell changes use the
project directory. The command is:

```
uv run --project opencode_lint opencode-lint --profile coding <changed-targets-or-project-directory>
```

The result never blocks the workflow. Exit `0` records `passed`. Any other exit
records `failed` and returns the complete linter output to the agent. The output
includes the rule ID, file path, line, column, and specific message. If the
linter returns no output, the agent receives the exit code and an explicit
no-diagnostics reason. Run `opencode-lint <paths>` explicitly when a
documentation change needs lint coverage or a blocking exit code.

Quality lint rules report warnings for non-code content such as Markdown,
reStructuredText, plain text, TOML, and YAML. Security and supply-chain rules
keep error severity for these files.

A successful Git operation is complete. The workflow does not run a redundant
status or diff inspection after success. It inspects again after an error or
when the next action needs unresolved state.

## Denial Causes

| Result | Source | Cause |
|---|---|---|
| Error starts with `policy-gate: protected credential path blocked` | Policy gate | Path matched credential regex |
| Error starts with `policy-gate: select_workflow` | Policy gate | Workflow not selected for non-read or external action |
| `opencode-lint: non-blocking findings` | Policy gate | Linter returned a nonzero exit and included its diagnostics |
| Error `source session is terminal after handoff` | Policy gate | Action after `create_handoff` |
| OpenCode shows Allow or Deny prompt | Native permissions | Rule matched `ask` |
| Native permission error after prompt | Native permissions | Prompt denied or approval service failed |

## Configuration Changes

Restart OpenCode (or `/reload`) after a change to `opencode.jsonc` or
`plugins/policy-gate.ts`. The current process keeps the old policy in memory.
External `git` restores a known-good configuration. Do not use
`OPENCODE_PURE=1` — it disables credential protection; the guarded launch
rejects it.

## Rule

Credential exposure is a hard stop. Native permissions ask for other protected
actions. Same command + same file + same workflow + same approval gives the
same prompt, same allow or deny.
