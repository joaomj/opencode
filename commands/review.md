---
description: Code review over current diff with P0-P3 findings, FAIL-CLOSED on P0/P1
model: openai/gpt-5.5
variant: high
---

# Code Review Command

**FAIL-CLOSED**: Verdict `passed` MUST be `false` if `p0 > 0` OR `p1 > 0`.
If any P0 or P1 issue exists, the ONLY valid verdict is `passed: false`.

## Severity Levels

| Level | Name | Description | Action |
|-------|------|-------------|--------|
| P0 | Critical | Security vulnerability, data loss risk, correctness bug | Must block merge |
| P1 | High | Logic error, significant SOLID violation, performance regression | Should fix before merge |
| P2 | Medium | Code smell, maintainability concern, minor SOLID violation | Fix or create follow-up |
| P3 | Low | Style, naming, minor suggestion | Optional improvement |

## Checklist Categories

### 1. Preflight

Before analysis:
- Review scope: !`git diff <ref>` (default: diff against main)
- Changed files: !`git diff --name-only <ref>`
- Entry points of changed modules
- Related tests

### 2. SOLID Principles

| Principle | Violation Examples | Severity |
|-----------|--------------------|----------|
| SRP | Class/function does multiple things | P2-P3 |
| OCP | Hardcoded types, if-else chains | P2 |
| LSP | Child class breaks parent contract | P1 |
| ISP | Fat interfaces with unused methods | P2-P3 |
| DIP | Depends on concrete implementations | P2 |

### 3. Security Scan

| Issue | Examples | Severity |
|-------|----------|----------|
| SQL Injection | User input in queries | P0 |
| XSS | Unsanitized output | P0 |
| SSRF | User-controlled URLs | P0 |
| Path Traversal | `../` in filenames | P0 |
| Auth/Authorization | Missing checks | P0-P1 |
| Race Conditions | Check-then-act | P1 |
| Secrets | Hardcoded keys/tokens | P0 |
| Unpinned dependency | `>=` without upper bound in requirements | P1 |
| Missing lockfile | Lockfile not updated with dependency changes | P0 |
| Blind upgrade | `uv lock --upgrade` without `--upgrade-package` | P2 |
| Unsafe download | `curl \| bash` patterns | P1 |
| Unsafe container | Privileged containers | P1-P0 |

### 4. Performance

| Issue | Examples | Severity |
|-------|----------|----------|
| N+1 Queries | Inside loops | P1-P2 |
| Missing Indexes | Slow joins | P2 |
| Memory Leaks | Unclosed resources | P1 |
| CPU Hotspots | O(n²) where O(n) possible | P2 |
| Pagination | Loading all records | P2 |

### 5. Code Quality

| Issue | Examples | Severity |
|-------|----------|----------|
| Swallowed Exceptions | `pass` in except | P2 |
| Async Errors | Missing await | P1 |
| Type Errors | Wrong types passed | P1 |
| Null/Empty | No validation | P2 |
| Boundary Conditions | Off-by-one errors | P1 |
| Dead Code | Unused variables | P3 |
| Hardcoded config | Values that should be centralized | P2 |
| Missing type hints | Public functions without annotations | P2 |

### 6. Failure-Resilient Execution

Apply this category strictly to scripts, CLIs, migrations, scrapers, batch jobs, data jobs, automation, filesystem generators, and any code with external side effects or long-running execution.

| Issue | Examples | Severity |
|-------|----------|----------|
| Missing idempotency | Retried run duplicates writes, sends duplicate requests, or corrupts state | P1-P2 |
| Missing checkpoint/resume | Long-running or multi-step job must restart from scratch after interruption | P2 |
| Silent failure | Exceptions swallowed, failed items only printed without durable record, process exits successfully after errors | P1-P2 |
| Missing durable logs | Operational job only logs to transient shell output | P2 |
| Unsafe concurrency | Duplicate runs can race without lock file, advisory lock, dedupe key, or atomic operation | P1-P2 |
| Unbounded loop | No batching, pagination, limits, timeouts, or periodic checkpointing | P2 |
| Non-atomic outputs | Checkpoint, state, or generated output can be left partially written | P2 |
| Missing dry-run | Destructive or external side-effecting operation cannot be previewed safely | P2-P3 |
| Missing final summary | Batch job does not report attempted, succeeded, skipped, failed, or retriable counts | P3 |

## Execution Flow

### Step 1: Identify Review Scope

Ask the user for the scope (if not already provided):
- "What should I review? (default: unstaged diff):"
  - `main` — diff against main branch
  - `HEAD` — last commit
  - `<commit>` — specific commit range
  - unstaged — working tree changes
  - Or provide a custom git ref range

If no scope is given, default to reviewing unstaged changes (`git diff`).

### Step 2: Get the Diff

!`git diff <scope>`

If the diff is empty, report "No changes to review" and exit.

### Step 3: Analyze Code Against Checklists

1. **Apply each checklist category** to every changed file
2. **Categorize findings by severity** (P0-P3)
3. **Filter findings to scope only** — do not review unchanged code
4. **Treat resilience gaps as defects** — for operational code, missing checkpointing, missing durable logs, non-idempotent retries, silent failures, and unsafe concurrent execution are review findings, not style preferences

### Step 4: Present Findings

Show a summary to the user:
```
Review summary:
  P0: N critical issues
  P1: N high priority issues
  P2: N medium priority issues
  P3: N low priority issues
```

Ask: "Write the review report? (yes/no)"

### Step 5: Output Report

If user says **yes**, produce a structured report:

- Present findings grouped by file, each with severity, line, description, and suggested fix
- Include a machine-readable JSON verdict at the end:
  ```json
  {"passed": bool, "p0": N, "p1": N, "p2": N, "p3": N, "issues": [{"file": "path", "line": N, "severity": "P0", "description": "...", "fix": "..."}]}
  ```
- If `passed` is `false`, explicitly state: **"Review FAILED — P0/P1 issues must be fixed before merge."**

If user says **no**, present findings inline without creating a file.
