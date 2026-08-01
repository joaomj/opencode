---
name: improve-agent
description: Analyze global OpenCode session history and configuration for evidence-based agent improvements, conflicts, redundancy, staleness, and risk. Use when the user invokes `/improve-agent` or asks to audit the global agent setup.
disable-model-invocation: true
---

# Improve Agent

Audit the global OpenCode setup and return proposals. Do not change files or
settings.

## Scope

Inspect only the global OpenCode setup:

- `~/.config/opencode/opencode.jsonc`
- `~/.config/opencode/AGENTS.md`
- `~/.config/opencode/commands/**/*.md`
- `~/.config/opencode/skills/**/SKILL.md`
- Global agent files and configured global plugins or tools
- `~/.local/share/opencode/opencode.db`, when it exists

Do not inspect project-local `.opencode` files unless the user explicitly asks.
Do not inspect `.env` files or environment values.

Use the command arguments as an optional focus. Keep the global scope even when
the focus names a specific skill, command, tool, or plugin.

## Safety Rules

- Perform a read-only audit.
- Do not use `edit`, `apply_patch`, `write`, `delete`, install, or mutation tools.
- Do not modify the configuration, skills, commands, plugins, or session data.
- Do not execute an audited plugin or tool as part of the audit.
- Treat a recommendation to remove, disable, merge, or rewrite as a proposal.
- Never include secrets, tokens, environment values, or full private messages in
  the report.
- Redact sensitive values from short evidence excerpts.
- Surface read, parse, query, or analysis failures. Do not silently skip them.

## Method

### 1. Inventory the global setup

Build an inventory before making recommendations. Record the path, artifact
type, frontmatter or configuration identity, and approximate size for each item.

Check that:

- Skill names match their directories.
- Skills have useful `name` and `description` frontmatter.
- Command files have a description and a usable template.
- Referenced files, directories, commands, and plugins exist.
- Configured agents, skills, commands, and plugins use supported locations.
- Instruction sources are visible, ordered, and not duplicated without reason.

Inspect plugin and tool source statically. Identify capabilities such as shell
execution, file writes, network access, environment access, subprocesses, and
startup-time side effects. Do not run the source.

### 2. Analyze session history

Use the OpenCode session database in read-only mode when it is available. Start
with metadata and aggregate queries. Read message or tool text only when it is
needed to verify a pattern.

Look for repeated evidence of:

- User corrections to agent behavior or output format.
- Repeated failed commands, permission blocks, or recovery steps.
- Repeated tool loops, unnecessary delegation, or context waste.
- Tasks that repeatedly require the same missing procedure.
- Skills or commands that activate but do not help the task.
- Successful procedures that should become reusable guidance.
- Configuration or instruction changes that follow recurring friction.

Do not treat one session as proof of a general pattern. State the sample size,
time range, and evidence strength for each session-based finding.

### 3. Sanitize the global setup

Check for these conditions:

- **Overlap:** Two or more artifacts target the same task, trigger, or output.
- **Redundancy:** The same rule or procedure appears in multiple places.
- **Conflict:** Artifacts give incompatible instructions or tool behavior.
- **Staleness:** An artifact is unused, references missing resources, names an
  old interface, or no longer matches the current OpenCode setup.
- **Risk:** An artifact has broad authority, hidden side effects, unsafe code, or
  permissions that exceed its stated purpose.
- **Context cost:** Long or repeated instructions consume context without clear
  benefit.
- **Trigger quality:** A skill or command is too broad, too vague, or likely to
  activate for unrelated work.
- **Missing capability:** Session evidence shows a recurring need with no clear
  reusable skill, command, or configuration support.

Unused does not mean obsolete. Mark unused artifacts as candidates for review
unless other evidence supports a stronger conclusion.

For conflicts, report the competing instructions and their sources. Do not
invent a precedence rule that is not documented or observed.

### 4. Form proposals

For each proposal, select one action:

- Keep
- Clarify
- Narrow
- Merge
- Rewrite
- Archive
- Remove
- Create
- Restrict

Do not apply the action. Include the affected paths, evidence, expected benefit,
possible regression, and a concise patch or content sketch when useful.

## Report

Return the report in this order:

1. **Scope and coverage**
   - Audited paths and session range.
   - Files or data that were unavailable.
   - Failures that reduced confidence.
2. **Executive summary**
   - The most important findings.
   - The highest-value proposals.
3. **Session patterns**
   - Recurring behavior, evidence, and confidence.
4. **Configuration findings**
   - Overlap, redundancy, conflict, staleness, risk, and context cost.
5. **Proposals**
   - One proposal per finding.
   - Action, affected paths, rationale, benefit, risk, and patch sketch.
6. **Open questions**
   - Decisions that require user input.

Use this record for each finding:

```text
ID: IA-001
Category: session-pattern | overlap | redundancy | conflict | staleness | risk | context-cost | missing-capability
Severity: critical | high | medium | low
Confidence: high | medium | low
Evidence: ...
Affected paths: ...
Finding: ...
Proposal: ...
Risk: ...
```

End by stating clearly that no changes were applied and that each proposal needs
user approval.
