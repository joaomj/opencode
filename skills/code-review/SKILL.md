---
name: code-review
description: Review changes since a fixed point for standards and specification compliance. Add a falsification-first adversarial review only for large, complex, high-risk, or explicitly requested diffs. FAIL-CLOSED on P0/P1. Can post results to GitHub PR.
metadata:
  credit: Matt Pocock (https://github.com/mattpocock/skills)
---

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the code conform to documented coding standards and pass concrete quality/security/resilience checks?
- **Spec** — does the code faithfully implement the originating spec or ticket?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings. Large, complex, high-risk, or explicitly adversarial reviews add focused sub-agents that try to prove the implementation incorrect.

## Process

### 1. Pin the fixed point

Whatever the user says is the fixed point — a commit SHA, branch name, tag, `main`, etc. Capture `git diff <fixed-point>...HEAD`.

If the user doesn't supply a fixed point:
1. Check for a PR: `gh pr view --json baseRefName 2>/dev/null || echo "no-pr"`
2. If PR found, diff against `origin/<baseRefName>`: `git fetch origin <baseRefName>` then `git diff origin/<baseRefName>...HEAD`
3. If no PR, ask: "What is the target branch? (default: main)", then diff against `origin/<answer>` after fetching

Only changes introduced by the current branch are reviewed. Never diff unstaged or working-tree changes.

### 2. Identify the spec source

Look for the originating spec: issue references in commit messages, a path the user passed, or a spec file under `docs/` or `specs/`.

### 3. Identify standards sources

Anything in the repo that documents how code should be written (`CODING_STANDARDS.md`, `CONTRIBUTING.md`).

### 4. Standards checklist categories

On top of whatever the repo documents, the Standards axis always checks the following categories with P0-P3 severity:

| Severity | Name | Action |
|----------|------|--------|
| P0 | Critical | Must block merge |
| P1 | High | Should fix before merge |
| P2 | Medium | Fix or create follow-up |
| P3 | Low | Optional improvement |

#### Smith baseline (always applies)

- **Mysterious Name** (P3) — rename to reveal purpose
- **Duplicated Code** (P2) — extract shared shape
- **Feature Envy** (P2) — move method onto the data it envies
- **Data Clumps** (P3) — bundle into one type
- **Primitive Obsession** (P2) — create a domain type
- **Repeated Switches** (P3) — polymorphism or shared map
- **Shotgun Surgery** (P2) — gather scattered changes into one module
- **Divergent Change** (P2) — split for single-responsibility
- **Speculative Generality** (P3) — delete unused abstraction
- **Message Chains** (P2) — hide walk behind one method
- **Middle Man** (P3) — call the real target directly
- **Refused Bequest** (P2) — use composition over inheritance

#### SOLID principles

| Principle | Violation Examples | Severity |
|-----------|--------------------|----------|
| SRP | Class/function does multiple things | P2-P3 |
| OCP | Hardcoded types, if-else chains | P2 |
| LSP | Child class breaks parent contract | P1 |
| ISP | Fat interfaces with unused methods | P2-P3 |
| DIP | Depends on concrete implementations | P2 |

#### Security scan

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

#### Performance

| Issue | Examples | Severity |
|-------|----------|----------|
| N+1 Queries | Inside loops | P1-P2 |
| Missing Indexes | Slow joins | P2 |
| Memory Leaks | Unclosed resources | P1 |
| CPU Hotspots | O(n²) where O(n) possible | P2 |
| Pagination | Loading all records | P2 |

#### Code quality

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

#### Failure-resilient execution (scripts, CLIs, migrations, scrapers, batch jobs, data jobs, automation, filesystem generators, any code with external side effects or long-running execution)

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

The repo's documented standards always override the baseline; each item is a labelled heuristic, never a hard violation.

### 5. Select the review depth

Start every review in **standard** mode. Escalate to **adversarial** mode only when at least one condition applies:

- The user explicitly asks for an adversarial, hostile, red-team, deep, or security review.
- The diff changes more than 300 non-generated lines or more than 8 non-test source files.
- The diff changes authentication, authorization, permissions, secrets, cryptography, payments, personally identifiable data, input parsing, or externally reachable endpoints.
- The diff changes persistence, schema or data migrations, concurrency, caching, retries, queues, transactions, background jobs, filesystem writes, or other external side effects.
- The diff introduces or materially changes a public API, dependency, infrastructure, deployment, or cross-service integration.
- The implementation has complex state transitions, non-obvious invariants, or a specification with meaningful failure modes.

Do not escalate solely because documentation, formatting, generated files, lockfiles, or test fixtures make the diff large. If the trigger is unclear, use standard mode and state the unresolved risk rather than starting a lengthy review.

State the selected mode and every trigger before reporting findings:

```
Review mode: adversarial
Triggers: persistence change; externally reachable endpoint
```

### 6. Spawn review sub-agents

**Standards sub-agent**: include the diff, standards-source files, the full checklist baseline (smells + all categories above), and the associated P0-P3 severity table. Report violations per file/hunk with severity, distinguish hard violations from judgement calls. Format each finding as:

```
file/path.py:15 (P1)
  Issue: Missing input validation on user-supplied data
  Fix: Add Pydantic model with field constraints
```

**Spec sub-agent**: include the diff and the spec. Report missing requirements, scope creep, and wrong implementations.

In standard mode, run only these two sub-agents. Keep findings focused on defects and documented standards, not speculative style suggestions.

In adversarial mode, retain the two baseline sub-agents and run applicable focused passes in parallel. Each pass assumes the implementation is wrong and attempts to falsify it:

- **Correctness and invariants**: derive intended invariants from the spec and code, then find inputs, sequences, or states that violate them.
- **Boundary and robustness**: test malformed input, empty values, limits, ordering, partial failure, timeouts, overflow, and resource exhaustion.
- **State and concurrency**: seek race conditions, stale reads, non-atomic updates, retry duplication, deadlocks, and invalid recovery after interruption.
- **Security and authorization**: seek trust-boundary failures, injection, traversal, data exposure, missing authorization, and denial of service.
- **Performance and operations**: seek unbounded work, unexpected complexity, N+1 calls, leaks, retry storms, missing backpressure, and unsafe observability.

Skip passes that cannot apply to the changed code. Do not invent hypothetical findings just to complete a pass.

Every adversarial finding must include:

```
file/path.py:15 (P1)
  Failure scenario: A retry after the remote timeout repeats the already-applied charge.
  Evidence: The request is issued before durable idempotency state is written.
  Impact: A customer can be charged twice.
  Reproduction: Send the same request twice after a simulated response timeout.
  Fix: Persist and enforce an idempotency key before the external call.
```

### 7. Aggregate

Present two reports under `## Standards` and `## Spec` headings. Do NOT merge or rerank findings.

**FAIL-CLOSED**: Verdict `passed` MUST be `false` if `p0 > 0` OR `p1 > 0`. If any P0 or P1 issue exists, the ONLY valid verdict is `passed: false`.

Start the Standards section with a summary:
```
P0: N critical issues
P1: N high priority issues
P2: N medium priority issues
P3: N low priority issues
```

End with one-line summary: total findings per axis and the worst issue within each.

If P0 > 0 or P1 > 0, state: **"Review FAILED — P0/P1 issues must be fixed before merge."**

### 8. Offer to post to GitHub PR

After presenting findings, check if the current branch is associated with a pull request:

```
`gh pr view --json number,url 2>/dev/null || echo "no-pr"`
```

If a PR exists, ask: **"Post this review as a comment on the pull request?"**

If user says **yes**:
1. Format the full review body
2. Execute: `gh pr comment <PR_NUMBER> --body "<formatted review>"`
3. Confirm: "Review posted to PR: <PR_URL>"

## Why two axes

A change can pass one and fail the other:
- Code that follows every standard but implements the wrong thing -> **Standards pass, Spec fail**
- Code that does exactly what was asked but breaks conventions -> **Spec pass, Standards fail**

Reporting separately stops one axis from masking the other.
