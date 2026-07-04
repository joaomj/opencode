---
name: coding-best-practices
description: SDD-first software development methodology with universal coding standards. Use for any coding activity - features, bug fixes, refactors, or AI work. SDD is the default (spec before code); TDD applies only for bug fixes. Covers quality, idempotency, error treatment, async safety, hardcoding avoidance, logging, and Python-specific enforcement rules.
license: MIT
---

# Coding Best Practices

## SDD Workflow

Spec-Driven Development (SDD) is the default methodology for substantial features and architecture work. A user-approved spec precedes code editing. TDD is reserved for bug fixes only.

### Phase 1: Explore

Inspect the project:
- Read project structure, existing patterns, conventions
- Check for relevant tests, existing documentation
- Identify risky areas (security, data mutations, external APIs)

If intent or scope is unclear, ask focused questions.

### Phase 2: Spec (SDD Gate)

Write a spec for user approval covering:
- What to build or fix
- Acceptance criteria (Given/When/Then)
- Files and modules likely involved
- Risks and edge cases
- **Plan**: tasks decomposed into microsteps (see below)

**Gate**: DO NOT edit any code until user approves the spec.

#### Minimal-Step Planning

Decompose each task into microsteps. A **microstep** must satisfy:

> The smallest change that advances the plan, is independently valid, defers all future work, and has a one-line verification.

Each microstep in the Plan section must state:

- **Step ID**: e.g. `T1-S1`
- **Minimal change**: exactly what to implement, no more
- **Defers**: what remains for later microsteps
- **Verifies**: one concrete check (lint, import, unit test) that passes after this step

Example:

```markdown
## Plan

### T1: Add user export endpoint

**Acceptance:**
- POST /users/{id}/export returns text/csv

**Microsteps:**
1. **T1-S1**: Add `ExportRequest` schema in `schemas/export.py`. Defers: endpoint, CSV logic, tests. Verifies: `import succeeds; mypy strict passes`.
2. **T1-S2**: Add pure `build_export(user) -> bytes` service fn using csv.writer. Defers: endpoint wiring, persistence, auth. Verifies: `unit test on a fixed User fixture passes`.
```

The expensive model writes the spec with microsteps once. The cheap model implements each microstep one at a time without deciding scope.

### Phase 3: Test Plan

Propose what to test:
- Integration tests for user-visible behavior
- Unit tests for edge cases and error paths
- Mock only external boundaries (3rd-party APIs, services you can't spin up)

### Phase 4: Implement

Implement against the approved spec.
- For features and refactors: implement against the spec; tests verify the acceptance criteria
- For bug fixes ONLY: write a failing regression test before implementation (TDD)

### Phase 5: Verify

Run the full toolchain:

```bash
pytest -q
ruff check --fix && ruff format
mypy --strict
trivy fs --scanners vuln,secret,misconfig .
```

All must pass with zero failures and zero errors.

### Phase 6: Review

Use `/review` command. If P0 or P1 issues are found, fix and re-review (max 3 cycles). Escalate to user if still failing after 3 cycles.

### Phase 7: Documentation

If public API, user-facing behavior, CLI interface, or config changed, load `doc-maintenance` skill, propose updates, and get user approval before applying.

### Phase 8: Report

Write a concise report in academic format:
- **Executive Summary**: what was done, 1 paragraph
- **Approach**: brief methodology
- **Results**: what changed, test evidence (passing/failing counts)
- **Decisions**: key tradeoffs and choices made
- **Next Steps**: remaining work, follow-up items

### Bug Fix Workflow (TDD)

When fixing a bug:
1. Write a failing regression test that reproduces the bug
2. Implement minimal code to make the test pass
3. Run the full verify chain
4. Refactor while keeping tests green

This is the only context where TDD applies.

### Delegation

| When | Action |
|------|--------|
| Code review | Use `/review` command |
| Unfamiliar libraries/APIs | Load `context7` skill |
| Simplify code | Load `simplify` skill (only on explicit user request) |
| Browser frontend verification | Load `browser-readonly` skill |
| Docker or containerization | Load `docker-best-practices` skill |
| Documentation updates | Load `doc-maintenance` skill |
| Write an issue | Load `issue-writing` skill |

## Quality Standards

### Memory & Speed
- Prefer lazy/streaming patterns over loading everything into memory
- Avoid unnecessary allocations in hot paths
- Profile or benchmark before optimizing — measure, don't guess
- Use appropriate data structures for access patterns

### Robustness
- Validate all external input at the boundary
- Handle edge cases explicitly (empty collections, None/null, overflow)
- Use defensive checks to protect invariants
- Favor explicit early returns over deep nesting

### Idempotency
- Every mutating operation must be safe to retry
- Use upserts (`INSERT ... ON CONFLICT` / `update_or_create`) instead of blind inserts
- Use `if-not-exists` guards before creating resources
- Use dedup keys (idempotency keys / request IDs) for state changes
- Design for at-least-once or exactly-once semantics, never best-effort

### Error & Exception Treatment
- Never silently swallow exceptions — no bare `except:` or `except Exception: pass`
- Every error path must either:
  - Propagate with context (wrap: `raise SomeError("context") from e`)
  - Handle gracefully with a fallback (default value, degraded mode)
  - Log with a clear message + stack trace
- Use specific exception types, not generic ones
- Python: use `logger.exception()` inside except blocks

### Logging
- Log at appropriate levels: debug (diagnostic), info (normal ops), warn (unexpected but handled), error (failure)
- Include enough context to trace failures (correlation IDs, request IDs, function inputs)
- NEVER log secrets, tokens, or PII
- Ensure logs are structured (JSON) where the infrastructure expects it

### Race Conditions & Async
- Acquire locks (`asyncio.Lock`, `threading.Lock`) when shared state is modified
- Prefer structured concurrency (`asyncio.TaskGroup`, `concurrent.futures`)
- Document thread-safety assumptions on every shared data structure
- Avoid `sync_to_async` / `async_to_sync` crossovers where possible
- Use atomic operations (or database transactions) for critical sections

### Failure-Resilient Execution

Apply this strictly when code performs multi-step work, external side effects, batch processing, filesystem writes, network calls, database mutations, migrations, scraping, automation, or long-running execution.

- Prefer resumable execution with checkpoints, durable progress markers, or already-processed detection
- Make each mutation idempotent and safe to retry after partial failure
- Avoid unbounded long loops; use batches, pagination, explicit limits, timeouts, and periodic checkpointing
- Avoid silent failures; errors must be logged, surfaced, or explicitly classified as recoverable
- Persist logs to files for jobs that may outlive the shell, and also print useful progress to stdout/stderr
- Use atomic writes for generated outputs, state files, and checkpoint files
- Use lock files, database advisory locks, idempotency keys, or dedupe keys when concurrent runs would be unsafe
- Prefer `--dry-run` for destructive operations or external side effects
- Prefer `--resume`, checkpoint-path, or continuation options for long-running workflows
- Emit a final summary with attempted, succeeded, skipped, failed, and retriable counts where applicable
- Design long jobs so they can run safely in tmux, CI, remote sessions, or other environments where the foreground UI may disappear

## Hardcoding Avoidance

All configurable values MUST live in centralized config files/modules — never inline in source.

### Blocked Patterns (manual + automated enforcement via OC014)
- **Magic numbers**: `price * 0.19` → `price * TAX_RATE` (with TAX_RATE in config)
- **Inline URLs**: `"https://api.example.com/v1"` in function body
- **Hardcoded ports**: `port=5432` in source (not in config/env)
- **Literal credentials**: API keys, tokens, passwords
- **Environment-specific values**: paths, db names, hostnames
- **Toggle flags / thresholds / timeouts / retry counts**: extract to config

### Allowed Patterns
- **Secrets**: env vars loaded at startup, never committed
- **App defaults & constants**: a `config.py` / `settings.py` module with validated schema
- **Env-specific values**: `.env` file loaded via validated config loader
- **Feature flags / tunables**: same config module, with sensible defaults

### Python Example
```python
# config/settings.py
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    database_url: str
    api_base_url: str = "https://default.api.com"
    max_retries: int = 3
    request_timeout_seconds: float = 30.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

config = AppConfig()
```

### Enforcement
- **OC014** (automated): `opencode-lint` detects magic numbers, inline URLs, hardcoded ports/timeouts/thresholds in source
- **Manual guardrail (agent)**: if you see a literal value that looks like it should be configurable, STOP and ask: "Should this be in config?" If yes, extract it before proceeding

## Pre-Commit Enforcement

- Linter MUST pass zero-warnings before every commit: `ruff check .`
- Pre-commit hook chain (`.pre-commit-config.yaml`) enforces this automatically via `opencode-lint`
- Agent instruction: run `ruff check .` before staging files and block if any errors remain
- All AGENTS.md rules (OC001-OC014, mock policy) are enforced by `opencode-lint`

---

## Python-Specific

### Non-Negotiable Rules

Core rules defined in `opencode_lint/rules/` and enforced via `.pre-commit-config.yaml`. Python-specific enforcement:

| Rule | Violation = STOP |
|------|-----------------|
| Every function has type hints (OC005) | Block if missing |
| No raw dicts for API schemas (OC001) | Block if detected |
| Use detected package manager for deps | Block if direct pyproject.toml edit |
| Lockfile must exist and be committed (OC009) | Block if no lockfile |
| 80% coverage minimum (OC007) | Block if `pytest --cov` < 80% |
| ZERO test skipping (OC008) | Block if `# noqa`, `skip`, or `xfail` found in tests |
| No hardcoded configurable values (OC014) | Block if magic numbers, inline URLs, hardcoded ports/timeouts/thresholds |
| Hardcoding avoidance | Block if literal values belong in config |

### Type Hints

#### Function Signatures

```python
def process_data(input_data: dict[str, Any]) -> Result[str]:
    """Process input data and return result."""
    pass

class DataProcessor:
    def __init__(self, config: Config) -> None:
        self.config = config

    def process(self, data: list[DataItem]) -> list[ProcessedItem]:
        """Process a list of data items."""
        return [self._process_item(item) for item in data]
```

#### Rules
- Always specify return types (even `None`)
- Use `-> NoReturn` for functions that always raise
- Prefer `list[str]` over `List[str]` (PEP 585)
- Every argument must have a type hint
- Use `Any` only when truly necessary

### Pydantic for API Schemas

```python
from pydantic import BaseModel, Field, field_validator

class CreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=0, le=150)

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if '@example.com' in v:
            raise ValueError('example.com emails not allowed')
        return v
```

- Always use `BaseModel` for request/response schemas
- Never accept `dict[str, Any]` directly in API endpoints
- Validate all inputs at the boundary

### Error Handling

```python
# BAD
try:
    process_file()
except Exception:
    pass

# GOOD
try:
    process_file()
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    raise
except PermissionError:
    logger.error(f"Permission denied: {file_path}")
    raise
except ProcessError as e:
    logger.error(f"Process failed: {e}")
    raise
```

- Never use bare `except:` or `except Exception: pass`
- Log exceptions before re-raising
- Add context: `raise SomeError("context") from e`
- Handle specific exceptions, not generic ones

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data: dict[str, Any]) -> Result[str]:
    logger.info(f"Processing data with {len(data)} items")
    try:
        result = _process(data)
        logger.debug(f"Processed successfully: {result}")
        return result
    except ValueError as e:
        logger.warning(f"Validation failed: {e}")
        raise
```

- Never log secrets: `logging.info(f"token={token}")` is FORBIDDEN
- Use `logger.exception()` inside except blocks
- Never expose sensitive data in log messages

### Ruff Configuration

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "PTH", "ERA", "PL", "RUF", "S", "NPY"]

[tool.ruff.lint]
max-complexity = 15
max-args = 7
max-statements = 50
```

Before committing: `ruff check .`

### Testing with Pytest

#### Structure

```python
import pytest
from myapp.processor import DataProcessor

@pytest.fixture
def processor():
    return DataProcessor(config=Config())

def test_process_success(processor):
    result = processor.process([{"id": 1, "value": 100}])
    assert len(result) == 1

def test_process_empty(processor):
    result = processor.process([])
    assert result == []

@pytest.mark.parametrize("input,expected", [
    (100, 200), (50, 100), (0, 0),
])
def test_process_calculation(processor, input, expected):
    result = processor.process([{"id": 1, "value": input}])
    assert result[0].processed_value == expected
```

#### Core Policy
- Test behavior, not implementation details
- Do not test private methods directly
- Prefer integration tests for I/O boundaries
- A good test must fail when behavior regresses

#### Test Integrity (OC008)

**NEVER skip failing tests.** No `# noqa`, `@pytest.mark.skip`, `@pytest.mark.xfail`, or any suppression mechanism.

When a test fails:
1. STOP - do not proceed with other work
2. Investigate: is the code wrong or the test wrong?
3. Fix the root cause
4. Verify all tests pass

There is no option 4: "suppress the failure."

#### E2E/Integration Tests (OC016)

User-visible behavior changes require e2e or integration tests.
Unit tests alone are insufficient for features that affect external interfaces,
APIs, or user workflows.

- Every user-facing change must have at least one e2e/integration test
- E2E tests verify real system behavior, not mocked internals
- Use TestClient (FastAPI/Flask), Playwright, or HTTP requests for integration
- Prefer integration tests over heavy mocking at internal boundaries
- If mocking is required, add `mock-allow-internal: <reason>` marker

#### Mock Usage

| Need | Preferred Double |
|------|------------------|
| External service isolation | Stub/mock external client |
| Time/UUID determinism | Fake clock/ID generator |
| Persistence simulation | In-memory fake repository |
| Service compatibility check | Contract test (CDC/Pact) |

**Allowed:** Mock external services (HTTP SDKs, cloud clients, payment gateways).
**Not allowed by default:** Mocking internal domain/services. If needed, add comment: `mock-allow-internal: <reason>` and pair with an integration test.

#### LLM Anti-Patterns to Reject
- Patching the function/class under test
- Mocking every collaborator by default
- Asserting implementation internals instead of observable outcomes

### Security

- Never hardcode secrets in code
- Never commit `.env` files
- Validate all inputs at boundaries using Pydantic
- Use parameterized queries to prevent SQL injection

### Dependency Management

| Detected file | Manager | Add | Install | Run |
|---------------|---------|-----|---------|-----|
| `uv.lock` | uv | `uv add X` | `uv sync` | `uv run ...` |
| `pdm.lock` | pdm | `pdm add X` | `pdm install` | `pdm run ...` |
| `poetry.lock` | poetry | `poetry add X` | `poetry install` | `poetry run ...` |
| None | **Suggest uv** | `uv init` then `uv add X` | `uv sync` | `uv run ...` |

- ALWAYS use the detected package manager
- NEVER manually edit `pyproject.toml` for dependencies
- ALWAYS commit the lockfile

### Supply Chain Security

| Control | How | Enforcement |
|---------|-----|-------------|
| Lockfile with hashes | `uv lock` / `pdm lock --hash` / `poetry lock` | OC009 |
| Delayed ingestion | `exclude-newer` with 7-day buffer in pyproject.toml | OC010 |
| CI lockfile enforcement | `uv sync --locked` in CI pipeline | OC011 |
| Targeted upgrades | `uv lock --upgrade-package <name>` only | OC012 |
| Vulnerability scanning | `pip-audit` on every commit (supply chain) | Pre-commit |
| Security linting | Ruff `S` rules (Bandit: secrets, crypto, timeouts) | Pre-commit |

```bash
# Hash pinning
uv pip compile --generate-hashes requirements.in -o requirements.txt

# Delayed ingestion (required - OC010)
# Add to pyproject.toml:
# [tool.uv]
# exclude-newer = "1 week"

# In CI, verify lockfile hasn't drifted (OC011)
uv sync --locked

# Targeted upgrade only (OC012)
uv lock --upgrade-package package-name
```

Recent incidents: axios (Mar 2026), telnyx (Mar 2026), Ultralytics (Dec 2024). Defense: hash pinning + delayed ingestion + pip-audit + Ruff S rules.

### File Organization

- Python files: max 300 lines
- Import order: stdlib -> third-party -> local
- Auto-format: `ruff check . --fix`

### Completion Checklist

- [ ] All functions have type hints
- [ ] Error handling is specific (no bare except)
- [ ] Multi-step or long-running work has checkpointing/resume behavior
- [ ] Mutations and external side effects are idempotent and retry-safe
- [ ] Batch jobs avoid unbounded loops and use batching, limits, timeouts, or pagination
- [ ] Operational scripts persist logs to files and print useful shell progress
- [ ] Unsafe concurrent runs are guarded by locks, dedupe keys, or equivalent controls
- [ ] No secrets hardcoded
- [ ] No magic numbers, inline URLs, or hardcoded config values (OC014)
- [ ] Tests written for new functionality
- [ ] Tests assert behavior (not implementation)
- [ ] Spec approved before implementation (SDD gate)
- [ ] Coverage >= 80% for new code
- [ ] `ruff check .` passes
- [ ] Dependencies added via package manager
- [ ] Lockfile committed
- [ ] ZERO test suppression mechanisms
- [ ] E2E/integration tests for user-visible changes (OC016)
- [ ] `exclude-newer = "1 week"` configured in pyproject.toml (OC010)
- [ ] CI uses `uv sync --locked` / `poetry install --locked` (OC011)
- [ ] Dependency upgrades use `--upgrade-package` only (OC012)
- [ ] `pip-audit` passes (no known dependency vulnerabilities)
