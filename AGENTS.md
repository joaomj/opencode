# AGENTS.md

## Core Principles

- **command-for-workflow**: Use commands for explicit user-invoked workflows with model routing.
- **skill-for-expertise**: Use skills for reusable procedures, standards, and domain knowledge.
- **spec-before-code**: User must approve a spec before substantial code editing.
- **test-before-code**: Production code changes start with a failing test before implementation (OC020). Exempted for doc-only changes.
- **docker-by-default**: Prefer Docker over local installs for development environments. Clean up containers and images after task completion.

## Critical Security

- **NEVER** read, print, echo, inspect, or otherwise access the contents of any `.env` file — not via the Read tool, bash commands (`cat`, `less`, `head`, `tail`, etc.), or scripts that read the file. Use environment variable loading mechanisms only (`dotenv.load_dotenv()`, `os.getenv()`, etc.).
- **NEVER** run privileged containers.

## Commands

| Command | Purpose |
|---------|---------|
| `/commit` | Atomic commit workflow and commit message generation
| `/review` | Code review over current diff with P0-P3 findings

## Skill Routing

| Intent | Action |
|--------|--------|
| Python, TypeScript, shell, configuration, feature, bug fix, refactor | Load `coding-best-practices` |
| Scripts, CLIs, batch jobs, migrations, scrapers, long-running jobs | Load `coding-best-practices`; apply Failure-Resilient Execution strictly |
| Planning a coding task before implementation | Include the Architecture and Design Gate |
| Code review | Use `/review` |
| Research libraries/APIs/frameworks | Load `context7` |
| Docker/containerization, Docker-based CI/CD | Load `docker-best-practices` |
| GitHub Actions CI/CD | Load `github-cicd-lite` |
| ML experiments, model evaluation, model training | Load `ml-best-practices` |
| Production ML code changes | Load `ml-best-practices` and `coding-best-practices` |
| README, API docs, technical reports, implementation summaries | Load `technical-writing` |
| Documentation maintenance, documentation cleanup | Load `doc-maintenance` |
| System architecture/design/ADRs | Include the Architecture and Design Gate; load `technical-writing` |
| Architecture diagrams | Load `architecture-diagram` |
| Browser debugging | Load `browser-readonly` and use `browser_cdp.py` for screenshots, DOM, JS eval, console, and network via local Brave/Chromium CDP |
| Jira ticket fetch, creation, search, update | Load `jira-issues` |
| Write issue, record issue | Load `issue-writing`; create `docs/issues/<slug>.md` only after user approval |
| Simplify code | Load `simplify` only when the user explicitly asks to simplify |
| Scrape web pages | Load `firecrawl-web-scraper` |
| Create a pull request | Load `create-pull-request` |

## Routing Determinism

When a user request matches multiple incompatible routes, ask the user to choose before acting. The question must present concrete named options. Do not silently pick one.

When multiple routes are compatible and mandatory, load all applicable ones. Compatible means no conflicting instructions, goals, or side effects. Mandatory means the route represents a requirement (a rule, a gate, or a standard), not a choice.

Explicit user intent always wins over semantic inference:
- If the user invokes a `/command`, use that command.
- If the user names a skill, load that skill if it exists.
- If the user asks for review, do not edit.
- If the user asks for implementation, follow the relevant coding gates.

Situations that always require asking the user with options:
- review vs implementation for the same diff
- planning vs editing for the same task
- skill-based feature work vs git-based workflow
- destructive vs non-destructive action with side effects
- ambiguous command routing (two commands could match)
- simplify vs broader refactor

The LLM retains semantic routing authority. Determinism governs what happens when authority is ambiguous.

## Coding Standards

Always load `coding-best-practices` when performing coding activity in any language. This skill enforces quality, failure-resilient execution, idempotency, error treatment, logging, async safety, and hardcoding avoidance rules.

- **Linter before commit**: Run `ruff check .` before any `git commit` when Python files are involved. Block if errors remain.
- **No hardcoded values**: App config, URLs, ports, timeouts, thresholds → centralized config only. OC014 enforces this.
- **Idempotent mutations**: All state changes must be safe to retry (upserts, if-not-exists, dedup keys).
- **Failure-resilient execution**: Multi-step, long-running, or side-effecting code must support safe retries, checkpointing/resume where appropriate, durable logs, explicit failures, batching, and concurrency guards.

## Architecture and Design Gate

For substantial coding tasks, the `plan` workflow must include an explicit software architecture and design discussion before implementation. Do not treat planning as just a task list.

The discussion must cover:

- Problem boundaries, core use cases, and non-goals.
- Proposed module/component boundaries and ownership.
- Data flow, control flow, and external integration points.
- Key abstractions, interfaces, and dependency direction.
- State management, persistence, idempotency, and retry behavior where relevant.
- Error handling, observability, security, and operational concerns.
- Tradeoffs between at least two viable designs when the choice is not obvious.
- Risks, unknowns, and validation steps before implementation.

The final plan must name the chosen design, explain why it was selected, and call out what would force revisiting it.

## Rules

Enforced by the `opencode-lint` linter (`opencode_lint/`). Run with `opencode-lint` or via the CLI.

| ID | Rule | File |
|----|------|------|
| OC001 | No raw dicts for API schemas | `no_raw_dict_api.py` |
| OC002 | Never inspect `.env` values | `no_env_file_access.py` |
| OC003 | No privileged containers | `no_privileged_containers.py` |
| OC004 | Absolute imports preferred | `absolute_imports.py` |
| OC005 | Strict type hints required | `strict_type_hints.py` |
| OC008 | No skipped, xfailed, or suppressed failing tests | testing/process rule |
| OC009 | Lockfile must exist and be committed | `lockfile_required.py` |
| OC010 | `exclude-newer` with 7-day buffer in pyproject.toml | `exclude_newer_configured.py` |
| OC011 | No blind `--upgrade` — use `--upgrade-package` | `no_blind_upgrade.py` |
| OC012 | No unsafe `curl \| bash` downloads | `no_unsafe_downloads.py` |
| OC014 | No hardcoded configurable values | `no_hardcoded_config.py` |
| OC015 | Research unfamiliar APIs before use | documentation/process rule |
| OC016 | E2E/integration tests for user-visible behavior | testing/process rule |
| OC020 | Failing test before implementation | testing/process rule |
| OC-MOCK | Mock external boundaries only | `no_test_mock_abuse.py` |
| OC-ROUTING | AGENTS.md routing table consistency | `routing_consistency.py` |
| OC-REGISTRY | AGENTS.md rules table sync with filesystem | `registry_sync.py` |
| OC-SKILL-CHECK | Skill description quality and trigger language | `skill_descriptions.py` |

Each implemented rule lives in `opencode_lint/rules/`. Process rules are enforced by instructions and review.
