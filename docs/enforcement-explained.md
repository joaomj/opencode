# How Enforcement Works

Two layers control an action. Both layers must allow the action.

## Policy Gate

`plugins/policy-gate.ts` selects one workflow and protects credential paths.

The policy gate hard-denies access to these credential files:

- `.env` files
- Package-manager credential files
- Private keys
- Cloud credential files
- GitHub and Docker credential files

The denial starts with `policy-gate:` and includes the protected file name.
The policy gate does not ask for approval. It does not export `approve_action`.

Use `policy_health` to confirm the approval mode:

```json
{
  "approvalMode": "native-permissions",
  "customApprovalTool": false
}
```

## Native Permissions

`opencode.jsonc` controls all other actions.

- Exact safe commands run without a prompt.
- Normal file reads run without a prompt.
- Normal file edits require a prompt.
- Other shell commands require a prompt.
- Credential reads and edits are denied.

OpenCode owns these prompts. The policy gate does not catch or replace native
permission errors.

Ask for one protected action at a time. Include the exact action, target, and
reason. An instruction in chat states user intent. It does not replace the
native permission prompt.

## Denial Causes

| Result | Source | Cause |
|---|---|---|
| Error starts with `policy-gate:` | Policy gate | The action uses a credential path or violates workflow state. |
| OpenCode shows an Allow or Deny prompt | Native permissions | The action matches an `ask` rule. |
| Native permission error | Native permissions | The prompt was denied or the approval service failed. |
| `finish_workflow blocked` | Policy gate | The coding linter failed. |

Preserve the exact native error. If OpenCode does not return a cause, report
`cause unavailable` and identify native permissions as the source.

## Configuration Changes

Restart OpenCode after a change to `opencode.jsonc` or `policy-gate.ts`. The
current process keeps the old policy in memory.

## Rule

Credential exposure is a hard stop. Native permissions ask for other protected
actions.
