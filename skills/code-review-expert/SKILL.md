---
name: code-review-expert
description: Expert code review with P0-P3 severity levels, covering SOLID principles, security risks, performance issues, and code quality
license: MIT
---
# Code Review Expert

Comprehensive checklists for thorough code reviews with actionable severity levels.

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

### 7. CODE_REVIEW.md Output Format

```markdown
# Code Review Report

**Review Scope**: `<git-diff-scope>`
**Iteration**: `N` of `3`
**Reviewers**: code-reviewer-1 (GPT-5.3 Codex), code-reviewer-2 (Claude Opus 4.5)

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
