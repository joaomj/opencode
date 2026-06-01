---
name: e2e-testing
description: Integration and end-to-end testing SOP. Robust instructions on writing tests, good practices, patterns, and what to avoid. Use when writing or reviewing integration/e2e tests.
license: MIT
---

# E2E Testing SOP

Robust integration and end-to-end testing: when to use what, good patterns, and anti-patterns to avoid.

## Philosophy

- **Integration over mocking** — test real systems, real behavior
- **Mock only external boundaries** — 3rd-party APIs, services you can't spin up
- **NEVER mock internal collaborators** — no patching internal functions, modules, database calls, or same-codebase components
- **User-visible behavior only** — test what the user sees, not implementation details

## When to Use What

| Tool | Use Case |
|------|----------|
| TestClient (FastAPI/Flask) | API integration, middleware, auth flows, request/response contracts |
| Playwright | Full browser flows, UI interactions, visual verification |
| HTTP requests | Contract tests, external API parity checks |
| Docker | Databases, caches, message queues, external service dependencies |

## Test Structure

### Deterministic Fixtures

- Fixed seeds for random data
- Fixed timestamps (no `datetime.now()` in test data)
- Explicit setup and teardown per test or suite

### Environment

- Use Docker for test dependencies (Postgres, Redis, etc.)
- Clean up containers after suite completes
- Each test suite gets isolated resources

### Atomicity

- No shared mutable state between tests
- Each test sets up its own data
- Tests runnable in any order

## What to Avoid

### Mock Abuse

- **Never** mock internal functions to reach coverage targets
- **Never** mock database calls (use Docker + real DB)
- **Never** mock imports within the same codebase
- **Never** mock to avoid setting up proper test fixtures

### Fragile Tests

- No time-based assertions without fixed clocks
- No ordering dependencies between tests
- No sleeps or arbitrary waits (use `wait_for` or polling)
- No assertions on internal state or private methods

### Over-Specification

- Don't assert exact error message strings unless user-visible
- Don't assert log output format
- Don't test framework code (serializers, routers, middleware internals)

## Mock-Allow-Internal

If internal mocking is genuinely required (no alternative exists):

```python
def test_cached_response():
    """mock-allow-internal: Redis not available in CI — mock cache layer"""
```

Format: `mock-allow-internal: <specific reason>` in the test docstring. Reviewer enforces this. Without this marker, internal mocking is a P1 finding.

## Verification Checklist

- [ ] Test covers user-visible behavior
- [ ] No internal mocking (or marker present with valid reason)
- [ ] Deterministic fixtures (no random, no real time)
- [ ] Test environment is isolated (Docker or equivalent)
- [ ] Test passes reliably (no flakes)
- [ ] Setup and teardown are explicit
- [ ] Tests can run in any order
