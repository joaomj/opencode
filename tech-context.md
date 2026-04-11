# Technical Context

This document provides detailed technical information about the opencode configuration system, including skills, commands, and development guidelines.

## Configuration Note

`opencode.json` contains personal model and provider settings, including the small model selection and provider limits. These values are known to work in my environment, but they are not guaranteed to work for every user without equivalent provider access or credentials.

## Skills Architecture

This configuration uses a skill-based architecture with domain-specific skills loaded on-demand.

### Skill Loading Pattern

Skills are loaded from `AGENTS.md` using intent-aware routing rather than exact phrase matching.

1. **User intent** - Match the requested task category, not literal keywords.
2. **Code context** - Load domain skills when the file, import, or architecture context suggests them.
3. **Conversation context** - Use surrounding discussion, errors, or task scope to decide which skill is relevant.
4. **User confirmation** - Ask before loading a skill unless the request clearly implies it.

### Available Skills

| Skill | Purpose | Domains |
|-------|---------|---------|
| `python-best-practices` | Type hints, error handling, Pydantic patterns, testing (pytest), logging, Ruff rules, security, dependency management (uv/pdm/poetry) | Python |
| `docker-best-practices` | Dockerfile patterns (non-root USER), Docker Compose (read_only), runtime security, network isolation, secrets handling | Docker |
| `ml-best-practices` | CRISP-DM phases with STAR documentation, data quality (test set ONCE), preprocessing in Pipeline, evaluation metrics, MLflow tracking | Machine Learning |
| `github-cicd-lite` | Lean GitHub Actions CI pattern (Python-first, speed + security, deploy optional) | CI/CD |
| `create-pull-request` | End-to-end PR creation with code review, merge conflict detection, and professional descriptions via GitHub CLI | PRs |
| `jira-issues` | Fetch Jira issue details and comments, save as markdown to workspace root | Jira |
| `context7` | Retrieve up-to-date documentation for software libraries, frameworks, and components via the Context7 API | Docs |
| `firecrawl-web-scraper` | Scrape single web pages with Firecrawl to markdown and structured JSON, with dynamic-page actions and local .firecrawl output | Web Scraping |

### Agent Configuration

| Agent | Model | Notes |
|-------|-------|-------|
| `explore` | `openai/gpt-5.4-mini` | Fast read-only subagent for codebase exploration |

## Available Commands

Commands are prefixed with `/` and available in opencode CLI.

### Plan Agent

Switch to the Plan agent (press Tab or `@plan`) for structured implementation planning using Spec-Driven Design (SDD).

**How to invoke:**
- Press Tab to cycle to the Plan agent
- Type `@plan` in your message

**Features:**
- Workspace analysis and pattern detection
- User interview for requirement clarification
- Systems design with architecture components and data flow
- Tradeoffs analysis with at least 2-3 options
- Phased plan with SDD flow: specs -> tests -> implement
- Clear gate criteria between phases with commit triggers
- Approval gate before execution
- Conditional skill loading (Python/Docker/ML best practices) based on project type

**Output:** `plan-[feature-name].md` at project root (not in docs/)

**Agent config:** `~/.config/opencode/agents/plan.md`

### `/review`

Performs task-scoped code review with severity classification (P0-P3).

**Usage:**
```bash
/review                    # Review current changes
/review from X to Y        # Review specific branch range
```

The `code-reviewer` subagent analyzes the diff and reports findings by severity.

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

### `/commit`

Stages and commits recent changes with auto-generated conventional commit messages.

**Usage:**
```bash
/commit                    # Stage and commit all changes
```

**Features:**
- Creates atomic commits (one logical change per commit)
- Automatically excludes planning/draft files (PLAN, TODO, DRAFT, WIP, TEMP, BACKUP, OLD)
- Generates conventional commit messages (feat:, fix:, docs:, style:, refactor:, test:, chore:)
- Respects .gitignore automatically

## Pre-Commit Hooks (Optional)

Install quality checks in any project:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/opencode/master/setup-hooks.sh | bash
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
| sdd-first | Spec-Driven Design is MANDATORY. Specs before tests, tests before implementation. NO exceptions for business logic. Bug fixes REQUIRE spec + regression test first. |
| no-hardcoding | No hardcoded values. All configurable values (URLs, timeouts, thresholds, file paths, magic numbers) in a config module using pydantic-settings. |
| testing-policy | Prefer behavior/state assertions and real integrations; mock only external boundaries by default. |
| env-files | Never view .env content. Read tool, cat, scripts printing envs are FORBIDDEN. Scripts can LOAD .env internally. Use .env.example for schema reference. |
| python-deps | When changing/adding Python dependencies, you MUST use the project's detected package manager (uv/pdm/poetry), not directly edit `pyproject.toml`. If no manager is detected, suggest uv. |
| tech-context | tech-context.md is the Single-File Memory Bank. |
| ml-reporting | ML projects must include a CRISP-DM Build Report in tech-context.md. Each phase documented with STAR. |
| doc-maintenance | Review documentation for obsolete content during code reviews, after major refactors, or when explicitly asked. |

### SDD (Spec-Driven Design) Non-Negotiables

| Rule | Violation |
|------|-----------|
| Specs before tests, tests before implementation | Block if code written without spec |
| 80% coverage threshold | Block commit if below |
| Critical path coverage | Business logic MUST have specs and tests |
| Behavior assertions | Tests must verify outcomes against spec contracts |
| Bug fixes need spec + regression test | Block fix until spec and test reproduce bug |

### SDD Workflow

1. **SPEC**: Define signatures, types, contracts, edge cases, errors
2. **TEST**: Write tests validating spec compliance
3. **IMPLEMENT**: Write code to fulfill spec contracts
4. **VERIFY**: Coverage >= 80%, all specs have tests, all tests pass
5. **COMMIT**: Only after all gates pass

**Spec-First Triggers:**
- User says "implement" -> Switch to Plan agent (Tab or `@plan`)
- User says "fix bug" -> Block: "Write spec + regression test that reproduces bug first"
- Implementation without spec -> WARN: "No spec defined for this implementation"

### Ruff Configuration

| Setting | Value |
|---------|-------|
| line-length | 100 |
| target-version | py310 |
| select | E, W, F, I, S |

### Workflow

1. **Workspace Analysis** - scan tech-context.md, pyproject.toml, entry points
2. **User Interview** - ask questions until spec is 100% clear
3. **Action Plan** - step-by-step todos with testable checkpoints between phases
4. **Approval Gate** - wait for explicit "yes" before executing the plan
5. **Execute** - after approval, write a temporary phased todo plan in docs/ with clear testable gates/checkpoints; only advance after gate pass; after each gate passes, commit changes (no pushes)

### Task Management

- **atomic-units** - Break tasks into smallest testable pieces
- **todo-tracking** - Use TodoWrite for 3+ steps. Mark complete immediately.
- **phase-plan-file** - After plan approval, write the plan as a phased todo list in a markdown file at project root (not docs/)
- **phase-gates** - Define explicit pass/fail gate criteria between phases and block next phase until pass
- **gate-commits** - After each gate passes, create a commit (commit only, never push unless explicitly requested)

### Documentation Standards

- **source-of-truth** - tech-context.md - Single-File Memory Bank consolidating Project Brief, Product Context, System Patterns, Tech Context.
- **document-why** - Explain decisions and tradeoffs, not just mechanics
- **data-flow** - How data moves through components, entry to exit
- **depth-over-brevity** - tech-context.md must be a DEEP technical report. Size is not a problem; shallowness is. For every metric, explain: calculation method, why chosen, observed values.
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

### Intent-Driven Routing (AGENTS.md)

The AGENTS.md file uses a compressed, pipe-delimited table format for fast scanning and intent-driven routing:

| Trigger | Action |
|---------|--------|
| User asks for code review | `@code-reviewer` |
| Python project context appears | Load `python-best-practices` skill |
| ML library imports appear | Load `ml-best-practices` skill |

This approach:
- Enables intent-driven skill loading without keyword matching
- Provides clear IF-THEN rules
- Allows fast scanning without parsing natural language
- Keeps the routing logic easy to maintain

### Code Review

Code reviews use the `code-reviewer` subagent with severity classification (P0-P3):
- Task-scoped reviews focus only on relevant code changes
- Ask user for context before reviewing
- Ask user before writing review document
- Single reviewer flow for reliability

### Skill-Based Architecture Benefits

- **Modularity** - Skills are self-contained and can be updated independently
- **Performance** - Only load what's needed for the current task
- **Clarity** - Each skill has a clear, focused purpose
- **Extensibility** - New skills can be added without changing existing ones
