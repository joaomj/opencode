---
name: testing-best-practices
description: Use for test strategy, regression tests, e2e tests, blackbox testing, and reviewing test quality. The agent writes tests that run against a live system (dev server, staging, production), using the same tools a user has: browser, terminal, HTTP client. No mocking internals.
license: MIT
---

# Testing Best Practices

Use this skill whenever writing, changing, reviewing, or planning tests. The goal is high-signal tests that catch real regressions when system behavior diverges from user expectations.

## Core Doctrine

The agent tests the system the same way a real user does.

- **E2E-first**. The default test type is an end-to-end test that runs against a live instance (dev server, staging, production). The agent starts the app or connects to a running instance and exercises it from the outside.
- **Blackbox only**. Tests know nothing about internal implementation. No inspecting private methods, no asserting internal state, no patching internals. The system is a black box.
- **Same tools as the user**. The agent tests with a browser, a terminal, an HTTP client, a CLI, a WebSocket client -- whatever tools a real user or operator uses to interact with the system.
- **Assert user-visible outcomes**. Assert on API response bodies and status codes, rendered HTML/UI state, CLI stdout/stderr, files written, database state observable by the user, logs, and events -- not internal call graphs or internal state.
- **No mocking internals**. The test exercises real code paths with real dependencies. A test database, a test broker, a test filesystem are acceptable. Patching or mocking internal functions, classes, or modules is not.
- **A bug is not fixed until an e2e test reproduces it**. Reproduce the bug at the user-facing level. If you cannot reproduce it there, you have not found it.
- **Error paths matter as much as happy paths**. Test what the user sees on failure: status codes, error bodies, UI messages. Do not test internal exception handlers in isolation.
- **Every fixed bug must become an e2e regression test**.
- **Release readiness** benefits from checklists: what e2e tests passed, what was skipped, what was manually verified, what remains risky.

## The Agent's Test Toolkit

The agent must be given the same interfaces a real user has:

| Interface | Tool | Example |
|-----------|------|---------|
| Web UI | Browser automation (Playwright, Selenium) | Navigate, click, fill forms, assert visible text, screenshot |
| REST/GraphQL API | HTTP client (httpx, requests, curl) | Send requests, assert status codes, assert response body shape |
| CLI | Subprocess / terminal | Run commands, assert exit codes, assert stdout/stderr |
| WebSocket/SSE | WebSocket client | Connect, send messages, assert received events |
| Mobile | Appium, XCTest, Espresso | Tap, swipe, assert UI elements |
| Email | IMAP/POP3 client, Mailpit API | Assert email received, assert content |

The agent does NOT use: `unittest.mock`, `pytest.monkeypatch` for internal code, `MagicMock`, `patch.object`, `jest.mock` for local modules, or any other tool that replaces internal code paths.

## Testing Against Running Instances

Tests target a running instance. There are three deployment levels:

1. **Dev server** (default): Start the app locally with a fresh test database and dependencies. Run tests against `localhost`. This is the primary target for feature work.
2. **Staging/CI**: Deploy to an ephemeral environment and run tests there. Useful for PR validation.
3. **Production** (smoke/canary): Run a subset of critical-path tests against production. These are read-only and non-destructive.

### Dev Server Pattern

```python
import subprocess
import time
import httpx
import pytest


@pytest.fixture(scope="session")
def dev_server():
    proc = subprocess.Popen(
        ["python", "-m", "myapp", "--db", "sqlite:///tmp/test.db"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2)
    yield "http://localhost:8000"
    proc.terminate()
    proc.wait()


def test_user_signup_and_login(dev_server: str) -> None:
    client = httpx.Client(base_url=dev_server)

    r = client.post("/auth/signup", json={"email": "a@b.com", "password": "secret"})
    assert r.status_code == 201
    assert "token" in r.json()

    r = client.post("/auth/login", json={"email": "a@b.com", "password": "secret"})
    assert r.status_code == 200
    assert r.json()["token"] is not None
```

### Browser Pattern

```python
from playwright.sync_api import sync_playwright


def test_signup_form_submits_and_redirects(dev_server: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{dev_server}/signup")

        page.fill('input[name="email"]', "a@b.com")
        page.fill('input[name="password"]', "secret")
        page.click('button[type="submit"]')

        page.wait_for_url(f"{dev_server}/dashboard")
        assert page.text_content("h1") == "Dashboard"
        browser.close()
```

### CLI Pattern

```python
import subprocess


def test_cli_export_produces_csv() -> None:
    result = subprocess.run(
        ["python", "-m", "myapp", "export", "--format", "csv", "--user", "1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "id,name,email" in result.stdout
```

## Test Taxonomy

### E2E Tests (primary, default)

Every test that exercises the system from the outside, against a running instance. E2E tests cover:

- User workflows (signup -> login -> create -> view -> edit -> delete)
- API contracts (request/response shape, status codes, error bodies)
- CLI behavior (exit codes, stdout, stderr, file output)
- Browser interactions (navigation, form submission, UI state)
- Cross-service interactions observable at the boundary
- Authorization (what each role can and cannot do)
- Error responses (what the user sees when things fail)

### Property Tests (for pure logic only)

The only non-e2e tests allowed. Apply exclusively to pure functions: same input always produces same output, no side effects, no I/O.

Good targets: parsers, validators, serializers, normalizers, math utilities, cryptographic functions, state machines.

```python
from hypothesis import given
from hypothesis import strategies as st


@given(st.lists(st.integers()))
def test_sort_is_idempotent(values: list[int]) -> None:
    once = sorted(values)
    twice = sorted(once)
    assert twice == once
```

If a property test finds a failure, save the minimized case as a permanent regression test.

### What No Longer Exists

- **Unit tests that mock internals**: Replaced by e2e tests against the running instance.
- **Integration tests that only wire internal components**: Replaced by e2e tests that cross the full stack.
- **Contract tests with mock servers**: Replaced by e2e tests against real endpoints.
- **Tests that assert internal call order or private state**: These test implementation, not behavior. Deleted on sight.

## Regression Test Workflow

For bug fixes:

1. Reproduce the bug at the user-facing level (e2e test that fails against the running instance).
2. Run the test and confirm it fails with the observed user-visible symptom.
3. Implement the minimal fix.
4. Run the e2e regression test and confirm it passes.
5. Run the full e2e suite.
6. Keep the regression test permanently.

Good regression names:

- `test_regression_16767_user_cannot_delete_published_post`
- `test_empty_cart_checkout_returns_400_not_500`
- `test_retry_after_timeout_does_not_duplicate_order`

Bad regression names:

- `test_bug`
- `test_fix`
- `test_works`

## Feature Test Workflow

For new features:

1. Identify the user-visible workflow and expected outcomes.
2. Write an e2e test that exercises the complete workflow against a running instance.
3. Assert user-visible results: API responses, UI state, CLI output, persisted data.
4. Add additional e2e tests for error paths, edge cases, and authorization boundaries -- all at the user-facing level.
5. Do NOT write unit tests for internal functions. If a function is complex enough to need isolated testing, it is a candidate for a property test -- and only if it is pure (no side effects, no I/O).

## E2E Test Patterns

### API Tests (httpx against live server)

```python
import httpx
import pytest


@pytest.fixture(scope="module")
def api(dev_server: str) -> httpx.Client:
    return httpx.Client(base_url=dev_server)


def test_create_and_get_resource(api: httpx.Client) -> None:
    r = api.post("/items", json={"name": "widget"})
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = api.get(f"/items/{item_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "widget"


def test_duplicate_creation_is_rejected(api: httpx.Client) -> None:
    payload = {"idempotency_key": "abc", "name": "widget"}
    api.post("/items", json=payload)
    r = api.post("/items", json=payload)
    assert r.status_code == 409
    assert "already exists" in r.json()["detail"]


def test_unauthenticated_request_is_rejected(api: httpx.Client) -> None:
    r = api.get("/items")
    assert r.status_code == 401


@pytest.mark.parametrize("role,expected_status", [
    ("admin", 200),
    ("user", 403),
    ("anonymous", 401),
])
def test_role_based_access(dev_server: str, role: str, expected_status: int) -> None:
    client = httpx.Client(base_url=dev_server, headers={"X-Role": role})
    r = client.get("/admin/dashboard")
    assert r.status_code == expected_status
```

### Browser Tests (Playwright against live server)

```python
from playwright.sync_api import sync_playwright


def test_user_can_complete_checkout(dev_server: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(f"{dev_server}/products")
        page.click('button:has-text("Add to cart")')
        page.click('a:has-text("Cart")')
        page.click('button:has-text("Checkout")')

        page.fill('input[name="address"]', "123 Main St")
        page.click('button:has-text("Place Order")')

        page.wait_for_selector("text=Order confirmed")
        assert page.text_content(".order-id") is not None
        browser.close()
```

### CLI Tests (subprocess against installed app)

```python
import subprocess


def test_cli_version_flag() -> None:
    result = subprocess.run(
        ["myapp", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "myapp v" in result.stdout


def test_cli_import_rejects_missing_file() -> None:
    result = subprocess.run(
        ["myapp", "import", "/nonexistent/file.csv"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()
```

## Assertions: What to Check

| Layer | Assert On |
|-------|-----------|
| HTTP API | Status code, response body shape, response body values, headers |
| Browser | Visible text, element presence/absence, URL, page title, form values |
| CLI | Exit code, stdout, stderr, written files |
| Database | Rows inserted/updated/deleted (query via the app's own API, not direct DB access unless testing data migrations) |
| Email | Delivery, subject, body content, links |
| Logs | Error presence, structured fields |

Never assert on:
- Internal function was called or not called
- Internal state of a class or module
- Order of internal method invocations
- Private attributes or methods

## Dependency Management for Tests

Use real dependencies, not mocks:

| Need | Solution |
|------|----------|
| Database | Test database instance (SQLite file, Postgres test container, Docker compose) |
| Cache | Real Redis with test prefix/namespace |
| Message queue | Real broker with test queues (RabbitMQ test vhost, Redis test stream) |
| File storage | Temporary directory (`tmp_path`) or MinIO test bucket |
| Email | Mailpit, mailhog, or catch-all SMTP server |
| External API | Local fake server that implements the same HTTP contract, or VCR-style record/replay |
| Time | System time for e2e tests; inject a configurable clock for pure logic property tests only |
| UUIDs/randomness | Real randomness for e2e tests; deterministic generator for property tests only |

If a dependency cannot run locally, use a test instance in CI, not a mock.

## Low-Signal Test Anti-Patterns

Reject or rewrite tests that:

- Mock or patch any internal function, class, or module.
- Use `unittest.mock`, `MagicMock`, `patch.object`, `jest.mock` for local code.
- Assert that an internal helper was called.
- Assert internal state or private attributes.
- Test private methods directly.
- Contain no real I/O or system interaction.
- Have a vague name like `test_success`, `test_error`, `test_works`.
- Pass immediately when written for a bug fix (no red-green).
- Duplicate implementation logic in the assertion.
- Only import a module and assert it exists.

## Test Review Checklist

When reviewing tests, ask:

- Does this test exercise the system from the outside, the way a user would?
- Does it run against a real instance (not mocked internals)?
- Would this test fail if the user-visible behavior regressed?
- Does it assert user-observable outcomes (status codes, response bodies, UI text, CLI output)?
- Are there any internal mocks or patches? If yes, reject.
- Does the test touch real secrets, user state, or live services without isolation?
- Is the test deterministic and safe to run repeatedly?
- Does the test name describe the user-facing behavior?

## Verification Commands

Run tests against a live instance:

```bash
python -m myapp --test-mode &
APP_PID=$!
pytest tests/e2e/ -q
kill $APP_PID
```

For a single test:

```bash
pytest tests/e2e/test_auth.py::test_user_signup_and_login -q
```

## Configuration

Recommended pytest config for e2e-only projects:

```toml
[tool.pytest.ini_options]
testpaths = ["tests/e2e"]
markers = [
    "e2e: user-visible end-to-end workflow against a running instance",
    "browser: requires browser automation (Playwright)",
    "property: pure logic property-based test",
    "slow: intentionally slow stress or soak test",
]
addopts = "-m 'not browser and not slow'"
```
