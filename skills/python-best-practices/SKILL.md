---
name: python-best-practices
description: Complete Python development guide covering code quality, testing, security, and dependency management
license: MIT
---

# Python Best Practices

Comprehensive guide for Python development with focus on type safety, error handling, testing, and security.

## Non-Negotiable Rules (STOP if violated)

| Rule | Violation = STOP |
|------|-----------------|
| Every function has type hints | Block if missing |
| No raw dicts for API schemas | Block if detected |
| No secrets in code | Block if detected |
| AGENT must never read .env files | Block if attempted |
| Use `pdm add X` for dependencies | Block if direct pyproject.toml edit |

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
def test_calculation(processor, input, expected):
    assert processor._calculate(input) == expected
```

### Test Patterns
- Use fixtures for common setup
- Parametrize tests for multiple cases
- Test both success and failure paths
- Mock external dependencies
- Tests should be fast (avoid slow I/O)

## Security

### Secrets Management
- Never hardcode secrets in code
- Never commit `.env` files
- AGENT must never Read `.env` files
- Application code can load `.env` using python-dotenv or pydantic-settings
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

## Pre-Commit Hooks (OPTIONAL)

### Installation
If `setup-hooks.sh` is missing in the codebase, you MUST ask the user before installing:

```
"Pre-commit hooks are not configured. Would you like me to install them?
This will add quality checks (linting, secrets detection, etc.) to your git workflow."
```

Only proceed with `curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash` if the user explicitly confirms "yes".

### Before Committing
If hooks are installed, run: `pre-commit run --all-files`

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
- [ ] AGENT never read `.env` files
- [ ] Tests written for new functionality
- [ ] `ruff check .` passes
- [ ] Dependencies added via `pdm add` (not manual edit)
- [ ] Pre-commit hooks installed only with user consent
