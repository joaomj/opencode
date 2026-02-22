# opencode-config

Personal [opencode](https://opencode.ai) configuration with custom agents, commands, and skills for enhanced AI-assisted development.

## Overview

This repository contains my personal opencode configuration, extending the base opencode CLI with:

- **Dual-agent code review** using independent AI reviewers
- **Documentation maintenance** automation
- **Custom development guidelines** loaded from external sources

## Prerequisites

- [opencode CLI](https://opencode.ai) installed
- API keys configured for model providers (OpenAI, Z.ai)

## Installation

```bash
# Clone to opencode config directory
git clone <repo-url> ~/.config/opencode

# Or symlink if you keep configs elsewhere
ln -s /path/to/this/repo ~/.config/opencode
```

## Configuration

### Model Settings

| Setting | Value | Provider | Purpose |
|---------|-------|----------|---------|
| `small_model` | `zai/glm-4.7` | Z.ai | Session title generation, lightweight tasks |

The `small_model` handles quick operations that don't require high reasoning capacity.

### Permission Settings

Key permissions configured in `opencode.json`:

| Command Pattern | Permission | Notes |
|-----------------|------------|-------|
| `git status`, `git diff`, `git log`, `git show` | allow | Read-only git operations |
| `git *` (other) | ask | Requires approval |
| `cat .env *` | deny | Security: never expose secrets |
| `rm *`, `npm *`, `ssh *`, `brew *`, `docker *` | ask | Destructive/system operations |

## Project Structure

```
~/.config/opencode/
├── opencode.json          # Main configuration (models, permissions, agents)
├── AGENTS.md              # Development guidelines (loaded from joaomj/skills)
├── README.md              # This file
├── agents/
│   ├── code-reviewer-1.md   # GPT-5.3 Codex reviewer (hidden subagent)
│   └── code-reviewer-2.md   # GLM 4.7 reviewer (hidden subagent)
├── commands/
│   ├── review.md            # /review - dual subagent code review
│   └── update-docs.md       # /update-docs - documentation maintenance
└── skills/
    ├── code-review-expert/  # P0-P3 severity checklists
    └── doc-maintenance/     # Documentation pruning guidelines
```

## Available Commands

### `/review`

Performs dual-agent code review with P0-P3 severity classification.

**Usage:**

```bash
# Review current changes vs origin/main
/review

# Review specific branch range
/review from feature-branch to main

# Review a pull request
/review PR #42
```

**How it works:**

1. Two independent subagents analyze the same code:
   - `code-reviewer-1`: GPT-5.3 Codex (high reasoning effort, 0.1 temperature)
   - `code-reviewer-2`: GLM 4.7 (0.1 temperature)
2. Each reviewer returns findings as structured JSON
3. Results are consolidated into `CODE_REVIEW.md`

**Review Coverage:**

- SOLID principles (SRP, OCP, LSP, ISP, DIP)
- Security risks (XSS, injection, SSRF, race conditions)
- Performance issues (N+1 queries, CPU, memory)
- Error handling (swallowed exceptions, async errors)
- Boundary conditions (null, empty, numeric limits)

### `/update-docs`

Automated documentation maintenance that prunes obsolete content.

**Usage:**

```bash
/update-docs
```

**Checks performed:**

- Outdated date references
- References to non-existent components
- Deprecated patterns or APIs
- Data flow mismatches in documentation

## Agents

| Agent | Mode | Model | Temperature | Purpose |
|-------|------|-------|-------------|---------|
| `code-reviewer-1` | subagent (hidden) | `openai/gpt-5.3-codex` | 0.1 | Security and performance focus |
| `code-reviewer-2` | subagent (hidden) | `zai/glm-4.7` | 0.1 | Architecture and SOLID focus |

Both agents:
- Cannot see each other's findings (independent analysis)
- Have write/edit disabled (read-only review)
- Can execute bash commands (limited to `git *` operations)

## Skills

| Skill | Purpose |
|-------|---------|
| `code-review-expert` | Provides P0-P3 severity checklists covering SOLID principles, security, performance |
| `doc-maintenance` | Guidelines for identifying and pruning obsolete documentation |

## Development Guidelines

This configuration references external development guidelines from:

- `https://raw.githubusercontent.com/joaomj/skills/main/AGENTS.md`

These guidelines cover:
- Code quality and best practices
- Security requirements
- Performance optimization
- Documentation standards

## Troubleshooting

### Session names not generating

Ensure `small_model` is set to a working model. If the current model fails, try:

```json
"small_model": "zai/glm-4.7"
```

### Review command not working

Verify that:
1. Git is configured properly
2. The `code-review-expert` skill is present in `skills/`
3. Both reviewer agents have proper frontmatter configuration

## License

See [LICENSE](LICENSE) file for details.
