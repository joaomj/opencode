# Skill: tdd-enforcement

Enforces Test-Driven Development practices with configurable strictness and coverage gates.

## Non-Negotiable Rules (STOP if violated)

| Rule | Violation = STOP |
|------|-------------------|
| Test-first for features | Block until failing test exists (or user justification) |
| 80% coverage minimum | Block commit if `pytest --cov` reports <80% |
| Behavior assertions | Tests must verify outcomes, not internals |
| No orphan test files | Tests must correspond to production code |

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `tdd.strictness` | `warn` | `block` = hard stop, `warn` = justification required |
| `tdd.coverage_threshold` | `80` | Minimum coverage percentage |
| `tdd.auto_scaffold` | `ask` | `auto` = create testfile, `ask` = prompt, `never` |
| `coverage.critical_path_only` | `false` | If true, only require tests for business logic |

## Test-First Protocol

### For New Features

1. **Detect**: User requests implementation
2. **Check**: Does test file exist?
3. **Prompt**: "Create test scaffold for `{module}` first?"
4. **Generate**: If yes, create test file with describe/test blocks
5. **Write failing test**: Add test case for feature
6. **Gate**: Require test to run (and fail) before implementation
7. **Implement**: Write minimal code to pass
8. **Verify**: Run tests, check coverage

### For Bug Fixes

1. **Reproduce**: Write test that demonstrates bug
2. **Verify test fails**: Confirm bug exists
3. **Fix**: Implement minimal fix
4. **Verify test passes**: Confirm fix works
5. **Gate**: No commit until test passes

### For Refactors

1. **Check**: Do tests exist for code being refactored?
2. **If no tests**: ASK "Add characterization tests first?"
3. **If yes**: Proceed with refactor, keep tests green

## TDD Cycle (RED-GREEN-REFACTOR)

### Step 1: RED - Write Failing Test
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

### Step 2: GREEN - Write Minimal Code
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

### Step 3: REFACTOR - Improve Code
- Extract methods, reduce duplication, improve naming
- Keep tests green throughout refactoring
- Run tests after each change

## Coverage Gate Enforcement

### Pre-Commit Hook Template
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

### CI Gate Template
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

## Test Quality Checklist

### Behavior Assertions (Required)
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

### Edge Cases (Required)
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

### Error Paths (Required)
```python
def test_database_connection_failure():
    with mock.patch('db.connect', side_effect=ConnectionError):
        with pytest.raises(ServiceUnavailable):
            fetch_user(1)

def test_invalid_input_types():
    with pytest.raises(TypeError):
        process(user_id="not_a_number")
```

## Warning Escalation Protocol

When user requests implementation without test:

### Level 1: Initial Prompt
```
"I recommend writing the test first. This ensures the implementation meets requirements and provides a safety net for future changes. Create test scaffold?"
```

### Level 2: If User Declines
```
"Understood. Please add justification in commit message: 'test-after: [brief reason for skipping test-first]'

Example: 'test-after: spike to validate API contract before stabilizing'"
```

### Level 3: Track Compliance
```
Log: test-first compliance for project health metrics
Note: Repeated test-after commits may indicate process issues
```

## Test File Naming Conventions

| Language | Pattern |
|----------|---------|
| Python | `tests/test_{module}.py` or `tests/{module}_test.py` |
| JavaScript/TypeScript | `{module}.test.ts` or `{module}.spec.ts` |
| Go | `{module}_test.go` |

## Test Organization

```
project/
├── src/
│   └── user_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # shared fixtures
│   ├── test_user_service.py  # unit tests
│   └── integration/
│       └── test_user_api.py  # integration tests
└── pyproject.toml
```

## Phase Gate Template

```markdown
## Phase X: Feature Implementation
**Estimation**: X days

### Pre-Requisite Gate
- [ ] Test file created: `tests/test_{module}.py` OR user declined with justification
- [ ] At least one failing test case for feature

### Tasks
1. Write minimal code to pass test
2. Run tests: `pytest tests/test_{module}.py -v`
3. Refactor if needed
4. Add more test cases (RED-GREEN-REFACTOR cycle)

### Gate Criteria
- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] No new warnings
- [ ] Code passes lint (ruff check)
```

## Exemptions

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

## Completion Checklist

- [ ] Chronological document order followed (PRD -> Design -> Specs -> Plan)
- [ ] Tests written BEFORE implementation (TDD)
- [ ] All gate criteria met
- [ ] Approval obtained before each phase
- [ ] All tests pass (pytest)
- [ ] Lint passes (ruff check)
- [ ] Coverage >= 80%
- [ ] Behavior assertions present
- [ ] Edge cases covered
- [ ] Error paths tested
- [ ] Documentation updated

Base directory for this skill: file:///Users/admin/.config/opencode/skills/tdd-enforcement
Relative paths in this skill are relative to this base directory.