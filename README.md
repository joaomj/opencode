# opencode-config

Personal opencode configuration with custom agents, commands, and skills.

## Structure

```
~/.config/opencode/
  AGENTS.md              # Development guidelines (loaded from joaomj/skills)
  README.md              # This file
  agents/
    code-reviewer-1.md   # GPT-5.3 Codex reviewer (hidden subagent)
    code-reviewer-2.md   # GLM 4.7 reviewer (hidden subagent)
  commands/
    review.md            # /review - dual subagent code review
    update-docs.md       # /update-docs - documentation maintenance
  skills/
    code-review-expert/  # P0-P3 severity checklists
    doc-maintenance/     # Documentation pruning guidelines
```

## Commands

### /review

Dual-subagent code review with P0-P3 severity levels.

```
/review                    # Review git diff origin/main...HEAD
/review from x to main     # Branch comparison
/review PR #42             # Pull request review
```

Invokes two independent reviewers:
- `code-reviewer-1`: GPT-5.3 Codex (high reasoning effort)
- `code-reviewer-2`: GLM 4.7

Outputs `CODE_REVIEW.md` with consolidated findings.

### /update-docs

Documentation maintenance - prunes obsolete content and updates stale sections.

```
/update-docs
```

Checks for:
- Old date references
- Non-existent components
- Deprecated patterns
- Data flow mismatches

## Agents

| Agent | Mode | Model | Purpose |
|-------|------|-------|---------|
| code-reviewer-1 | subagent (hidden) | GPT-5.3 Codex | Independent code review |
| code-reviewer-2 | subagent (hidden) | GLM 4.7 | Independent code review |

## Skills

| Skill | Purpose |
|-------|---------|
| code-review-expert | P0-P3 severity checklists, SOLID, security, performance |
| doc-maintenance | Documentation pruning guidelines and update process |
