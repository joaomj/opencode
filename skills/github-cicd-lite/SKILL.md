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

5. Reliability
   - Pin action versions to stable releases (and SHA pinning for third-party actions when feasible)
   - Avoid brittle shell one-liners without `set -euo pipefail` for multiline scripts

## Python-First CI Shape

Use this as the default pattern and adapt to project tooling (`pdm`, `poetry`, `pip`):

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
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install ruff
      - name: Lint
        run: ruff check .

  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest
      - name: Test
        run: pytest -q

  security:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Dependency audit
        run: |
          python -m pip install --upgrade pip
          pip install pip-audit
          pip-audit
```

## Tooling Detection Rules

Select install/test commands by existing files:

- `pdm.lock` or `pyproject.toml` with PDM config -> `pdm install --dev`, `pdm run ...`
- `poetry.lock` -> `poetry install --with dev`, `poetry run ...`
- `requirements*.txt` -> `pip install -r ...`

Do not introduce a new package manager if one is already in use.

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
- Security baseline check present
- No secrets required for PR validation path
- Deployment omitted unless explicitly requested
