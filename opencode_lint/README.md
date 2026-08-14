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
| OC001 | No raw dicts for API schemas | Error | `opencode_lint` |
| OC002 | Never read/print `.env` values | Error | `opencode_lint` |
| OC003 | No privileged containers | Error | `opencode_lint` |
| OC004 | Absolute imports preferred | Warning | `opencode_lint` |
| OC005 | Strict type hints required | Warning | `opencode_lint` |
| OC009 | Lockfile must exist and be committed | Error | `opencode_lint` |
| OC010 | `exclude-newer` with 7-day buffer | Error | `opencode_lint` |
| OC011 | No blind `uv lock --upgrade` | Error | `opencode_lint` |
| OC012 | No unsafe `curl \| bash` downloads | Error | `opencode_lint` |
| OC014 | No hardcoded configurable values | Error | `opencode_lint` |
| OC-MOCK | Mock external boundaries only | Error | `opencode_lint` |
| OC-DECISION | Decision notes use valid lifecycle, structure, and approval data | Error | `opencode_lint` |
| OC-SKILL-CHECK | Skill descriptions use valid trigger-oriented frontmatter | Warning | `opencode_lint` |

### Testing Policy Enforcement

`OC-MOCK` enforces the mock policy from `skills/engineering/testing-best-practices/SKILL.md`:
mock external boundaries only, avoid internal collaborator mocks, and prefer
fakes, temporary resources, or integration tests for internal behavior.

Allowed by default:
- HTTP/cloud/payment/email/SMS clients
- Time, UUID, randomness, and similar determinism boundaries
- External services that cannot run locally in normal CI

Not allowed by default:
- Patching the function or class under test
- Mocking internal domain/services/repositories when a fake or integration test is practical
- Asserting internal call graphs instead of observable outcomes

If internal mocking is unavoidable, add `mock-allow-internal: <reason>` near the
mock and pair it with integration coverage.

Additional security enforcement (not in linter):
- **Gitleaks** — secret detection (pre-commit)
- **pip-audit** — dependency vulnerability scanning (pre-commit, via `uvx`)
- **Ruff `S` rules** — Bandit security lints (pre-commit)

## Configuration

Create `.opencode-lint.yaml` to customize:

```yaml
rules:
  OC001:
    severity: warning
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

## Development

```bash
# Install dev dependencies
uv sync --project opencode_lint --extra dev

# Run tests
uv run --project opencode_lint pytest

# Lint
uv run --project opencode_lint ruff check .
```
