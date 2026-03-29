---
name: python-best-practices
description: Complete Python development guide covering code quality, testing, security, dependency management, and TDD
license: MIT
---

# Python Best Practices

Comprehensive guide for Python development with focus on type safety, error handling, testing, security, and Test-Driven Development.

## Non-Negotiable Rules (STOP if violated)

Core rules defined in AGENTS.md. Python-specific additions:

| Rule | Violation = STOP |
|------|-----------------|
| Every function has type hints | Block if missing |
| No raw dicts for API schemas | Block if detected |
| Use `pdm add X` for dependencies | Block if direct pyproject.toml edit |
| Test-first for features | Block until failing test exists (or user justification) |
| 80% coverage minimum | Block commit if `pytest --cov` reports <80% |
| **ZERO test skipping** | **Block if `# noqa`, `@pytest.mark.skip`, or `@pytest.mark.xfail` found in tests** |

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

### Return Type Hints
- Always specify return types (even if `None`)
- Use `-> None` for void functions
- Use `-> NoReturn` for functions that always raise
- Prefer `list[str]` over `List[str]` (PEP 585)

### Argument Type Hints
- Every argument must have a type hint
- Use `Any` only when truly necessary
- Prefer `typing` module types for complex annotations

## Pydantic for API Schemas

### BaseModel Patterns
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

### No Raw Dicts for Schemas
- Always use `BaseModel` for request/response schemas
- Never accept `dict[str, Any]` directly in API endpoints
- Validate all inputs at the boundary

## Error Handling

### Specific Exception Types
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

### Never Swallow Exceptions
- Never use bare `except:` or `except Exception: pass`
- Log exceptions before re-raising
- Add context when re-raising: `raise SomeError("context") from e`
- Handle specific exceptions, not generic ones

## Logging

### Best Practices
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

### Security Rules
- Never log secrets: `logging.info(f"token={token}")` is FORBIDDEN
- Use `logger.exception()` inside except blocks (includes stack trace)
- Configure log levels appropriately
- Never expose sensitive data in log messages

## Ruff Configuration

### Default Rules
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

### Before Committing
Run: `ruff check .`

## Testing with Pytest

### Test Structure
```python
# test_processor.py
import pytest
from myapp.processor import DataProcessor

@pytest.fixture
def processor():
    return DataProcessor(config=Config())

@pytest.fixture
def sample_data():
    return [{"id": 1, "value": 100}]

def test_process_success(processor, sample_data):
    result = processor.process(sample_data)
    assert len(result) == 1
    assert result[0].processed_value == 200

def test_process_empty(processor):
    result = processor.process([])
    assert result == []

@pytest.mark.parametrize("input,expected", [
    (100, 200),
    (50, 100),
    (0, 0),
])
def test_process_calculation_behavior(processor, input, expected):
    result = processor.process([{"id": 1, "value": input}])
    assert result[0].processed_value == expected
```

### Core Test Policy
- Test behavior, not implementation details
- Do not test private methods directly (verify through public interfaces)
- Prefer integration tests for I/O boundaries (DB, HTTP, filesystem, queues)
- Keep unit tests for pure business logic and deterministic transforms
- A good test must fail when behavior regresses (not just when mocks change)

## TEST INTEGRITY - ZERO EXCEPTIONS

### The Non-Negotiable Rule

**NEVER skip failing tests. NEVER use `# noqa`, `@pytest.mark.skip`, `@pytest.mark.xfail`, or any mechanism to bypass test failures.**

The sole purpose of tests is to identify failures. When a test fails, it means:
1. **The code is wrong** → Fix the code
2. **The test is wrong** → Fix the test
3. **Both are wrong** → Fix both

**There is no option 4: "Suppress the failure"**

### Why This Matters

- **Tests are safety nets**: They catch bugs before they reach production
- **Skipping tests = accepting bugs**: You're choosing to ship broken code
- **Technical debt compounds**: Skipped tests never get fixed, they multiply
- **False confidence**: A green CI with skipped tests is worse than red CI

### Enforcement Protocol

#### When You See a Failing Test:
1. **STOP** - Do not proceed with any other work
2. **Investigate** - Determine if code or test is wrong
3. **Fix** - Make the minimal change to make the test pass
4. **Verify** - Run the test suite, confirm everything passes
5. **Commit** - Only when all tests pass

#### Forbidden Patterns (BLOCKED):
```python
# NEVER DO THIS
@pytest.mark.skip("TODO: fix later")  # BLOCKED
def test_feature():
    pass

# NEVER DO THIS  
@pytest.mark.xfail  # BLOCKED
def test_broken_feature():
    assert broken_code() == expected

# NEVER DO THIS
def test_feature():  # noqa: F841  # BLOCKED
    unused_var = 123
    assert actual == expected

# NEVER DO THIS
def test_feature():
    try:
        risky_operation()
    except:  # noqa: E722  # BLOCKED - bare except
        pass
```

#### Correct Approach:
```python
# GOOD: Fix the test or fix the code
def test_feature():
    result = feature_under_test()
    assert result == expected_value
    
# If this fails, investigate WHY it fails
# Fix the root cause, don't suppress the symptom
```

### Agent Instructions

**When you encounter a failing test:**
1. Ask: "Should I fix the code or fix the test?"
2. Investigate the failure thoroughly
3. Make the minimal change to resolve it
4. **Never** suggest skipping, marking as xfail, or adding noqa

**When you see `# noqa` in a test file:**
1. Remove it immediately
2. Fix the underlying issue
3. Run the test to verify it passes

**When a user asks to "just make it pass":**
1. Explain: "Tests exist to identify real failures"
2. Ask: "Should I fix the implementation or the test expectations?"
3. Proceed only after determining the correct fix

### Test Patterns
- Use fixtures for common setup
- Parametrize tests for multiple cases
- Test both success and failure paths
- Assert on outputs/state/events instead of call order/count
- Tests should be fast (avoid slow I/O)

### Test Layer Guidance (Default)
- Unit tests (pure logic): majority of suite
- Integration tests (component + real boundary): substantial coverage for every I/O path
- E2E tests: small set for critical user journeys

### Mock Usage Policy (Strict)

**Allowed (default)**
1. External service boundaries (HTTP SDKs, cloud clients, payment gateways)
2. Time/randomness control where determinism is required
3. Unavailable, rate-limited, or expensive third-party systems

**Not allowed (default)**
1. Mocking internal domain/services/repositories in unit tests
2. Testing private implementation paths through interaction assertions
3. Tests that only assert `mock.called`, call counts, or exact call order

**Exception rule**
- Internal mocks require explicit justification comment: `mock-allow-internal: <reason>`
- Prefer replacing internal mocks with fakes/in-memory adapters
- When exception is used, add or reference a paired integration test for the same behavior
- Optional allowlist file: `.test-mock-external-allowlist` (one external module prefix per line)
- Emergency opt-out per file only with explicit marker: `mock-policy: disable`

### Test Doubles Decision Table
| Need | Preferred Double | Why |
|------|------------------|-----|
| Keep test deterministic for time/UUID | Fake clock/ID generator | Stable, behavior-focused |
| Isolate third-party HTTP API | Stub/mock external client | Avoid network + cost |
| Simulate persistence behavior | In-memory fake repository | Less brittle than internal mocks |
| Verify service-to-service compatibility | Contract test (CDC/Pact) | Catches API drift early |

### LLM Anti-Patterns to Reject
- Patching the function/class under test
- Mocking every collaborator by default
- Asserting implementation internals instead of observable outcomes
- Writing tests that pass even if real integration is broken

## Test-Driven Development (TDD) - MANDATORY

**TDD is NON-NEGOTIABLE for all business logic. No exceptions.**

### The Law of TDD

1. **You are not allowed to write any production code unless it is to make a failing unit test pass.**
2. **You are not allowed to write any more of a unit test than is sufficient to fail; and compilation failures are failures.**
3. **You are not allowed to write any more production code than is sufficient to pass the one failing unit test.**

### TDD Cycle (RED-GREEN-REFACTOR) - STRICT ENFORCEMENT

#### Step 1: RED - Write Failing Test
```python
# tests/test_user_service.py
def test_register_duplicate_email():
    service = UserService(db)
    service.register("test@example.com", "password123")
    with pytest.raises(DuplicateEmailError):
        service.register("test@example.com", "different123")
```

Run: `pytest tests/test_user_service.py::test_register_duplicate_email`
Expected: FAIL (feature not implemented)

#### Step 2: GREEN - Write Minimal Code
```python
# src/user_service.py
def register(self, email: str, password: str) -> User:
    existing = self.db.query(User).filter_by(email=email).first()
    if existing:
        raise DuplicateEmailError(f"Email {email} already exists")
    user = User(email=email, password_hash=hash_password(password))
    self.db.add(user)
    self.db.commit()
    return user
```

Run: `pytest tests/test_user_service.py::test_register_duplicate_email`
Expected: PASS

#### Step 3: REFACTOR - Improve Code
- Extract methods, reduce duplication, improve naming
- Keep tests green throughout refactoring
- Run tests after each change

### Test-First Protocol - MANDATORY GATES

#### For New Features

**GATE 1: Test Must Exist**
- **Action**: Check if test file exists for the feature
- **If NO**: Create test file FIRST (before any implementation)
- **If YES**: Check if test covers the new behavior
- **Block**: Do NOT proceed to implementation without failing test

**GATE 2: Test Must Fail (RED)**
- **Action**: Run the test
- **Expected**: Test FAILS (proving the feature doesn't exist)
- **If PASSES**: Test is wrong - fix it first
- **Block**: Do NOT proceed until you see RED

**GATE 3: Implementation (GREEN)**
- **Action**: Write minimal code to make test pass
- **Rule**: Simplest possible solution, no premature optimization
- **Verify**: Run test, confirm it PASSES
- **Block**: Do NOT refactor while test fails

**GATE 4: Refactor**
- **Action**: Improve code quality while keeping tests green
- **Rule**: Run tests after every change
- **Block**: If tests fail during refactor, undo and try again

**VIOLATION CONSEQUENCES:**
- Writing implementation before test → MUST delete implementation, start over
- Skipping RED phase → Not TDD, violates protocol
- No test for new feature → Commit blocked, coverage gate fails

#### For Bug Fixes - REGRESSION TEST FIRST

**MANDATORY: Every bug fix requires a regression test.**

**GATE 1: Reproduce with Test**
- **Action**: Write a test that demonstrates the bug
- **Rule**: Test must describe the expected (correct) behavior
- **Verify**: Run test, confirm it FAILS (bug exists)
- **Block**: Do NOT fix bug without regression test

**GATE 2: Verify Failure**
- **Action**: Confirm test fails for the right reason
- **Check**: Error message matches bug description
- **Block**: If test passes, bug is misunderstood - investigate

**GATE 3: Minimal Fix**
- **Action**: Implement smallest change that makes test pass
- **Rule**: One bug = one focused fix, no scope creep
- **Verify**: Run test, confirm it PASSES

**GATE 4: Regression Prevention**
- **Action**: Run full test suite
- **Verify**: All tests pass, coverage maintained
- **Commit**: Only when everything is green

**WHY THIS MATTERS:**
- Without regression test, the bug WILL return
- Tests document expected behavior for future developers
- Prevents "whack-a-mole" debugging (fix one bug, create another)

#### For Refactors

1. **Check**: Do tests exist for code being refactored?
2. **If no tests**: ASK "Add characterization tests first?"
3. **If yes**: Proceed with refactor, keep tests green

### Coverage Gate Enforcement

#### Pre-Commit Hook Template
```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit - TDD coverage gate

MIN_COVERAGE=80

# Check if pytest-cov is available
if ! command -v pytest &> /dev/null; then
    echo "pytest not found, skipping coverage gate"
    exit 0
fi

# Run coverage check
pytest --cov --cov-fail-under=$MIN_COVERAGE --cov-report=term-missing

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Coverage below $MIN_COVERAGE%"
    echo "Add tests before committing."
    echo ""
    echo "To skip this check (not recommended):"
    echo "  SKIP_COVERAGE=1 git commit"
    exit 1
fi
```

#### CI Gate Template
```yaml
# .github/workflows/tdd-gate.yml
name: TDD Gate
on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
          pip install -r requirements.txt
      - name: Run tests with coverage
        run: pytest --cov --cov-fail-under=80 --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

### Test Quality Checklist

#### Behavior Assertions (Required)
```python
# GOOD: Tests outcome
def test_user_registration():
    user = register("test@example.com", "password")
    assert user.email == "test@example.com"
    assert user.is_active is True

# BAD: Tests implementation
def test_user_registration_bad():
    User.__init__.assert_called_once()# DON'T
```

#### Edge Cases (Required)
```python
def test_empty_input():
    with pytest.raises(ValidationError):
        process([])

def test_maximum_input():
    large_input = list(range(10000))
    result = process(large_input)
    assert len(result) <= MAX_LIMIT

def test_negative_input():
    with pytest.raises(ValueError):
        calculate(-1)
```

#### Error Paths (Required)
```python
def test_database_connection_failure():
    with mock.patch('db.connect', side_effect=ConnectionError):
        with pytest.raises(ServiceUnavailable):
            fetch_user(1)

def test_invalid_input_types():
    with pytest.raises(TypeError):
        process(user_id="not_a_number")
```

### Exemptions

The following are exempt from test-first requirement:

| Type | Reason |
|------|--------|
| Config files | No business logic |
| Boilerplate/setup | Auto-generated |
| Spike code | Experimental|
| Type definitions | No runtime behavior |
| Migrations | Database schema changes |
| Documentation | No executable code |

For exemptions, add comment: `# test-exempt: [reason]`

## Security

### Secrets Management
- Never hardcode secrets in code
- Never commit `.env` files
- Use environment variables for configuration

### Input Validation
- Validate all inputs at boundaries (using Pydantic)
- Sanitize user inputs
- Never trust client-side data
- Use parameterized queries to prevent SQL injection

## Dependency Management

### Using PDM
```bash
# Add dependency
pdm add package-name

# Add dev dependency
pdm add -d package-name

# Remove dependency
pdm remove package-name

# NEVER edit pyproject.toml directly
```

### Rule
- ALWAYS use `pdm add` for dependencies
- NEVER manually edit `pyproject.toml` to add dependencies
- NEVER use `pip install` for persistent dependencies

## File Organization

### Maximum File Length
- Python files should not exceed 300 lines
- Split large files into modules
- Related functions should be grouped together

### Import Order
1. Standard library
2. Third-party imports
3. Local imports

Use `ruff check . --fix` to auto-format imports.

## Completion Checklist

- [ ] All functions have type hints
- [ ] All arguments have type hints
- [ ] Error handling is specific (no bare except)
- [ ] Secrets are not hardcoded
- [ ] Tests written for new functionality
- [ ] Tests assert behavior/state (not implementation internals)
- [ ] Internal mocks only used with explicit `mock-allow-internal` justification
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Coverage >= 80% for new code
- [ ] `ruff check .` passes
- [ ] Dependencies added via `pdm add` (not manual edit)
- [ ] **ZERO `# noqa`, `@pytest.mark.skip`, or `@pytest.mark.xfail` in tests**
- [ ] **All tests pass - none skipped or suppressed**

Base directory for this skill: file:///Users/admin/.config/opencode/skills/python-best-practices
Relative paths in this skill are relative to this base directory.
