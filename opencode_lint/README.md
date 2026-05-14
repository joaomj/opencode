# OpenCode Lint - Custom Linter for AGENTS.md Rules

A custom linter that enforces core AGENTS.md guidelines from the Factory.ai "Linters as Law Enforcement" concept. Additional policies are enforced by pre-commit hooks and sub-agents.

## Installation

```bash
pip install -e opencode_lint
```

Or use the pre-commit hook setup:
```bash
curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/setup-hooks.sh | bash
```

## Usage

### As CLI
```bash
# Check all files
opencode-lint

# Check specific file
opencode-lint src/main.py

# Fix auto-fixable issues
opencode-lint --fix

# Pre-commit mode (exit code 1 on violations)
opencode-lint --pre-commit
```

### As Pre-commit Hook
The linter runs automatically on commit if hooks are installed.

## Rules

| Rule ID | Description | Severity | Auto-fix |
|---------|-------------|----------|----------|
| OC001 | No raw dicts for API schemas | Error | No |
| OC002 | Never read/print `.env` values | Error | No |
| OC003 | No privileged containers | Error | No |
| OC004 | Absolute imports preferred | Warning | No |
| OC005 | Strict type hints required | Warning | No |

## Configuration

Create `.opencode-lint.yaml` to customize:

```yaml
rules:
  OC001:
    severity: error
    enabled: true
  OC004:
    severity: warning
    enabled: true
    exclude:
      - "tests/*"

ignore:
  - "*.pyc"
  - "__pycache__/*"
  - ".venv/*"
```
