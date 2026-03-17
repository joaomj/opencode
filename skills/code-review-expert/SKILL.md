---
name: code-review-expert
description: Expert code review with P0-P3 severity levels, covering SOLID principles, security risks, performance issues, and code quality. Uses independent sub-agents with graceful degradation. Execution: Try both subagents → proceed with available reviewers → main agent fallback only if both fail. Task-scoped reviews focus only on relevant code changes.
license: MIT
---
# Code Review Expert

Comprehensive checklists for thorough code reviews with actionable severity levels.

## Task-Scoped Reviews

**IMPORTANT**: Code reviews should focus ONLY on code directly related to the current task context:

| Task Context Type | How to Scope |
|-------------------|--------------|
| Jira Issue | Review only files changed to address the issue |
| Task Plan | Review only files modified to implement the plan |
| Feature Request | Review only files related to the feature |
| Bug Fix | Review only files touched by the fix |
| Refactor | Review only files within refactor scope |

**Before reviewing**, identify the task context:
1. Ask user: "What is the task context for this review?" (Jira issue, plan file, feature description, etc.)
2. If user provides context, extract the specific files/functions involved
3. Limit review scope to those files and their direct dependencies
4. Do NOT review unrelated code, even if in same changed files

**Task Context Prompt Template**:
```
Task Context: <jira-issue/plan-file/feature-description>
Scope: <list of files/functions directly related>
Exclude from review: <files/sections unrelated to task>
```

## Graceful Degradation (No Stalling)

**CRITICAL**: The review process MUST NEVER stall or wait indefinitely:

| Failure Scenario | Immediate Action |
|------------------|------------------|
| subagent timeout (>30s) | Skip that subagent, continue with others |
| subagent error/exception | Log error, skip subagent, continue |
| subagent returns empty | Proceed with other reviewers |
| ALL subagents fail | Main agent performs full review |
| Partial subagent response | Use what's available, main agent supplements |

**Timeout Behavior**:
- Each subagent call has a 30-second timeout
- On timeout: Continue with available results
- Never retry failed subagents during same review

**Error Handling**:
- Subagent errors are logged in report: `Execution: Single reviewer (reviewer-2 timed out after 30s)`
- User is informed of degradation: "Review completed with N reviewers" where N may be 0, 1, or 2
- Quality is maintained by fallback reviewers, not by retrying

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

## Review Execution Flow (For Main Agent)

When invoking the code-review-expert skill, follow this exact execution flow:

### Step 0: Identify Task Context (REQUIRED)

**ALWAYS ask the user for task context before reviewing**:

Ask the user:
```
What is the task context for this review?
Options:
1. Add Jira issue number (e.g., PROJ-123)
2. Provide path to task plan file
3. Describe the feature/bug being addressed
4. Specify files to review manually
```

Once context is provided:
1. Extract the specific scope (files, functions, modules)
2. Identify which changed files are directly related vs tangential
3. Create a review scope document

**If user cannot provide context**: Ask if they want a full review of all changes, then proceed.

### Step 1: Try to Invoke Subagents (Parallel with Timeout)

Attempt to invoke BOTH subagents in parallel with explicit 30-second timeouts:

```
task(subagent_type="code-reviewer-1", timeout=30000, ...) 
task(subagent_type="code-reviewer-2", timeout=30000, ...)
```

**Include task context in each subagent prompt**:
- Pass the task scope (files, context)
- Instruct subagent to focus ONLY on task-related code

**If a subagent times out or errors**:
- Log the failure with reason
- DO NOT retry
- DO NOT wait
- Continue with available reviewers

### Step 2: Determine Available Reviewers (Non-Blocking)

Immediately after timeout/error, determine available reviewers:

| Scenario | Action | Log Message |
|----------|--------|-------------|
| **Both succeed** | Proceed with dual-reviewer workflow | "Dual reviewer execution" |
| **reviewer-1 succeeds, reviewer-2 fails** | Continue with reviewer-1 only | "Single reviewer (reviewer-2: <error reason>)" |
| **reviewer-2 succeeds, reviewer-1 fails** | Continue with reviewer-2 only | "Single reviewer (reviewer-1: <error reason>)" |
| **Both fail/timeout** | Main agent performs review | "All subagents unavailable (<reasons>)" |

**Never block**: If any reviewer returns data, process it immediately.

### Step 3: Process and Merge Reviewer Output

If reviewers succeed (any count):
1. Collect findings from all successful reviewers
2. Merge findings, deduplicating by (file, line, severity, issue_title)
3. Filter findings to task scope only (discard unrelated issues)
4. Group by file, prioritize P0 > P1 > P2 > P3

If all reviewers fail:
1. Load the code-review-expert skill checklists yourself
2. Perform the review against all checklists
3. Focus review on task-scoped files only
4. Generate findings in the same JSON format

### Step 4: Ask User Before Writing Report (REQUIRED)

**BEFORE writing CODE_REVIEW.md, ask the user**:

```
Review completed. Found:
- P0: X critical issues
- P1: Y high priority issues  
- P2: Z medium priority issues
- P3: W low priority issues

Write the review report to CODE_REVIEW.md? (yes/no)
```

**If user says "yes"**: Write CODE_REVIEW.md
**If user says "no"**: Present findings inline, do NOT create file

### Step 5: Write Report (After User Approval)

In CODE_REVIEW.md, include:

**Review Execution Note** (add after Review Scope line):
```markdown
**Task Context**: <jira-issue/plan-file/description>
**Execution**: <dual/single/fallback> - <details>
**Reviewers**: code-reviewer-1, code-reviewer-2
**Scope**: Focused on task-related code only
```

### Key Principles

| Principle | Behavior |
|-----------|----------|
| **Never stall** | Proceed with available results, never wait or retry |
| **Never block** | If subagent fails, use fallback immediately |
| **Task-scoped** | Review only code directly related to the task |
| **User approval** | Always ask before writing the review document |
| **Transparency** | Document execution mode and any failures |
| **Quality maintains** | Same checklists regardless of who performs the review |

## CODE_REVIEW.md Output Format

```markdown
# Code Review Report

**Review Scope**: `<git-diff-scope>`
**Task Context**: `<jira-issue OR plan-file OR feature-description>`
**Task Scope**: `<files/functions directly related to task>`
**Excluded**: `<files/sections excluded from this review>`
**Iteration**: `N` of `3`
**Execution**: `<execution-mode>` - `<details>`
**Reviewers**: code-reviewer-1, code-reviewer-2
*Note: Models are configured in agents/code-reviewer-*.md; fallback to session model may occur automatically if primary is unavailable.*

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

[Repeat for all issues]

## Execution Details

| Reviewer | Status | Notes |
|----------|--------|-------|
| code-reviewer-1 | success/timeout/error | Details if failed |
| code-reviewer-2 | success/timeout/error | Details if failed |

## Iteration History

| Iteration | P0 | P1 | P2 | P3 | Fixed |
|-----------|----|----|----|----|-------|
| 1 | X | Y | Z | W | - |
| 2 | X' | Y' | Z' | W' | Z+Y-X'-Y' |
```
