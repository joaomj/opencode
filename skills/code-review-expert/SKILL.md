---
name: code-review-expert
description: Expert code review with P0-P3 severity levels, covering SOLID principles, security risks, performance issues, and code quality. Uses independent sub-agents with automatic fallback to session model. Execution: Try both subagents → proceed with available reviewers → main agent fallback only if both fail.
license: MIT
---
# Code Review Expert

Comprehensive checklists for thorough code reviews with actionable severity levels.

## Model Availability & Fallback

This skill uses independent sub-agents (code-reviewer-1, code-reviewer-2) for thorough code review:

- **code-reviewer-1**: Primary reviewer, or session model as fallback
- **code-reviewer-2**: Secondary reviewer (different model than reviewer-1), or session model as fallback
- **Fallback Behavior**: If a primary model is unavailable (no API key, quota exceeded, provider unreachable), the system automatically uses the current session's model
- **No Manual Intervention Required**: The review process continues seamlessly regardless of model availability
- **Consistent Quality**: Both primary and fallback models follow the same review framework

**Note**: You don't need to configure anything - fallback is automatic and transparent.

The specific models used by each subagent are defined in their respective agent configuration files (`agents/code-reviewer-1.md` and `agents/code-reviewer-2.md`).

## Severity Levels

| Level | Name | Description | Action |
|-------|------|-------------|--------|
| P0 | Critical | Security vulnerability, data loss risk, correctness bug | Must block merge |
| P1 | High | Logic error, significant SOLID violation, performance regression | Should fix before merge |
| P2 | Medium | Code smell, maintainability concern, minor SOLID violation | Fix in this PR or create follow-up |
| P3 | Low | Style, naming, minor suggestion | Optional improvement |

## Checklist Categories

### 1. Preflight Context

Before analyzing code, understand:
- Git diff scope: `git diff <scope>`
- Changed files: `git diff --name-only`
- Entry points of changed modules
- Related tests

### 2. SOLID Principles

| Principle | Violation Examples | Severity |
|-----------|-------------------|----------|
| SRP (Single Responsibility) | Class/function does multiple things | P2-P3 |
| OCP (Open/Closed) | Hardcoded types, if-else chains | P2 |
| LSP (Liskov Substitution) | Child class breaks parent contract | P1 |
| ISP (Interface Segregation) | Fat interfaces with unused methods | P2-P3 |
| DIP (Dependency Inversion) | Depends on concrete implementations | P2 |

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

### 4. Performance Issues

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

### 6. Removal Planning

Before deleting code:
- Find all usages: `grep -r "function_name"`
- Check tests referencing it
- Verify no dynamic references
- Create removal PR with clear rationale

### 7. Model Fallback Behavior

When a reviewer sub-agent cannot use its configured model (e.g., no API key, quota exceeded, provider unreachable):

1. **Automatic Detection**: The agent detects model unavailability during initialization
2. **Graceful Degradation**: The current session's model is used instead
3. **Transparent Operation**: The review proceeds with the same checklists and output format
4. **Quality Assurance**: All models (primary or fallback) apply identical review criteria

**What this means for you**:
- No action required if a reviewer model is unavailable
- Code review continues without interruption
- Multiple independent reviews still happen (ensuring diverse perspectives)
- Output format and severity classification remain consistent

**Edge cases**:
- If ALL reviewer models fail to initialize, the skill uses the session model for both reviewers
- This maintains the dual-reviewer requirement while ensuring availability

## Review Execution Flow (For Main Agent)

When invoking the code-review-expert skill, follow this exact execution flow:

### Step 1: Try to Invoke Both Subagents (Parallel)

Always attempt to invoke BOTH subagents in parallel:
- `task(subagent_type="code-reviewer-1", ...)` with the review scope
- `task(subagent_type="code-reviewer-2", ...)` with the review scope

**Do NOT check model availability beforehand** - let the subagents handle their own fallback.

### Step 2: Determine Available Reviewers

After invocation, determine how many reviewers succeeded:

| Scenario | Action |
|----------|--------|
| **Both succeed** | Proceed with dual-reviewer workflow |
| **Only reviewer-1 succeeds** | Continue with single reviewer (reviewer-1) |
| **Only reviewer-2 succeeds** | Continue with single reviewer (reviewer-2) |
| **Both fail** | Perform the review yourself using the current session model |

### Step 3: Process Reviewer Output

If 1 or 2 reviewers succeed:
1. Collect JSON arrays from all successful reviewers
2. Merge findings, deduplicating by (file, line, severity, issue_title)
3. Group by file, prioritize P0 > P1 > P2 > P3
4. Write CODE_REVIEW.md with consolidated report

If both reviewers fail:
1. Load the code-review-expert skill checklists yourself
2. Perform the review against all checklists
3. Generate findings in the same JSON format
4. Write CODE_REVIEW.md with the consolidated report

### Step 4: Report Execution

In CODE_REVIEW.md, include:

**Review Execution Note** (add after Review Scope line):
- If 2 reviewers: "Dual reviewer execution completed"
- If 1 reviewer: "Single reviewer execution (reviewer-X unavailable)"
- If 0 reviewers: "All subagents unavailable, review performed by main agent using session model"

### Key Principles

- **Never block the review** - proceed with whatever reviewers are available
- **Prefer subagents** - only do the review yourself if both subagents fail
- **Maintain quality** - use the same checklists regardless of who performs the review
- **Transparency** - clearly document in the report how the review was executed

## CODE_REVIEW.md Output Format

```markdown
# Code Review Report

**Review Scope**: `<git-diff-scope>`
**Iteration**: `N` of `3`
**Execution**: `<execution-note>`
**Reviewers**: code-reviewer-1, code-reviewer-2
*Note: Models are configured in agents/code-reviewer-*.md; fallback to session model may occur automatically if primary is unavailable.*

## Summary

- P0: `X` - Critical issues (must fix)
- P1: `Y` - High priority (should fix)
- P2: `Z` - Medium priority (fix or follow-up)
- P3: `W` - Low priority (optional)

## Findings by File

### file/path.py (P0, P1, P2, P3)

**[P0] Issue Title**
- **Line**: `N`
- **Severity**: P0
- **Description**: Issue details
- **Fix**: Recommended fix

[Repeat for all issues]

## Iteration History

| Iteration | P0 | P1 | P2 | P3 | Fixed |
|-----------|----|----|----|----|-------|
| 1 | X | Y | Z | W | - |
| 2 | X' | Y' | Z' | W' | Z+Y-X'-Y' |
```
