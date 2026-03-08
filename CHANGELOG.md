# Changelog

All notable changes to the OpenCode Agent Guidelines.

## [4.1.3] - 2026-03-08

### Added

- **Code Simplifier Skill** (`skills/code-simplifier/SKILL.md`)
  - Pre-commit code simplification that applies project standards
  - Enforces type hints, no raw dicts, explicit code over clever one-liners
  - Validates changes with lint/typecheck before staging
  - Integrated into commit protocol as automatic step

- **Codebase Diagrams Skill** (`skills/codebase-diagrams/SKILL.md`)
  - Generate Excalidraw diagrams for architecture, data flow, and sequence diagrams
  - Optimized for onboarding and system design explanations
  - Basic shapes only (no icon library complexity), max 15 elements per diagram
  - Outputs to `docs/diagrams/` directory

### Changed

- **AGENTS.md Commit Protocol**
  - Added explicit rule: ALWAYS use one-line commit messages (max 72 chars, no body text)
  - Changed pre-commit hooks policy: Do NOT install by default (only on explicit request)
  - Added code-simplifier as step 1 in before-committing workflow

- **README.md**
  - Updated skill count from 9 to 11
  - Added code-simplifier and codebase-diagrams to skills table and project structure
  - Updated Development Guidelines table with new skill entries

## [4.1.2] - 2026-03-05

### Changed

- **Firecrawl Skill Scope** (`skills/firecrawl-web-scraper/SKILL.md`)
  - Narrowed the skill to single-URL website scraping only
  - Removed PDF/crawl/map/search guidance to avoid overengineering
  - Added focused recipes for dynamic content (`waitFor`, `actions`) and structured JSON extraction
  - Switched output convention to `.firecrawl/<domain>/<slug>.{md,json}`
  - Removed undocumented stealth proxy retry guidance and aligned examples with current docs

- **README Skill Description** (`README.md`)
  - Updated `firecrawl-web-scraper` row to reflect single-URL, dynamic-page, and structured JSON behavior

## [4.1.1] - 2026-03-01

### Added

- **Anti-Mock-Abuse Hook** (`instructions/check_test_mock_abuse.py`)
  - Added pre-commit guardrail to flag internal/mock-heavy test patterns in test files
  - Supports explicit exception marker `mock-allow-internal: <reason>`
  - Supports optional external boundary allowlist via `.test-mock-external-allowlist`

- **Checker Self-Tests** (`instructions/tests/test_check_test_mock_abuse.py`)
  - Added Python unittest-based validation for internal-mock detection, allow markers, disable marker, JS local mocks, and custom allowlist behavior

- **Python Allowlist Template** (`.test-mock-external-allowlist.example`)
  - Added starter allowlist for common Python external boundaries

### Changed

- **Python Testing Guidance** (`skills/python-best-practices/SKILL.md`)
  - Replaced implementation-coupled private method example with public behavior testing
  - Added strict mock policy: mock external boundaries only by default
  - Added test double decision table and LLM anti-pattern checklist

- **Workflow TDD Guidance** (`skills/workflow-development/SKILL.md`)
  - Relaxed absolute TDD rules to "prefer test-first" with explicit exceptions
  - Kept verify-first and bug-regression test requirements

- **Hook Installer** (`setup-hooks.sh`, `instructions/.pre-commit-config.yaml`)
  - Installer now downloads and wires mock policy hook into local `.hooks/`
  - Pre-commit config now includes `check-test-mock-abuse` local hook

- **Mock Policy Defaults** (`instructions/check_test_mock_abuse.py`)
  - Expanded built-in Python external boundary prefixes (HTTP clients, DB clients, queues, SMTP/socket)

## [4.1.0] - 2026-03-01

### Added

- **Deep Research Subagent Suite** (`agents/dr-*.md`)
  - Added 10 hidden global subagents: `dr-gate`, `dr-planner`, `dr-query-builder`, `dr-websearch-highrep`, `dr-source-triage`, `dr-evidence-extractor`, `dr-section-writer`, `dr-editor-integrator`, `dr-citation-auditor`, and `dr-orchestrator`
  - Added strict output contracts (JSON-only where required, citation discipline, insufficient-evidence fallback)
  - Added orchestrated staged pipeline for evidence-first long-form research synthesis

### Changed

- **README.md**
  - Documented deep research architecture and hidden subagent usage
  - Added `websearch` prerequisite clarification (`OPENCODE_ENABLE_EXA=1` when not using OpenCode provider)
  - Updated project structure to include `dr-*` agents and `dr-orchestrator`

- **Environment setup**
  - Persisted Exa enablement in shell profile via `OPENCODE_ENABLE_EXA=1` for websearch availability in OpenCode sessions

- **Instructions Directory Cleanup**
  - Removed old instruction subdirectories: python/, docker/, ml/, workflow/, tools/
  - Kept essential files for setup-hooks.sh: .pre-commit-config.yaml, check_file_length.py
  - Kept reference file: pyproject.toml (Ruff configuration example)
  - All instruction content now consolidated into 4 new skills

## [4.0.0] - 2026-03-01

### Added

- **Skill-Based Architecture** - Converted all `@instructions/` files to reusable skills
  - `python-best-practices` - Consolidates type-hints, error-handling, logging, testing, pydantic, ruff-rules into single skill
  - `docker-best-practices` - Consolidates dockerfile, runtime-security, compose-template, network-isolation into single skill
  - `ml-best-practices` - Consolidates crisp-dm, data-splitting, leakage-prevention, evaluation, feature-importance, mlflow into single skill
  - `workflow-development` - Consolidates planning, task-management, pr-description into single skill with TDD emphasis

- **Vercel-Style Decision Index** (AGENTS.md)
  - Refactored from 370 lines to 177 lines (52% compression)
  - Pipe-delimited tables for fast scanning and decision-making
  - Deterministic skill triggers with clear IF-THEN rules
  - No ambiguity about WHEN to load skills
  - `IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning`
  - Separation of concerns: AGENTS.md handles decisions, skills provide knowledge

### Changed

- **AGENTS.md** - Complete refactor following Vercel's approach
  - Removed Pre-Flight Checklist (replaced with deterministic triggers)
  - Removed `@instructions/` references (all content now in skills)
  - Removed detailed detection tables (replaced with compressed triggers)
  - Added clear "Deterministic Skill Triggers" section
  - Compressed "Skill Index" to load-on-demand format
  - Pre-commit hooks now marked OPTIONAL (must ask user before installing)

- **Skills** - Enhanced with non-negotiable rules and checklists
  - All skills now include "Non-Negotiable Rules" section
  - Pre-commit hooks explicitly marked as OPTIONAL with user consent requirement
  - Clarified AGENT restrictions: "AGENT must never read .env files" (application code can load .env)
  - Added completion checklists to all skills

- **Documentation** - Updated README.md
  - Updated project structure to reflect skills directory
  - Updated skills table to show all 8 skills
  - Added retrieval-led reasoning explanation
  - Updated pre-commit hooks section to note optional status

### Philosophy Updates

- **Decision Over Instruction** - AGENTS.md provides clear decision rules, removing ambiguity that caused skills to not be triggered reliably
- **Retrieval-Led Reasoning** - Agents prefer loading skills/docs over relying on potentially outdated training data
- **Load-on-Demand** - Skills are indexed but not loaded upfront; loaded only when deterministic triggers fire
- **Optional Safety** - Pre-commit hooks require user opt-in, not automatic installation

## [2.4.0] - 2026-02-15

### Added

- **Advanced Testing Guidelines** (testing.md)
  - **Concurrency & Race Conditions Testing**: Comprehensive section on testing threaded code, async operations, and race conditions using pytest-asyncio, threading, pytest-xdist, and freeze_time
  - **Integration vs Unit Test Decision Framework**: Decision matrix table for when to write integration tests vs mocked unit tests with 15+ specific scenarios
  - **Before/After Test Examples**: Concrete examples showing useless tests (heavy mocking, always pass) vs useful tests (catches real bugs like race conditions, payment declines)
  - **Property-Based Testing Guidelines**: Introduction to Hypothesis with real-world examples for sorting, serialization, cache invariants, and concurrency testing
  - **Test Data Management**: Strategies for realistic test data including factories, property-based generation, edge case data sets, data builders with chaining, and anti-patterns
  - **Enhanced Test Quality Checklist**: Updated checklist with concurrency, integration testing, property-based testing, test data realism, and anti-mock criteria
  - **Updated Test Metrics**: Added "flaky test rate" and "test effectiveness" metrics, plus anti-metrics to avoid (100% coverage, test count)

- **Dual Subagent Code Review Workflow** (code-review.md)
  - **Dual Subagent Review Workflow**: Two independent subagents perform full reviews in parallel for 85-95% issue coverage (vs 60-70% with single reviewer)
  - **Subagent Invocation Protocol**: Step-by-step protocol for launching 2 independent subagents with identical scope, parallel execution, and structured output format
  - **Finding Merge Protocol**: Deduplication algorithm for identical findings, prioritization by severity, grouping by file, and summary generation
  - **Iterative Review Loop**: Complete loop structure with pseudocode for re-launching subagents after user fixes, tracking iteration state, and comparing progress
  - **Termination Criteria**: Clear rules for when to stop (0 P1/P2 issues, max 3 iterations, or diminishing returns) with concrete examples of each termination scenario
  - **Updated Workflow Steps (1-9)**: Complete workflow incorporating dual subagent review, iterative fixes, and convergence detection
  - **Example Subagent Prompts**: Three complete prompt templates for default review, branch-to-branch review, and PR review with structured output requirements

### Changed

- **Testing Guidelines** (testing.md)
  - Strengthened "Mock Abuse" section with additional warnings about mock-heavy tests providing false confidence
  - Added emphasis on integration tests over heavily mocked unit tests
  - Enhanced examples throughout to show real bug-finding scenarios

- **Code Review Guidelines** (code-review.md)
  - Completely restructured workflow to support dual subagent review
  - Updated "Example User Interactions" to reflect new iterative workflow
  - Added pseudocode implementation showing complete dual subagent review process
  - **P0 Severity Level**: Added P0 (Critical) for "must block merge" issues (security vulnerabilities, data loss risk, correctness bugs)
  - **SOLID Checklists**: Added comprehensive sections for SRP, OCP, LSP, ISP, DIP with detection prompts and refactor heuristics
  - **Race Conditions**: Added detailed coverage including shared state, check-then-act (TOCTOU), database concurrency, and distributed systems
  - **Boundary Conditions**: Added checklist for null/undefined handling, empty collections, numeric boundaries, and string boundaries
  - **Removal Planning**: Added template for safe vs deferred deletion with priority levels and verification steps
  - **Enhanced Security**: Added JWT & token security, supply chain & dependencies, CORS & headers, and ReDoS patterns
  - **Preflight Edge Cases**: Added handling for no changes, large diff (>500 lines), and mixed concerns
  - **Next Steps Confirmation**: Added explicit options after review presentation (Fix all, Fix P0/P1 only, Fix specific items, No changes)

### Philosophy Updates

- **Testing Focus**: Shift from "test to pass" to "test to find bugs" - tests should catch real issues (race conditions, integration failures), not verify mock behavior
- **Review Redundancy**: Dual independent reviews provide maximum issue coverage by eliminating blind spots through independent perspectives
- **Iterative Improvement**: Code review is now a loop, not a one-time check - fix, re-review, repeat until convergence

## [2.3.0] - 2026-02-11

### Added

- **Single-File Memory Bank** (AGENTS.md, documentation.md)
  - `|tech-context|` rule: `docs/tech-context.md` is mandatory Single-File Memory Bank
  - Consolidates Cline Memory Bank core files: Project Brief, Product Context, System Patterns, Tech Context
  - Reference: https://docs.cline.bot/prompting/cline-memory-bank

- **ML Build Report** (AGENTS.md, documentation.md)
  - `|ml-reporting|` rule: ML projects must include CRISP-DM Build Report in `docs/tech-context.md`
  - Each of 6 CRISP-DM phases documented with STAR (Situation, Task, Action, Result) methodology
  - All metrics require HOW, WHY, WHAT, WHERE documentation

- **Deep Technical Report Requirement** (documentation.md)
  - `docs/tech-context.md` must be a deep technical report
  - Size is not a problem; shallowness is
  - For every metric: explain calculation method (HOW), rationale (WHY), observed values (WHAT), location (WHERE)

### Changed

- **AGENTS.md**
  - Added `|tech-context|` core principle for mandatory Single-File Memory Bank
  - Added `|ml-reporting|` core principle for ML projects
  - Updated Documentation section with depth-over-brevity rule

- **Documentation Guidelines** (`instructions/workflow/documentation.md`)
  - Added Single-File Memory Bank structure definition
  - Added 4 required sections for `docs/tech-context.md`
  - Added ML-only Build Report section with CRISP-DM + STAR template
  - Updated Core Principle to include HOW/WHY/WHAT/WHERE requirement
  - Updated Documentation Checklist with new compliance items

## [2.2.0] - 2025-02-04

### Added

- **Multi-Machine Support** - AGENTS.md now loads via GitHub URL
  - Update global opencode.json with `instructions` field
  - Lazy-loading from `https://raw.githubusercontent.com/joaomj/skills/main/`
  - Added `opencode.example.json` as setup template
  - Enables consistent agent behavior across 4+ machines

- **External File Loading** (AGENTS.md)
  - WebFetch-based lazy loading for instruction files
  - `@instructions/python/type-hints.md` syntax
  - 5-second timeout per remote fetch
  - Reduces initial context load

- **One-Command Pre-Commit Setup** (`setup-hooks.sh`)
  - Automatic installation of quality checks in any project
  - Downloads pre-commit config and custom hooks
  - Config updates to use local file-length script

### Changed

- **AGENTS.md** - Replaced local path references with GitHub URLs
- **AGENTS.md** - Replaced "Enforcement|pre-commit" with "Quality Checks|pre-commit-hooks"
- **AGENTS.md** - Updated "stop-when" to remove "security addressed" (now handled by pre-commit hooks)
- **README.md** - Updated documentation for GitHub-based setup
- **README.md** - Added "Multi-Machine Setup" section
- **README.md** - Replaced "Usage" section with pre-commit hooks setup
- **README.md** - Updated "Key Principles" #3 to reflect pre-commit quality checks
- **CHANGELOG.md** - Added v2.2.0 entry documenting all changes

## [2.1.0] - 2024-02-04

### Added

- **Structured Logging Policy** (`instructions/python/logging.md`)
  - JSON structured logging format requirement
  - Trace IDs for distributed systems / Run IDs for batch-ML systems
  - Context propagation patterns
  - Explicit ban on logging secrets (P1 security requirement)

- **Testing Policy** (`instructions/python/testing.md`)
  - Test behavior, not implementation philosophy
  - Strict anti-mock-abuse rules (only external I/O)
  - 70/20/10 test pyramid ratios
  - Clear guidance on when NOT to test

- **Code Review Guidelines** (`instructions/workflow/code-review.md`)
  - P1/P2/P3 priority classification system
  - Per-file review format
  - `CODE_REVIEW.md` document generation at project root
  - Only reports issues (clean files ignored)
  - Suggests fixes, never implements

- **Custom Code Review Command** (`commands/codereview.md`)
  - `/codereview` slash command for OpenCode TUI
  - Supports default (origin/main...HEAD) and custom scopes
  - Generates priority-based review documents

- **Development Philosophy** (AGENTS.md)
  - `|incremental|` - Build in testable increments
  - `|checkpoint-driven|` - Define testable success criteria
  - `|verify-first|` - Prove increment works before building on it

- **Architecture Tradeoff Documentation** (`instructions/workflow/documentation.md`)
  - Mandatory "Why This Architecture" sections
  - Alternatives considered table format
  - Explicit tradeoffs documentation
  - Revisit conditions

### Changed

- **AGENTS.md Updates**
  - Added `|env-files|` principle: NEVER read .env files, only .env.example
  - Added Development Philosophy section
  - Updated workflow indices to include logging.md, testing.md, code-review.md
  - Workflow step 5 now explicitly ends with "update docs/tech-context.md when done"
  - Workflow step 3 emphasizes "testable checkpoints between phases"

- **Workflow Planning** (`instructions/workflow/planning.md`)
  - Added explicit warning: NEVER read .env files
  - Redefined checkpoints as "testable functionality gates"
  - Added checkpoint table with phase-specific test criteria
  - Step 5 After Changes now explicitly updates docs/tech-context.md

- **Task Management** (`instructions/workflow/task-management.md`)
  - Added "Implementation Plan Checkpoints" section
  - Each major step must have clear test criteria before proceeding

- **Documentation Guidelines** (`instructions/workflow/documentation.md`)
  - Added required Architecture Tradeoff Documentation section
  - Mandates explaining "why this architecture" in all tech-context.md and Start Here sections

## [2.0.0] - Previous Release

- Initial structured guidelines with AGENTS.md index
- Python, Docker, ML, Workflow instruction categories
- Pre-commit enforcement (gitleaks, ruff, hadolint, file length)
- Vercel-style retrieval-led reasoning approach

---

## Format

This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

Versioning: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes to workflow or core principles
- MINOR: New instructions, features, or significant enhancements
- PATCH: Bug fixes, clarifications, minor updates
