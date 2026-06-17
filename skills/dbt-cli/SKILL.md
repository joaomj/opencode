---
name: dbt-cli
description: >
  Run SQL transformations and data models using the dbt platform CLI (`dbt`). Use this
  skill when you need to develop dbt projects locally, compile models, run tests, build
  pipelines, manage dbt environments, or lint SQL files — all backed by dbt platform's
  infrastructure for secure credential storage, automatic deferral, and parallel execution.
---

# dbt CLI (`dbt`)

The dbt CLI lets you run dbt commands against your dbt platform development environment
from your local command line. It integrates with the dbt platform for secure credential
storage, automatic deferral, and Mesh (cross-project `ref`) support.

## Quick Reference

```bash
# Build selected resources (run + test)
dbt build --select tag:daily

# Run models
dbt run --select stg_orders

# Test data quality
dbt test --select source:raw

# Compile (validate without running)
dbt compile

# Generate docs
dbt docs generate

# View environment config
dbt environment show

# List resources in project
dbt list --output json

# Install package dependencies
dbt deps

# Lint SQL files
dbt sqlfluff lint

# Debug connection
dbt debug
```

## Installation

Install the dbt platform CLI (distinct from dbt Core):

```bash
# macOS (Homebrew)
brew tap dbt-labs/dbt-cli
brew install dbt

# Linux — download latest release from GitHub and extract
tar -xf dbt_<version>_linux_amd64.tar.gz

# Windows — download dbt.exe from GitHub releases

# pip (existing Python users)
pip install dbt --no-cache-dir
```

Verify installation:

```bash
dbt --help
# → "The dbt CLI - an ELT tool for running SQL transformations and data models in dbt..."
```

## Configuration

### 1. Download credentials

Download `dbt_cloud.yml` from **Account settings → Your profile → CLI → Download CLI configuration file**.
Place it at `~/.dbt/dbt_cloud.yml`:

```bash
mkdir -p ~/.dbt && mv ~/Downloads/dbt_cloud.yml ~/.dbt/dbt_cloud.yml
```

### 2. Add `dbt-cloud` block in `dbt_project.yml`

```yaml
# dbt_project.yml
name: my_project
version: "1.0.0"

dbt-cloud:
  project-id: YOUR_PROJECT_ID
  defer-env-id: '123456'  # optional — auto-deferral target
```

### 3. Set developer credentials

In the dbt platform UI, set **developer credentials** for your project's development
environment. The CLI uses these (stored securely in dbt) — no `profiles.yml` needed.

### 4. Verify

```bash
dbt environment show
```

## Core Commands

| Command | Description | Parallel |
|---------|-------------|----------|
| `dbt build` | Build + test selected resources | ❌ write |
| `dbt run` | Run selected models | ❌ write |
| `dbt test` | Execute data tests | ✅ read |
| `dbt compile` | Compile (validate) project | ✅ read |
| `dbt seed` | Load CSV seed files | ❌ write |
| `dbt snapshot` | Execute snapshot jobs | ❌ write |
| `dbt docs generate` | Generate project docs | ✅ read |
| `dbt docs serve` | Serve docs locally | ✅ read |
| `dbt deps` | Install package deps | ✅ read |
| `dbt list` | List project resources | ✅ read |
| `dbt show` | Preview transformed rows | ✅ read |
| `dbt parse` | Parse + write timing info | ✅ read |
| `dbt debug` | Debug connections | ✅ read |
| `dbt clean` | Delete artifacts | ✅ read |
| `dbt clone` | Clone models from state | ❌ write |
| `dbt retry` | Retry from failure point | ✅ read |
| `dbt run-operation` | Invoke a macro | ❌ write |
| `dbt source freshness` | Validate source freshness | ✅ read |

Write commands are limited to **one at a time**. Read commands can run in parallel.

```bash
# Node selection examples
dbt run --select my_model                    # single model
dbt run --select stg_*                       # glob pattern
dbt run --select tag:daily                   # tag selector
dbt run --select +my_model                   # model + upstream
dbt run --select my_model+                   # model + downstream
dbt run --select 3+my_model                  # model + 3 upstream
dbt run --select --exclude tag:nightly       # exclude tagged

# Common flags
dbt run --full-refresh                       # force full refresh
dbt build --fail-fast                        # stop on first failure
dbt test --warn-error                        # treat warnings as errors
dbt compile --no-populate-cache              # skip cache population
```

## dbt CLI–Specific Commands

### `dbt environment`

Interact with your dbt platform environment configuration.

```bash
dbt environment show        # view current config details
```

### `dbt invocation`

Debug long-running sessions by interacting with active invocations.

```bash
dbt invocation list         # list active invocations
```

### `dbt login`

Log in to your dbt platform account from the CLI.

```bash
dbt login
```

### `dbt cancel`

Cancel the most recent invocation.

```bash
dbt cancel
```

### `dbt reattach`

Reattach to the most recent invocation to retrieve logs and artifacts.

```bash
dbt reattach
```

## SQLFluff Linting

dbt CLI bundles SQLFluff for linting SQL files:

```bash
# Lint all SQL files in project
dbt sqlfluff lint

# Lint specific file or directory
dbt sqlfluff lint models/staging/

# Auto-fix violations
dbt sqlfluff fix

# Auto-format SQL
dbt sqlfluff format
```

dbt reads `.sqlfluff` config files for custom rules. CI/CD workflows require a
`dbt_cloud.yml` file to be present.

## Environment Variables

Set user-level environment variables in **Account settings → Credentials → your project → Edit**.

Referenced in dbt project as `{{ env_var('DBT_ENV_VAR') }}`.

## Artifacts

dbt CLI automatically downloads artifacts (manifest, run results, etc.) after each run.
Skip artifact download for faster performance:

```bash
dbt run --download-artifacts=false
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `dbt not found` | Install via `brew install dbt` or `pip install dbt` |
| Path conflict with dbt Core | Deactivate virtualenv, create alias (`alias dbt-cli='dbt'`), or install via `pip` in isolated venv |
| `Stuck session` / `Session occupied` | Run `dbt invocation list` in another terminal, then `dbt cancel` or `Ctrl + Z` |
| `dbt deps` not needed on start | dbt CLI auto-installs deps; only run `dbt deps` when `packages.yml` changes |
| Relative paths in `packages.yml` | Not supported in dbt CLI — use Studio IDE instead |
| Artifacts slowing runs | Add `--download-artifacts=false` |
| `dbt sqlfluff` returns exit code 0 on violations | Known dbt CLI behavior (differs from upstream SQLFluff) |

## Best Practices

- **Isolate from dbt Core** — Use a dedicated virtual environment or alias to avoid `$PATH` conflicts
- **Use `--select` with tags** — Organize models with tags (`tag:daily`, `tag:nightly`) for targeted runs
- **Prefer `dbt build` over `dbt run` + `dbt test`** — Single command validates + tests in one pass
- **Skip artifacts in CI** — Use `--download-artifacts=false` when artifacts aren't needed
- **Parallel read commands** — `dbt compile`, `dbt test`, `dbt list`, `dbt parse` can run concurrently
- **Keep `dbt_cloud.yml` out of version control** — Add to `.gitignore` (contains API tokens)
- **Use `dbt environment show`** to verify your configuration before running builds

## References

- [dbt CLI Installation](https://docs.getdbt.com/docs/platform/dbt-cli-installation)
- [dbt CLI Configuration](https://docs.getdbt.com/docs/platform/configure-dbt-cli)
- [dbt Command Reference](https://docs.getdbt.com/reference/dbt-commands)
- [Node Selection Syntax](https://docs.getdbt.com/reference/node-selection/syntax)
- [dbt_cloud.yml Reference](https://docs.getdbt.com/reference/dbt_cloud.yml)
- [dbt SQLFluff Linting](https://docs.getdbt.com/reference/commands/lint)
