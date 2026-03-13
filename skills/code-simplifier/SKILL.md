---
name: code-simplifier
description: Apply project standards to simplify code when explicitly requested. Pre-commit hooks handle automatic quality enforcement.
license: MIT
---
# Code Simplifier

Apply project standards to simplify code when explicitly requested by the user.

## When to Run

- **Primary**: When user requests "/simplify" or "simplify this code"
- **Implicit**: Pre-commit hooks automatically handle linting, formatting, and type checking
- **Scope**: Only files specified by user or modified in current session

## Pre-commit Hook Integration

The following checks are handled automatically by pre-commit hooks:

| Check | Pre-commit Tool |
|-------|-----------------|
| Linting | ruff |
| Formatting | ruff-format |
| Type checking | mypy |
| Secret detection | gitleaks |
| Dockerfile linting | hadolint |
| File length | check_file_length.py |
| Mock abuse | check_test_mock_abuse.py |

This skill complements those hooks by applying higher-level simplifications that require intelligent code restructuring.

## Non-Negotiables

| Rule | Action |
|------|--------|
| Never alter functionality | Only change how code works, not what it does |
| Only process session changes | Git diff --name-only since last commit |
| Must pass lint/typecheck | If simplification breaks checks, skip and report |
| Preserve type hints | Never remove existing type annotations |
| Respect .gitignore | Never modify ignored files |

## Simplification Rules

### Python Projects

| Category | Rule | Example |
|----------|------|---------|
| **Type Hints** | Add missing hints | `def func(x)` → `def func(x: int) -> str:` |
| **No Raw Dicts** | Convert to dataclasses/Pydantic | `{"name": str}` → `class Config(BaseModel):` |
| **Explicit Returns** | Add return type annotations | All functions have `-> Type` |
| **No Raw Exceptions** | Always log or re-raise | `except:` → `except Exception as e: logger.error(e)` |
| **Avoid Nested Ternaries** | Use if/elif/else chains | `a if b else (c if d else e)` → if/elif |
| **Function Naming** | Descriptive over terse | `fn()` → `process_user_data()` |
| **Single Responsibility** | Split multi-purpose functions | 1 function = 1 clear purpose |

### TypeScript/JavaScript Projects

| Category | Rule | Example |
|----------|------|---------|
| **Prefer Function Keyword** | Over arrow functions | `function foo()` not `const foo = ()` |
| **Explicit Return Types** | For top-level functions | `function getData(): Promise<Data>` |
| **No Nested Ternaries** | Use if/else or switch | 3+ conditions → switch |
| **Avoid Any Type** | Use proper types | `any` → `unknown` with type guards |
| **Destructuring** | Simplify nested access | `obj.a.b.c` → `const { a: { b: { c } } } = obj` |
| **Async/Await** | Over then chains | `await` instead of `.then().catch()` |

### General Rules (All Languages)

| Rule | Rationale |
|------|-----------|
| Reduce nesting | Flatten early returns, avoid arrow code |
| Eliminate redundancy | Remove duplicate logic, consolidate similar functions |
| Improve naming | Clear intent > short names |
| Remove obvious comments | Code should explain itself |
| Consolidate conditionals | Merge repeated checks |
| Prefer explicit code | Clever one-liners → readable code |

## What NOT to Simplify

| Do Not Simplify | Reason |
|-----------------|--------|
| Already simplified code | Would create churn without value |
| Test assertions | Explicit assertions are clearer |
| Configuration schemas | Verbose config is more maintainable |
| Generated code | Skip auto-generated files |
| Code marked `# noqa` or `# no-simplify` | Respect explicit opt-outs |

## Workflow

1. **Identify modified files**
   ```bash
   git diff --name-only HEAD
   ```

2. **Filter for source files**
   - Python: `*.py` (not test files, not generated)
   - TS/JS: `*.ts`, `*.tsx`, `*.js` (not build output)

3. **Apply simplification rules**
   - Read file contents
   - Apply applicable rules from above
   - Ensure functionality unchanged

4. **Validate changes**
   - Run `ruff check` (Python) or `eslint` (TS/JS)
   - Run `mypy` (Python) or `tsc` (TS)
   - If validation fails: revert changes, report issues

5. **Stage simplified files**
   ```bash
   git add <files>
   ```

6. **Proceed to commit**
   - Create commit with generated message
   - If validation failed: proceed with original code + report

## Integration with Commit Protocol

Pre-commit hooks run automatically during `git commit`. This skill is reserved for:

1. **User-requested simplification**: When user explicitly asks to simplify code
2. **Complex refactoring**: Changes that require intelligent restructuring beyond linting
3. **Before code review**: Optionally run to clean up code before submission

## How to Use

When user requests:
- "/simplify" or "simplify this code" → Run this skill
- "/commit" → Pre-commit hooks handle quality enforcement automatically

## Output Report

After simplification, report:

```
Code Simplification Report
- Files processed: X
- Simplifications applied: Y
- Validation passed: Yes/No
- Files skipped (validation failed): Z (list reasons)
```

## Edge Cases

| Scenario | Action |
|----------|--------|
| Large diff (>50 files) | Process only first 20, report "too many changes" |
| Binary files in diff | Skip silently |
| Syntax errors in modified code | Skip, report: "cannot parse file" |
| Validation fails after simplification | Revert changes for that file only |
| User has custom project rules | Detect from ruff.toml/pyproject.toml/.eslintrc |

## Success Criteria

Code is considered "simplified" when:

- Passes all linting checks
- All functions have type hints (Python/TS)
- No nested ternaries present
- Single-purpose functions only
- No raw dicts for API schemas
- Clear, descriptive naming
- Reduced nesting (cyclomatic complexity)

## Examples

### Example 1: Type Hints
```python
# Before
def get_user(id):
    return db.query(id)

# After
def get_user(id: int) -> User:
    return db.query(id)
```

### Example 2: No Raw Dicts
```python
# Before
def create_user(data: dict) -> dict:
    return {"id": 1, "name": data["name"]}

# After
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str

class User(BaseModel):
    id: int
    name: str

def create_user(data: UserCreate) -> User:
    return User(id=1, name=data.name)
```

### Example 3: Avoid Nested Ternaries
```python
# Before
status = "active" if user.is_active else ("pending" if user.is_pending else "inactive")

# After
if user.is_active:
    status = "active"
elif user.is_pending:
    status = "pending"
else:
    status = "inactive"
```

### Example 4: Prefer Function Keyword
```typescript
// Before
const processData = async (data: any) => {
    return await transform(data);
};

// After
async function processData(data: unknown): Promise<TransformedData> {
    return await transform(data);
}
```

## Validation Commands

| Language | Lint | Type Check |
|----------|------|------------|
| Python | `ruff check .` | `mypy .` or `pyright` |
| TypeScript | `eslint .` | `tsc --noEmit` |
| JavaScript | `eslint .` | (if using JSDoc) |

Always run validation before staging simplified code.
