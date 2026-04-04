---
name: python-best-practices
description: Complete Python development guide covering code quality, testing, security, dependency management, and SDD
license: MIT
---

# Python Best Practices

## Non-Negotiable Rules

Core rules defined in AGENTS.md (OC001-OC010). Python-specific enforcement:

| Rule | Violation = STOP |
|------|-----------------|
| Every function has type hints (OC005) | Block if missing |
| No raw dicts for API schemas (OC001) | Block if detected |
| Use detected package manager for deps | Block if direct pyproject.toml edit |
| Lockfile must exist and be committed (OC009) | Block if no lockfile |
| SDD: specs before tests, tests before implementation (OC006) | Block until spec + failing test exists |
| 80% coverage minimum (OC007) | Block if `pytest --cov` < 80% |
| ZERO test skipping (OC008) | Block if `# noqa`, `skip`, or `xfail` found in tests |

## Type Hints

### Function Signatures

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

### Rules
- Always specify return types (even `None`)
- Use `-> NoReturn` for functions that always raise
- Prefer `list[str]` over `List[str]` (PEP 585)
- Every argument must have a type hint
- Use `Any` only when truly necessary

## Pydantic for API Schemas

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

## Error Handling

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

## Logging

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

## Ruff Configuration

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

## Testing with Pytest

### Structure

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

### Core Policy
- Test behavior, not implementation details
- Do not test private methods directly
- Prefer integration tests for I/O boundaries
- A good test must fail when behavior regresses

### Test Integrity (OC008)

**NEVER skip failing tests.** No `# noqa`, `@pytest.mark.skip`, `@pytest.mark.xfail`, or any suppression mechanism.

When a test fails:
1. STOP - do not proceed with other work
2. Investigate: is the code wrong or the test wrong?
3. Fix the root cause
4. Verify all tests pass

There is no option 4: "suppress the failure."

### Mock Usage

| Need | Preferred Double |
|------|------------------|
| External service isolation | Stub/mock external client |
| Time/UUID determinism | Fake clock/ID generator |
| Persistence simulation | In-memory fake repository |
| Service compatibility check | Contract test (CDC/Pact) |

**Allowed:** Mock external services (HTTP SDKs, cloud clients, payment gateways).
**Not allowed by default:** Mocking internal domain/services. If needed, add comment: `mock-allow-internal: <reason>` and pair with an integration test.

### LLM Anti-Patterns to Reject
- Patching the function/class under test
- Mocking every collaborator by default
- Asserting implementation internals instead of observable outcomes

## Spec-Driven Development (SDD)

SDD replaces traditional TDD for all business logic. Flow:

1. **Define specs first** - Write type signatures, contracts, Pydantic models, and edge cases BEFORE any implementation
2. **Write tests against specs** - Tests validate spec compliance
3. **Implement to fulfill specs** - Write minimal code
4. **Refactor** - Improve while keeping tests green

For bug fixes, write a regression test that reproduces the bug BEFORE fixing it.

Exempt from SDD: config files, boilerplate, type definitions, migrations, documentation. Add comment: `# test-exempt: [reason]`

See `/plan` command for full SDD workflow.

## Security

- Never hardcode secrets in code
- Never commit `.env` files
- Validate all inputs at boundaries using Pydantic
- Use parameterized queries to prevent SQL injection

## Dependency Management

| Detected file | Manager | Add | Install | Run |
|---------------|---------|-----|---------|-----|
| `uv.lock` | uv | `uv add X` | `uv sync` | `uv run ...` |
| `pdm.lock` | pdm | `pdm add X` | `pdm install` | `pdm run ...` |
| `poetry.lock` | poetry | `poetry add X` | `poetry install` | `poetry run ...` |
| None | **Suggest uv** | `uv init` then `uv add X` | `uv sync` | `uv run ...` |

- ALWAYS use the detected package manager
- NEVER manually edit `pyproject.toml` for dependencies
- ALWAYS commit the lockfile

## Supply Chain Security

| Control | How | Enforcement |
|---------|-----|-------------|
| Lockfile with hashes | `uv lock` / `pdm lock --hash` / `poetry lock` | OC009 |
| Delayed ingestion | `--exclude-newer` with 7-day buffer | OC010 |
| Vulnerability scanning | `pip-audit` in CI on every push/PR | CI pipeline |
| Security linting | Ruff `S` rules (Bandit: secrets, crypto, timeouts) | Pre-commit |

```bash
# Hash pinning
uv pip compile --generate-hashes requirements.in -o requirements.txt

# Delayed ingestion
uv pip compile --exclude-newer $(date -v-7d +%Y-%m-%d) requirements.in -o requirements.txt

# Vulnerability scanning
uvx pip-audit --desc
```

Recent incidents: axios (Mar 2026), telnyx (Mar 2026), Ultralytics (Dec 2024). Defense: hash pinning + delayed ingestion + pip-audit + Ruff S rules.

## File Organization

- Python files: max 300 lines
- Import order: stdlib -> third-party -> local
- Auto-format: `ruff check . --fix`

## Completion Checklist

- [ ] All functions have type hints
- [ ] Error handling is specific (no bare except)
- [ ] No secrets hardcoded
- [ ] Tests written for new functionality
- [ ] Tests assert behavior (not implementation)
- [ ] SDD followed: specs -> tests -> implementation
- [ ] Coverage >= 80% for new code
- [ ] `ruff check .` passes
- [ ] Dependencies added via package manager
- [ ] Lockfile committed
- [ ] ZERO test suppression mechanisms
