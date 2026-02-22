# opencode-config

Personal [opencode](https://opencode.ai) configuration with development guidelines, custom agents, commands, and skills for enhanced AI-assisted development.

## Overview

This repository contains a comprehensive opencode configuration with:

- **Development Guidelines** - Python, Docker, ML, and workflow best practices
- **Dual-agent code review** using independent AI reviewers
- **Documentation maintenance** automation
- **Pre-commit hooks** for quality enforcement

## Prerequisites

- [opencode CLI](https://opencode.ai) installed
- API keys configured for model providers (OpenAI, Z.ai)

## Installation

```bash
# Clone to opencode config directory
git clone https://github.com/joaomj/opencode.git ~/.config/opencode

# Or symlink if you keep configs elsewhere
ln -s /path/to/this/repo ~/.config/opencode
```

## Project Structure

```
~/.config/opencode/
├── AGENTS.md              # Main guidelines index (references local instructions/)
├── opencode.json          # Main configuration (models, permissions, agents)
├── README.md              # This file
├── CHANGELOG.md           # Version history
├── setup-hooks.sh         # Pre-commit hooks installer
├── instructions/          # Development guidelines (self-contained)
│   ├── python/            # Python best practices (6 files)
│   ├── docker/            # Docker security (4 files)
│   ├── ml/                # Machine learning methodology (6 files)
│   ├── workflow/          # Development workflows (3 files)
│   ├── tools/             # External tool usage (1 file)
│   ├── pyproject.toml     # Ruff configuration template
│   ├── .pre-commit-config.yaml  # Pre-commit hooks template
│   └── check_file_length.py     # File length validation script
├── skills/                # OpenCode native skills
│   ├── code-review-expert/
│   └── doc-maintenance/
├── agents/                # Subagent configurations
│   ├── code-reviewer-1.md
│   └── code-reviewer-2.md
└── commands/              # OpenCode commands
    ├── review.md
    └── update-docs.md
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

### `/update-docs`

Automated documentation maintenance that prunes obsolete content.

**Usage:**

```bash
/update-docs
```

## Skills

| Skill | Purpose | Invoke |
|-------|---------|--------|
| `code-review-expert` | P0-P3 severity checklists covering SOLID principles, security, performance | `/skill code-review-expert` |
| `doc-maintenance` | Guidelines for identifying and pruning obsolete documentation | `/skill doc-maintenance` |

## Pre-Commit Hooks

Enable automatic quality checks in any project:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash
```

This installs hooks that check for:
- **Secrets** - gitleaks detects hardcoded secrets
- **File length** - max 300 lines per Python file
- **Formatting** - ruff ensures proper code formatting
- **Dockerfile** - hadolint enforces best practices
- **No main commits** - prevents direct commits to main/master

## Development Guidelines

The `instructions/` directory contains detailed guidelines organized by domain:

### Python (`instructions/python/`)
- Type hints and Pydantic patterns
- Error handling strategies
- Ruff configuration and rules
- Structured logging requirements
- Comprehensive testing guidelines

### Docker (`instructions/docker/`)
- Dockerfile security best practices
- Runtime security flags
- Compose templates
- Network isolation strategies

### Machine Learning (`instructions/ml/`)
- CRISP-DM methodology
- Data splitting strategies
- Leakage prevention
- Evaluation metrics
- Feature importance analysis
- MLflow experiment tracking

### Workflow (`instructions/workflow/`)
- Investigation and planning
- Task management with testable checkpoints
- PR description templates

### Tools (`instructions/tools/`)
- Context7 API for up-to-date library documentation

## Multi-Machine Setup

This repo is designed to work consistently across multiple machines. After cloning to `~/.config/opencode/` on each machine, all instances will automatically use the same guidelines and configurations.

To update all machines after making changes:

```bash
cd ~/.config/opencode
git pull origin main
```

## Configuration

### Model Settings

| Setting | Value | Provider | Purpose |
|---------|-------|----------|---------|
| `small_model` | `zai/glm-4.7` | Z.ai | Session title generation, lightweight tasks |

### Permission Settings

Key permissions configured in `opencode.json`:

| Command Pattern | Permission | Notes |
|-----------------|------------|-------|
| `git status`, `git diff`, `git log`, `git show` | allow | Read-only git operations |
| `git *` (other) | ask | Requires approval |
| `cat .env *` | deny | Security: never expose secrets |
| `rm *`, `npm *`, `ssh *`, `brew *`, `docker *` | ask | Destructive/system operations |

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
