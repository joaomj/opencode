---
name: code-reviewer
description: P0-P3 structured code review with FAIL-CLOSED verdict. Use when the user asks to review code, review a diff, or before merging. Reviews are task-scoped. The skill enforces SOLID, security, performance, and quality checklists.
---

# Code Review

**FAIL-CLOSED**: `passed` MUST be `false` if `p0 > 0` OR `p1 > 0`.
If any P0 or P1 issue exists, the ONLY valid verdict is `passed: false`.
This is non-negotiable.

## Task-Scoped Reviews

Reviews focus ONLY on code directly related to the current task context.

| Task Context Type | How to Scope |
|-------------------|--------------|
| Jira Issue | Review only files changed to address the issue |
| Task Plan | Review only files modified to implement the plan |
| Feature Request | Review only files related to the feature |
| Bug Fix | Review only files touched by the fix |
| Refactor | Review only files within refactor scope |

Before reviewing, identify the task context:
1. Ask user: "What is the task context for this review?"
2. Extract the specific files/functions involved
3. Limit review scope to those files and their direct dependencies
4. Do NOT review unrelated code

## Severity Levels

| Level | Name | Description | Action |
|-------|------|-------------|--------|
| P0 | Critical | Security vulnerability, data loss risk, correctness bug | Must block merge |
| P1 | High | Logic error, significant SOLID violation, performance regression | Should fix before merge |
| P2 | Medium | Code smell, maintainability concern, minor SOLID violation | Fix in this PR or create follow-up |
| P3 | Low | Style, naming, minor suggestion | Optional improvement |

## Checklist Categories

### 1. SOLID Principles

| Principle | Violation Examples | Severity |
|-----------|-------------------|----------|
| SRP (Single Responsibility) | Class/function does multiple things | P2-P3 |
| OCP (Open/Closed) | Hardcoded types, if-else chains | P2 |
| LSP (Liskov Substitution) | Child class breaks parent contract | P1 |
| ISP (Interface Segregation) | Fat interfaces with unused methods | P2-P3 |
| DIP (Dependency Inversion) | Depends on concrete implementations | P2 |

### 2. Security Scan

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
| Missing lockfile update | Lockfile not updated with dependency changes | P0 |
| No hash in lockfile | Requirements compiled without `--generate-hashes` | P1 |
| Blind upgrade | `uv lock --upgrade` without `--upgrade-package` | P2 |
| Unsafe download | `curl | bash` patterns in CI/scripts | P1 |
| exclude-newer missing | `pyproject.toml` lacks `exclude-newer` config | P1 |
| Trivy scan missing | No `trivy fs` run before PR; HIGH/CRITICAL CVEs | P0 |

### 3. Performance Issues

| Issue | Examples | Severity |
|-------|----------|----------|
| N+1 Queries | Inside loops | P1-P2 |
| Missing Indexes | Slow joins | P2 |
| Memory Leaks | Unclosed resources | P1 |
| CPU Hotspots | O(n^2) where O(n) possible | P2 |
| Pagination | Loading all records | P2 |

### 4. Code Quality

| Issue | Examples | Severity |
|-------|----------|----------|
| Swallowed Exceptions | `pass` in except | P2 |
| Async Errors | Missing await | P1 |
| Type Errors | Wrong types passed | P1 |
| Null/Empty | No validation | P2 |
| Boundary Conditions | Off-by-one errors | P1 |
| Dead Code | Unused variables | P3 |

## Review Execution Flow

### Step 1: Identify Task Context

ALWAYS ask the user for task context before reviewing:

```
What is the task context for this review?
Options:
1. Add Jira issue number (e.g., PROJ-123)
2. Provide path to task plan file
3. Describe the feature/bug being addressed
4. Specify files to review manually
```

Once context provided:
1. Extract specific scope (files, functions, modules)
2. Identify which changed files are directly related vs tangential
3. Create review scope document

### Step 2: Security Scan

Before code analysis, run the security scanner:

```bash
trivy fs --scanners vuln,secret,misconfig .
```

Any HIGH or CRITICAL finding is a **P0** blocker.

### Step 3: Analyze Code

1. **Get the diff**: `git diff <scope>`
2. **Apply each checklist category**:
   - SOLID principles (SRP, OCP, LSP, ISP, DIP)
   - Security risks (XSS, injection, SSRF, race conditions)
   - Performance (N+1 queries, CPU, memory)
   - Error handling (swallowed exceptions, async errors)
   - Boundary conditions (null, empty, numeric limits)
3. **Categorize findings by severity** (P0-P3)
4. **Filter findings to task scope only**

### Step 4: Ask User Before Writing Report

BEFORE writing CODE_REVIEW.md, ask the user:

```
Review completed. Found:
- P0: X critical issues
- P1: Y high priority issues
- P2: Z medium priority issues
- P3: W low priority issues

Write the review report to CODE_REVIEW.md? (yes/no)
```

If user says yes, write CODE_REVIEW.md. If no, present findings inline, do not create file.

### Step 5: Write Report (After User Approval)

```markdown
# Code Review Report

**Review Scope**: `<git-diff-scope>`
**Task Context**: `<jira-issue OR plan-file OR feature-description>`
**Task Scope**: `<files/functions directly related to task>`
**Excluded**: `<files/sections excluded from this review>`
**Iteration**: `N` of `3`

## Summary

- P0: `X` - Critical issues (must fix)
- P1: `Y` - High priority (should fix)
- P2: `Z` - Medium priority (fix or follow-up)
- P3: `W` - Low priority (optional)

**Note**: This review is scoped to the task context. Issues in unrelated code are not included.

## Findings by File

### file/path.py (P0, P1, P2, P3)

**[P0] Issue Title**
- **Line**: `N`
- **Severity**: P0
- **Description**: Issue details
- **Fix**: Recommended fix
- **Task Relation**: How this relates to the current task

## Iteration History

| Iteration | P0 | P1 | P2 | P3 | Fixed |
|-----------|----|----|----|----|-------|
| 1 | X | Y | Z | W | - |
| 2 | X' | Y' | Z' | W' | Z+Y-X'-Y' |
```

## Key Principles

| Principle | Behavior |
|-----------|----------|
| **FAIL-CLOSED** | `passed: false` if P0>0 or P1>0. Non-negotiable. |
| **Structured verdict** | Every review MUST include JSON verdict: `{"passed": bool, "p0": N, "p1": N, "p2": N, "p3": N, "issues": [...]}` |
| **Task-scoped** | Review only code directly related to the task |
| **User approval** | Always ask before writing the review document |
| **Transparency** | Document execution mode and any limitations |
| **Thoroughness** | Apply all checklists regardless of scope |
