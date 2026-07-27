---
name: github-cicd-lite
description: Lean GitHub-only CI pipelines for small Python projects, optimized for speed and security; deployment optional
license: MIT
---

# GitHub CI/CD Lite (Python-First)

Design and implement lean GitHub Actions pipelines for small repositories.

## Scope

- Platform: GitHub Actions only
- Default target: CI (lint, test, lightweight security)
- Deployment: optional and disabled by default
- Bias: fast feedback, low maintenance, strong baseline security

## Invocation Contract

Use this skill when:

- User asks for CI/CD or GitHub Actions pipeline creation
- User asks to improve, harden, or speed up an existing GitHub pipeline
- Agent detects no `.github/workflows/*.yml` and user confirms pipeline creation

If no workflow exists, ask exactly:

`I don't see a GitHub CI workflow here. Want me to add a lean, secure CI pipeline for this repo?`

## Default Deliverable

Create or update:

- `.github/workflows/ci.yml`

Keep one primary workflow unless the user requests split workflows.

## Required Baseline

1. CI triggers
   - `pull_request`
   - `push` on primary branch (`main` by default)

2. Least privilege permissions
   - Set explicit top-level `permissions`
   - Default to `contents: read`

3. Speed controls
   - `concurrency` with cancel-in-progress for the same ref
   - Dependency caching via `actions/setup-python`
   - Keep jobs minimal and parallel when possible

4. Security controls
   - Never expose secrets in PR jobs
   - Add at least one dependency/security check suitable for project size
   - Set per-job `timeout-minutes`

5. Supply chain enforcement (OC011)
   - Use `--locked` on all install commands to prevent lockfile drift
   - Add `exclude-newer` gate job that verifies config in pyproject.toml

6. Reliability
   - Pin action versions to stable releases (and SHA pinning for third-party actions when feasible)
   - Avoid brittle shell one-liners without `set -euo pipefail` for multiline scripts

## Python-First CI Shape

Use this as the default pattern. Adapt to project tooling by detecting the package manager:

### Package Manager Detection

| Detected file | Install command | Run command | Lockfile check |
|---------------|----------------|-------------|----------------|
| `uv.lock` | `uv sync --locked` | `uv run ...` | `uv.lock` exists |
| `pdm.lock` | `pdm install --dev --locked` | `pdm run ...` | `pdm.lock` exists |
| `poetry.lock` | `poetry install --with dev --locked` | `poetry run ...` | `poetry.lock` exists |
| `requirements*.txt` | `pip install -r ...` | direct call | N/A |

Do not introduce a new package manager if one is already in use.

### CI Workflow Template

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lockfile-check:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - name: Check exclude-newer configured
        run: |
          if ! grep -q 'exclude-newer' pyproject.toml; then
            echo 'ERROR: exclude-newer not configured in pyproject.toml (OC010)'
            exit 1
          fi
      - name: Verify lockfile integrity
        run: |
          if [ -f uv.lock ]; then uv lock --locked
          elif [ -f pdm.lock ]; then pdm lock --check
          elif [ -f poetry.lock ]; then poetry lock --check
          fi

  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Install dependencies
        run: uv sync --locked
      - name: Lint
        run: uv run ruff check .

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Install dependencies
        run: uv sync --locked
      - name: Test
        run: uv run pytest -q

  security:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Vulnerability audit
        run: uvx pip-audit --desc
      - name: Secret detection
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Tooling Detection Rules

Select install/test commands by existing files (see table above).

Additional rules:
- `pyproject.toml` without any lockfile -> suggest `uv init` to bootstrap
- Always verify lockfile exists before running install commands
- Add `pip-audit` step as a mandatory CI job for dependency vulnerability scanning
- When using `uv pip compile`, enforce `--exclude-newer` with 7-day buffer (OC010)

### pip-audit Integration (Mandatory)

Add a dedicated security job to every CI pipeline:

```yaml
  security:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - name: Vulnerability scan
        run: uvx pip-audit --desc
```

For projects with requirements.txt:
```yaml
      - name: Vulnerability scan
        run: uvx pip-audit --requirement requirements.txt --desc
```

### Container Image Scanning (Trivy)

For projects building Docker images, add Trivy scanning:

```yaml
  container-scan:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          format: sarif
          output: trivy-results.sarif
          severity: HIGH,CRITICAL
      - name: Upload results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: trivy-results.sarif
```

And add to job dependencies:
```yaml
    needs: [lockfile-check, lint, test, security, container-scan]
```

## Optional Deployment Block

Only add deployment when user requests it. If requested:

- Use separate `deploy` job gated by `needs: [lint, test, security]`
- Restrict to `push` on protected branch
- Use GitHub Environments for approval/secrets scoping
- Keep permissions minimal; add only what deploy needs

## Anti-Patterns to Avoid

- Running deploy on `pull_request`
- Broad workflow permissions by default
- Long serial pipelines for small projects
- Unbounded runtime (missing timeouts)
- Installing unnecessary heavy scanners for tiny repos by default

## Completion Checklist

- Workflow validates in GitHub Actions syntax
- CI runs quickly with caching and cancellation
- Security baseline check present (lint + pip-audit)
- Container image scanning with Trivy (for projects building images)
- Package manager auto-detected from lockfile (uv.lock/pdm.lock/poetry.lock)
- All install commands use `--locked` (OC011)
- Lockfile integrity gate in CI (lockfile-check job)
- exclude-newer verified in pyproject.toml (OC010)
- No secrets required for PR validation path
- Deployment omitted unless explicitly requested
