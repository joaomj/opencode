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

# Pre-commit mode (exit code 1 on any violation)
opencode-lint --pre-commit
```

### As Pre-commit Hook
The linter runs automatically on `.md`, `.py`, `.yml`, and `.yaml` files when committing.

## Rules

| Rule ID | Description | Severity | Enforced By |
|---------|-------------|----------|-------------|
| OC002 | Never read/print `.env` values | Error | `opencode_lint` |
| OC003 | No privileged containers | Error | `opencode_lint` |
| OC012 | No shell-piped remote install scripts; use explicit verified steps | Error | `opencode_lint` |
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
