# OpenCode Config

Personal configuration for [OpenCode](https://opencode.ai) — the AI coding assistant that lives in your terminal. Includes custom agents, skills, a custom linter, pre-commit hooks, and slash commands.

> **Disclaimer:** This project is not built by the OpenCode team and is not affiliated with OpenCode in any way. It is a personal configuration using OpenCode as a platform.

## What's Inside

### Skills (12)
| Skill | Purpose |
|-------|---------|
| `architecture-diagram` | System architecture diagrams (dark-themed HTML/SVG) |
| `c4-diagram` | C4 model architecture diagrams |
| `coding-best-practices` | Universal coding standards (quality, idempotency, error treatment, logging, async safety, hardcoding avoidance) |
| `context7-docs` | Real-time library/framework documentation lookup |
| `create-pull-request` | End-to-end PR creation with merge conflict detection |
| `docker-best-practices` | Containerization (Dockerfile, Compose, security, networking) |
| `firecrawl-web-scraper` | Single-page web scraping to markdown/JSON |
| `github-cicd-lite` | Lean GitHub CI pipelines for small Python projects |
| `google-drive-reader` | Read Google Docs/Sheets via Drive API |
| `jira-issues` | Fetch/create/search Jira issues via ACLI |
| `ml-best-practices` | ML development (CRISP-DM, data quality, MLflow) |
| `notion-reader` | Search/fetch Notion content via notion-cli |

### Commands (3)
- `commit` — structured commit messages
- `standup-prep` — daily standup preparation
- `update-opencode` — self-update this config

### Agent Personas (6)
- `ml-engineer` — Python/ML coding with `uv`, e2e tests, frontend delegation
- `frontend-tester` — read-only browser-based frontend verification
- `researcher` — read-only library/API research via web search + Context7
- `code-reviewer` — expert review (SOLID, security, performance, P0-P3 severity)
- `doc-maintainer` — update/prune documentation for accuracy
- `simplifier` — apply project standards to simplify code

### Custom Linter (`opencode_lint`)
A standalone Python linter enforcing all AGENTS.md rules via a single pre-commit hook. Runs as both a CLI (`opencode-lint`) and a pre-commit hook:

| Rule | Description | Severity |
|------|-------------|----------|
| OC001 | No raw dicts for API schemas | Error |
| OC002 | Never read/print `.env` values | Error |
| OC003 | No privileged containers | Error |
| OC004 | Absolute imports preferred | Warning |
| OC005 | Strict type hints required | Warning |
| OC009 | Lockfile must exist and be committed | Error |
| OC010 | `exclude-newer` must be configured with 7-day buffer | Error |
| OC011 | No blind `uv lock --upgrade` — use `--upgrade-package` | Error |
| OC012 | No unsafe `curl \| bash` downloads | Error |
| OC014 | No hardcoded configurable values | Warning |
| OC-MOCK | Mock external boundaries only; avoid internal mocks | Error |

Install: `pip install -e opencode_lint`

### Pre-commit Hooks

**Code Quality:**
- **Ruff** (lint + `--fix`) and **ruff-format** — separate hooks per ruff's recommended setup; lint rules and formatting are distinct concerns managed by two different ruff subcommands
- **Mypy** — strict type checking (`--disallow-untyped-defs`, `--check-untyped-defs`)

**Security & Supply Chain:**
- **Gitleaks** — secret detection (credentials, keys, tokens)
- **pip-audit** (`uvx pip-audit --desc`) — dependency vulnerability scanning, runs on every commit
- **`opencode-lint`** — enforces OC009-OC012 (lockfile, exclude-newer, targeted upgrades, unsafe downloads)

**Dockerfile:**
- **Hadolint** — Dockerfile linting

**AGENTS.md Rules:**
- **`opencode-lint`** — single hook enforcing all rules: no raw API dicts (OC001), no `.env` access (OC002), no privileged containers (OC003), absolute imports (OC004), type hints (OC005), lockfile (OC009), exclude-newer (OC010), no blind upgrades (OC011), no unsafe downloads (OC012), no hardcoded config (OC014), mock policy (OC-MOCK)

All custom policy hooks (file length, test skip, e2e enforcement, pyproject edits) were consolidated into `opencode-lint` and AGENTS.md documentation — removing redundant commit gates.

### MCP Servers
- `chrome-devtools` — browser debugging via DevTools Protocol (Brave)

### Models Configured
- DeepSeek V4 Flash / Pro
- MiMo V2.5 Pro
- Kimi K2.6
- GPT 5.5

## Updating

Run `/update-opencode` from within OpenCode.

## License

[MIT](LICENSE)
