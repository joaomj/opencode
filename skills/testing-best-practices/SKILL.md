---
name: testing-best-practices
description: Use for test strategy, regression tests, pytest patterns, reducing mocks, logic coverage, property tests, integration tests, e2e tests, and reviewing test quality.
license: MIT
---

# Testing Best Practices

Use this skill whenever writing, changing, reviewing, or planning tests. The goal is high-signal tests that catch real regressions, not test volume.

## Core Doctrine

- Test observable behavior, not implementation details.
- Every fixed bug must become a regression test.
- A good test fails when the logic is wrong.
- Prefer logic and branch coverage over line-count coverage.
- Mock only external boundaries. Do not mock internal collaborators by default.
- Prefer fakes, in-memory adapters, temporary files, local test clients, and real pure functions over mocks.
- Smoke tests are allowed only as startup/import/health checks. They do not prove correctness.
- Tests must be deterministic, isolated, and safe to run repeatedly.
- No skipped, xfailed, or suppressed tests unless the user explicitly approves a tracked exception.

## SQLite-Inspired Standard

SQLite's testing policy is too large for ordinary projects, but its core habits transfer:

- A bug is not fixed until a test reproduces it.
- Boundary values must be tested explicitly.
- Error paths matter as much as happy paths.
- Anomaly tests should verify behavior under failure: I/O errors, network errors, timeouts, invalid inputs, partial writes, interrupted work, and retry paths.
- Coverage should ask whether each decision and branch matters, not merely whether each line ran.
- Fuzz and property tests are valuable for parsers, validators, serializers, state machines, permissions, and data transformations.
- Release readiness benefits from checklists: what passed, what was skipped, what was manually verified, and what remains risky.

## Lessons From Mature Repos

| Repo | Useful Pattern |
|------|----------------|
| `NousResearch/hermes-agent` | Regression-heavy suite, incident-number tests, hermetic test env, per-file pytest subprocess isolation, default exclusion of integration tests, separate stress/property suites. |
| `pydantic/pydantic` | Branch coverage, warnings as errors, broad edge-case validation, benchmarks separated from normal tests. |
| `pytest-dev/pytest` | Acceptance tests, example-project tests, plugin behavior tests, strict warnings, many behavior-focused regressions. |
| `encode/httpx` | Network tests marked separately, strict warnings, transport/client contract-style tests. |
| `pallets/flask` | Tox matrix across Python and dependency versions, branch coverage, minimum/latest dependency testing. |
| `HypothesisWorks/hypothesis` | Property-based tests, stateful tests, regression tests, invariant checks, shrinking-quality tests. |

## Test Taxonomy

| Type | Use For | Rules |
|------|---------|-------|
| Regression | Any fixed bug | Must fail before the fix and pass after. Name the behavior or issue. |
| Logic/unit | Pure business/domain logic | Use real code and focused fixtures. Table-test branches and boundaries. |
| Integration | Multiple internal components or I/O boundary | Prefer real app/test client, temporary DB/files, in-memory broker, local fake server. |
| E2E | User-visible workflow | Exercise the public interface. Keep few but meaningful. |
| Contract | External service/client compatibility | Verify request/response shape at the boundary. Do not call live services in normal CI. |
| Property | Invariant-heavy logic | Generate many inputs. Assert invariants, round trips, monotonicity, idempotency, or equivalence. |
| Fuzz | Parsers, decoders, untrusted input | Assert no crash, sane errors, and preserved invariants. Save discovered failures as regressions. |
| Stress | Concurrency, queues, retries, state machines | Separate from default suite. Check invariants under adversarial timing/load. |
| Benchmark | Performance-sensitive code | Separate from correctness tests. Fail only on deliberate performance gates. |
| Smoke | Import/startup/health | Keep minimal. Never treat as behavior coverage. |

## Regression Test Workflow

For bug fixes, use strict regression-first development:

1. Reproduce the bug with the smallest failing test.
2. Run the test and confirm it fails for the expected reason.
3. Implement the minimal fix.
4. Run the regression test and confirm it passes.
5. Run related tests, then the project's standard suite.
6. Keep the regression test permanently unless the behavior is intentionally removed.

Good regression names:

- `test_regression_16767_preserves_provider_scope`
- `test_empty_payload_returns_validation_error`
- `test_retry_does_not_duplicate_completed_job`

Bad regression names:

- `test_bug`
- `test_fix`
- `test_works`

## Feature Test Workflow

For new features, tests come from acceptance criteria:

1. Identify the public behavior and user-visible result.
2. Add at least one integration or e2e test for the main workflow when the change affects an API, CLI, UI, persistence, or external interface.
3. Add focused logic/unit tests for branches, boundaries, and error paths.
4. Use contract tests for external service request/response assumptions.
5. Avoid asserting internal call order unless ordering is itself part of the public behavior.

## Logic Coverage Checklist

When testing logic, cover:

- Happy path.
- Empty input.
- Single item.
- Multiple items.
- Minimum boundary.
- Maximum boundary.
- Just below and just above boundaries.
- Invalid input.
- Duplicate input.
- Ordering differences.
- Idempotent retry.
- Partial failure.
- Timeout or cancellation.
- Permission denied.
- State transition from each valid state.
- Invalid state transition.
- Serialization/deserialization round trip.
- Persistence save/load round trip.

Use parametrized tests for branch and boundary matrices.

```python
import pytest


@pytest.mark.parametrize(
    ("quantity", "expected"),
    [
        (0, "empty"),
        (1, "single"),
        (2, "many"),
    ],
)
def test_classifies_quantity_boundaries(quantity: int, expected: str) -> None:
    assert classify_quantity(quantity) == expected
```

## Good Test Criteria

A good test:

- Has a descriptive name stating behavior.
- Fails on a plausible real defect.
- Uses realistic inputs.
- Asserts outputs, persisted state, emitted events, API responses, files, logs, or errors that users/operators observe.
- Keeps setup smaller than the behavior under test.
- Uses deterministic time, randomness, and IDs.
- Fails with a useful assertion message or diff.

## Low-Signal Test Anti-Patterns

Reject or rewrite tests that:

- Only import a module.
- Only assert that something does not crash.
- Mock most of the system under test.
- Patch the function or class being tested.
- Assert that an internal helper was called instead of checking the outcome.
- Duplicate the implementation logic in the assertion.
- Use vague names like `test_success`, `test_error`, or `test_works`.
- Have no meaningful assertion.
- Test private methods directly instead of public behavior.
- Pass immediately when written for a bug fix.

Smoke test example, acceptable but low coverage:

```python
def test_app_imports() -> None:
    import myapp

    assert myapp is not None
```

Behavior test, higher signal:

```python
def test_rejects_duplicate_idempotency_key(client) -> None:
    payload = {"idempotency_key": "abc", "amount": 100}

    first = client.post("/payments", json=payload)
    second = client.post("/payments", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error"] == "duplicate_idempotency_key"
```

## Mock Policy

Allowed by default:

- External HTTP APIs.
- Cloud SDK clients.
- Payment gateways.
- Email/SMS providers.
- Time, UUID, randomness, and clocks when determinism is needed.
- Slow or unavailable third-party services.

Not allowed by default:

- Mocking internal domain services.
- Mocking repositories when a temporary database or in-memory fake is practical.
- Mocking the unit under test.
- Mocking internal helpers to force branches.
- Asserting internal call graphs as proof of correctness.

Preferred alternatives:

| Need | Preferred Pattern |
|------|-------------------|
| Database behavior | Temporary DB, transaction rollback fixture, in-memory SQLite if compatible. |
| File behavior | `tmp_path` with real reads/writes. |
| Time | Inject fake clock or freeze time at boundary. |
| UUIDs/randomness | Inject deterministic generator. |
| External HTTP | Local fake server, response stub at client boundary, contract fixture. |
| Message queue | In-memory broker fake that preserves queue semantics. |

If internal mocking is unavoidable, add a clear marker and pair it with integration coverage:

```python
# mock-allow-internal: legacy singleton cannot be constructed twice; covered by integration test.
```

## Pytest Patterns

Use `tmp_path` for filesystem tests:

```python
def test_writes_report_atomically(tmp_path) -> None:
    path = tmp_path / "report.txt"

    write_report(path, "ok")

    assert path.read_text(encoding="utf-8") == "ok"
```

Use `monkeypatch` for environment and boundary replacement:

```python
def test_uses_default_region(monkeypatch) -> None:
    monkeypatch.delenv("APP_REGION", raising=False)

    assert load_region() == "us-east-1"
```

Use `pytest.raises` to assert error type and message:

```python
def test_rejects_negative_amount() -> None:
    with pytest.raises(ValueError, match="amount must be positive"):
        charge(amount=-1)
```

Mark slow or external suites explicitly:

```python
pytestmark = pytest.mark.integration
```

Recommended default config:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
filterwarnings = ["error"]
markers = [
  "integration: requires external services or full app wiring",
  "e2e: user-visible end-to-end workflow",
  "slow: intentionally slow stress or soak test",
]
addopts = "-m 'not integration and not e2e and not slow'"
```

## Hermetic Test Environment

Tests should not depend on the developer machine.

- Clear credential environment variables in tests.
- Use per-test temp directories for home/config/state.
- Pin timezone and locale when relevant.
- Avoid live network calls in default CI.
- Avoid real user config, caches, and global state.
- Reset mutable module-level state or isolate test files in separate processes when state leakage is common.
- Use deterministic random seeds unless the test intentionally explores randomness.

## Property-Based Testing

Use property tests when examples are too narrow.

Good targets:

- Parsers and serializers.
- Validators.
- Normalizers.
- Permission rules.
- Scheduling logic.
- State machines.
- Migrations and round trips.
- Numeric and date/time logic.

Common properties:

- Round trip: `decode(encode(x)) == x`.
- Idempotency: `normalize(normalize(x)) == normalize(x)`.
- Monotonicity: increasing input does not decrease output.
- Conservation: totals remain equal after transformation.
- Equivalence: optimized path equals reference implementation.
- Invariant: invalid states are never reachable.

Example:

```python
from hypothesis import given
from hypothesis import strategies as st


@given(st.lists(st.integers(), max_size=100))
def test_sort_is_idempotent(values: list[int]) -> None:
    once = sort_values(values)
    twice = sort_values(once)

    assert twice == once
```

When property testing finds a failure, save the minimized case as a normal regression test too.

## Mutation Testing

Mutation testing asks whether tests detect wrong logic.

Use it selectively for:

- Billing.
- Permissions.
- Security checks.
- Parsers and validators.
- Data migrations.
- Retry/idempotency logic.
- State machines.

Do not require mutation testing globally. It is a high-signal audit for critical logic, not a default tax on every change.

## Test Review Checklist

When reviewing tests, ask:

- Would this test fail if the bug returned?
- Does it assert user-visible or operator-visible behavior?
- Is there too much mocking?
- Is the setup realistic but minimal?
- Are boundary and error cases covered?
- Are warnings treated as failures?
- Does the test touch real secrets, user state, or live services?
- Could a refactor break the test while behavior remains correct?
- Is the test fast enough for the default suite?
- If slow or external, is it marked and separated?

## Verification Commands

Prefer the project's canonical runner. If none exists, start with:

```bash
pytest -q
pytest --cov --cov-branch
```

For a bug fix, first run the specific regression test:

```bash
pytest tests/path/test_file.py::test_regression_behavior -q
```

Then run the related suite and the full default suite.
