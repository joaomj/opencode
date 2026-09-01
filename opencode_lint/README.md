# OpenCode Lint

A standalone Python linter that checks repository policies through the
pre-commit hook chain. It runs as both a CLI (`opencode-lint`) and a single
pre-commit hook. A target repository does not need an `AGENTS.md` file.

## Installation

```bash
uv sync --project opencode_lint
```

Or set up pre-commit hooks:
```bash
uvx pre-commit install
```

## Usage

### As CLI
```bash
# Check all files in current directory
opencode-lint

# Check specific files
opencode-lint src/main.py tests/

# Run the coding profile
opencode-lint --profile coding

# Run the fast profile on staged files
opencode-lint --profile fast --staged

# Pre-commit mode (exit code 1 on any violation)
opencode-lint --pre-commit path/to/file.py
```

Directory scans cover source and configuration files. Documentation is checked
only when its path is passed explicitly.

### As Pre-commit Hook
The hook passes staged source and configuration filenames to the fast profile.
Documentation files are excluded from the default hook. Run the CLI explicitly
when documentation lint coverage is needed. The linter checks files without
changing them.

## Rules

| Rule ID | Description | Severity | Enforced By |
|---------|-------------|----------|-------------|
| OC002 | Never read/print `.env` values | Error | `opencode_lint` |
| OC003 | No privileged containers | Error | `opencode_lint` |
| OC012 | No shell-piped remote install scripts; use explicit verified steps | Error | `opencode_lint` |
| LNT004 | Broad checker suppressions | Error | `opencode_lint` |
| LNT005 | Test skips and expected failures need reasons | Error | `opencode_lint` |
| LNT020 | Mechanical writing rules | Warning | `opencode_lint` |
| LNT022 | Required checks fail closed | Error | `opencode_lint` |
| LNT025 | Local agent artifacts and plan files stay unstaged | Error | `opencode_lint` |
| LNT-PY-BUDGET | Changed Python code budgets | Error | `opencode_lint` |
| OC-SKILL-CHECK | Skill descriptions use valid trigger-oriented frontmatter | Warning | `opencode_lint` |

## Configuration

Create `.opencode-lint.yaml` to customize:

```yaml
rules:
  OC002:
    severity: warning
    enabled: true
    exclude:
      - "fixtures/*"

ignore:
  - "*.pyc"
  - "__pycache__/*"
  - ".venv/*"
```

## Development

```bash
# Install dev dependencies
uv sync --project opencode_lint --extra dev

# Run tests
uv run --project opencode_lint pytest

# Lint
uv run --project opencode_lint ruff check .
```
