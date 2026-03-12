# Technical Context

This document provides detailed technical information about the opencode configuration system, including skills, commands, and development guidelines.

## Skills Architecture

This configuration uses a skill-based architecture with 10 domain-specific skills loaded on-demand.

### Skill Loading Pattern

Skills are loaded via deterministic triggers defined in `AGENTS.md` (decision-index approach following Vercel's pattern):

1. **User Request Triggers** - Exact match patterns (e.g., "/review", "update docs")
2. **File Pattern Triggers** - Based on file types (e.g., `test_*.py`, `Dockerfile`)
3. **Import Statement Triggers** - Based on imports (e.g., `import pandas`)
4. **Code Pattern Triggers** - Based on detected patterns (e.g., missing type hints)
5. **Conversation Triggers** - Based on context (e.g., stack traces, test failures)

### Available Skills

| Skill | Purpose | Domains |
|-------|---------|---------|
| `python-best-practices` | Type hints, error handling, Pydantic patterns, testing (pytest), logging, Ruff rules, security, dependency management (pdm) | Python |
| `docker-best-practices` | Dockerfile patterns (non-root USER), Docker Compose (read_only), runtime security, network isolation, secrets handling | Docker |
| `ml-best-practices` | CRISP-DM phases with STAR documentation, data quality (test set ONCE), preprocessing in Pipeline, evaluation metrics, MLflow tracking | Machine Learning |
| `workflow-development` | Test-first where it fits (verify-first always), chronological document order (PRD→Design→Specs→Plan), approval gates, todo tracking | Workflow |
| `code-review-expert` | Dual-agent code review with P0-P3 severity classification | Code Quality |
| `doc-maintenance` | Guidelines for identifying and pruning outdated documentation | Documentation |
| `github-cicd-lite` | Lean GitHub Actions CI pattern (Python-first, speed + security, deploy optional) | CI/CD |
| `firecrawl-web-scraper` | Single-URL web scraping with dynamic-page actions and structured JSON output | Web Scraping |
| `standup-prep` | Daily standup summaries from git activity, blocker detection, markdown report generation | Daily Standup |
| `code-simplifier` | Pre-commit simplification with type hints, no raw dicts, explicit code enforcement | Code Quality |
| `jira-issues` | Search assigned Jira issues and update status or description | Project Management |

## Available Commands

Commands are prefixed with `/` and available in opencode CLI.

### `/review`

Performs dual-agent code review with severity classification (P0-P3).

**Usage:**
```bash
/review                    # Review current changes
/review from X to Y        # Review specific branch range
```

Two independent reviewers analyze the same code and findings are consolidated into a review report.

**Severity Levels:**
- **P0** - Critical security/performance issues, blockers
- **P1** - Important issues, should fix before merge
- **P2** - Minor issues, nice to have
- **P3** - Suggestions, style preferences

### `/update-docs`

Identifies and removes obsolete documentation content.

**Usage:**
```bash
/update-docs
```

Scans documentation files for outdated sections and provides recommendations for cleanup.

### `/standup-prep`

Generates daily standup summaries from git activity for team meetings.

**Usage:**
```bash
/standup-prep              # Generate standup summary for yesterday
```

**Features:**
- Analyzes git activity (GitHub CLI or local git)
- Detects potential blockers (failed CI, stale PRs, TODOs)
- Creates a markdown report at `docs/activity-log/activities-YYYY-MM-DD.md`

## Pre-Commit Hooks (Optional)

Install quality checks in any project:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash
```

**Important:** Pre-commit hooks are optional. The installer will ask for confirmation before proceeding.

### Included Checks

| Check | Tool | Purpose |
|-------|------|---------|
| **Secrets** | gitleaks | Detects hardcoded secrets |
| **File length** | Python script | Limits Python files to 300 lines |
| **Test mock policy** | pre-commit hook | Flags internal/mock-heavy test patterns unless justified |
| **Formatting** | ruff | Ensures proper code style |
| **Dockerfile** | hadolint | Validates Dockerfile best practices |
| **Branch protection** | pre-commit | Prevents direct commits to main/master |

### Mock Policy Customization

Add `.test-mock-external-allowlist` in your repo to allow external module prefixes (one per line). Start from `.test-mock-external-allowlist.example` for Python-heavy repos. Use `mock-allow-internal: <reason>` only for rare exceptions.

## Development Guidelines

### Core Principles

| Principle | Description |
|-----------|-------------|
| investigate-first | NEVER edit without approval. Analyze, plan, ask permission. |
| tradeoffs-required | Every suggestion MUST include: pros, cons, alternatives. Quantify when possible. |
| consistency | Follow existing patterns. Scan codebase before writing new code. |
| simplicity | Prefer fewest moving parts. Ask "is this overkill?" before abstractions. |
| no-emojis | Never use emojis in code, docs, or communication. |
| security | No secrets in code. Use .env + pydantic-settings. Validate all inputs. |
| env-files | NEVER read .env files - only .env.example for schema reference. |
| python-deps | When changing/adding Python dependencies, you MUST use `pdm` commands, not directly edit `pyproject.toml`. |
| tech-context | docs/tech-context.md is the Single-File Memory Bank. |
| ml-reporting | ML projects must include a CRISP-DM Build Report in docs/tech-context.md. Each phase documented with STAR. |
| doc-maintenance | Review documentation for obsolete content during code reviews, after major refactors, or when explicitly asked. |

### Ruff Configuration

| Setting | Value |
|---------|-------|
| line-length | 100 |
| target-version | py311 |
| max-complexity | 15 |
| max-args | 7 |
| max-statements | 50 |
| select | E, W, F, I, B, C4, UP, ARG, SIM, PTH, ERA, PL, RUF, S, NPY |

### Workflow

1. **Workspace Analysis** - scan docs/tech-context.md, pyproject.toml, entry points
2. **User Interview** - ask questions until spec is 100% clear
3. **Action Plan** - step-by-step todos with testable checkpoints between phases
4. **Approval Gate** - wait for explicit "yes" before executing the plan
5. **Execute** - after approval, write a temporary phased todo plan in docs/ with clear testable gates/checkpoints; only advance after gate pass; after each gate passes, commit changes (no pushes)

### Task Management

- **atomic-units** - Break tasks into smallest testable pieces
- **todo-tracking** - Use TodoWrite for 3+ steps. Mark complete immediately.
- **phase-plan-file** - After plan approval, write the plan as a phased todo list in a temporary markdown file under docs/
- **phase-gates** - Define explicit pass/fail gate criteria between phases and block next phase until pass
- **gate-commits** - After each gate passes, create a commit (commit only, never push unless explicitly requested)

### Documentation Standards

- **source-of-truth** - docs/tech-context.md - Single-File Memory Bank consolidating Project Brief, Product Context, System Patterns, Tech Context.
- **document-why** - Explain decisions and tradeoffs, not just mechanics
- **data-flow** - How data moves through components, entry to exit
- **depth-over-brevity** - docs/tech-context.md must be a DEEP technical report. Size is not a problem; shallowness is. For every metric, explain: calculation method, why chosen, observed values.
- **no-proactive-docs** - Never create README/docs unless explicitly requested, except temporary docs phase-plan files required after approval

## Context7 API Integration

For external libraries (React, FastAPI, Pandas, etc.), this configuration uses Context7 API:

### Fetch Flow

1. Detect version from `package.json` OR `requirements.txt` OR `pyproject.toml` OR `pip show`
2. Find library ID via: `curl -s "https://context7.com/api/v2/libs/search?libraryName=LIBRARY_NAME&query=USER_QUESTION"`
3. Fetch docs via: `curl -s "https://context7.com/api/v2/context?libraryId=LIBRARY_ID&query=TOPIC&type=txt"`

### Version Matching

| Scenario | Action |
|----------|--------|
| User specifies version | Fetch that version |
| Project has version in package.json/requirements.txt | Fetch matching major version |
| Cannot detect version | Fetch latest, WARN user |
| Library not found in Context7 | Tell user, proceed with knowledge |

## Architecture Decisions

### Decision-Index Format (AGENTS.md)

The AGENTS.md file uses a compressed, pipe-delimited table format for fast scanning and deterministic routing:

| Trigger | Action |
|---------|--------|
| User says "review" | `/skill code-review-expert` |
| File pattern `test_*.py` | `/skill python-best-practices` |
| Import `import pandas` | `/skill ml-best-practices` |

This approach:
- Enables deterministic skill loading (no model decisions)
- Provides clear IF-THEN rules
- Allows fast scanning without parsing natural language
- Follows Vercel's pattern for their AI systems

### Dual-Agent Code Review

Code reviews use two independent reviewers that cross-check each other:

1. **Reviewer 1** (agents/code-reviewer-1.md) - Primary reviewer
2. **Reviewer 2** (agents/code-reviewer-2.md) - Secondary reviewer for validation

Findings are consolidated with severity classification (P0-P3).

### Skill-Based Architecture Benefits

- **Modularity** - Skills are self-contained and can be updated independently
- **Performance** - Only load what's needed for the current task
- **Clarity** - Each skill has a clear, focused purpose
- **Extensibility** - New skills can be added without changing existing ones
