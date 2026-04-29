---
description: Create implementation plan using Goal-Driven Development (GDD) with TDD as guardrail
---

# Goal-Driven Development (GDD) Planning

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Think Before Coding** | State assumptions explicitly. Present multiple interpretations. Push back when simpler approach exists. Stop when confused — ask rather than guess. |
| **Simplicity First** | Minimum code that solves the problem. No speculative abstractions. No "flexibility" not requested. If 200 lines could be 50, rewrite. |
| **Surgical Changes** | Touch only what you must. Clean up only your own mess. Every changed line should trace directly to the user's request. |
| **Goal-Driven Execution** | Define success criteria. Loop until verified. Transform "add validation" into "write tests for invalid inputs, then make them pass." |

## Non-Negotiable Rules

| Rule | Violation = STOP |
|------|------------------|
| think-first | Block if assumptions are being made silently instead of stated |
| simplicity-check | Block if proposed code is overengineered for the task |
| surgical-check | Block if changes touch code orthogonal to the request |
| tdd-guardrail | Block if no failing test exists to define success before implementation |
| no-hardcoding | Block if hardcoded values found (URLs, timeouts, thresholds, file paths, magic numbers) |

---

## Workflow

### Phase 1: Think & Clarify

**Goal:** Surface assumptions and ambiguity before doing anything wrong.

1. **State assumptions** — What are you assuming about the task? Say them out loud.
2. **Identify ambiguity** — If anything is unclear, ask. Don't guess.
3. **Present alternatives** — If multiple interpretations exist, present them briefly.
4. **Push back if warranted** — If a simpler approach exists, say so.

**Gate:** If ambiguity exists, STOP and ask. If clear, proceed.

---

### Phase 2: Success Criteria (TDD Guardrail)

**Goal:** Define what "done" looks like before writing code.

For EVERY task, write a failing test that defines success:

| Task | Transform to |
|------|--------------|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |
| "Implement feature" | "Write tests for expected behavior, then implement" |

**Gate:** Block if no failing test exists before implementation begins.

---

### Phase 3: Brief Plan

**Goal:** Show what will be done, in what order, with success checks.

```
## Plan: [Feature Name]

**Summary:** One sentence describing the goal.

**Approach:** [If tradeoffs existed, brief rationale here]

**Todos:**
1. [Step 1] → verify: [how to check step 1 is done]
2. [Step 2] → verify: [how to check step 2 is done]
3. [Step 3] → verify: [how to check step 3 is done]
```

**Approval Gate:**
- **If tradeoffs exist**: Present options, wait for explicit "yes"
- **If no tradeoffs**: Show brief plan, proceed unless user says "wait"

---

### Phase 4: Temporary Plan File

Before executing, ask the user:

> "Would you like me to write a temporary `PLAN.md` file to the workspace root for reference during execution?"

If yes, write the plan to `PLAN.md` at the workspace root. Delete it after completion if requested.

---

### Phase 5: Execute with Verification

**Goal:** Loop until all success criteria are met.

For each todo step:
1. Execute the step
2. Verify: does the success check pass?
3. If no, diagnose and fix, then re-verify

**Gate:** All tests must pass. Lint must pass. No regressions.

---

### Phase 6: Completion

After all todos complete:
1. Run full test suite
2. Run lint/type checks
3. Verify no regressions
4. Commit (ask user)
5. Ask: "Update documentation?"

---

## Progressive Disclosure

| User says... | Agent shows... |
|--------------|----------------|
| (default) | Brief plan: summary + todos + success criteria |
| "expand" / "show full plan" | Full internal plan: assumptions, alternatives, detailed steps, test code |
| "simplify" | Aggressive simplification review |
| "just do it" | Execute immediately with minimal planning, still use TDD guardrail |

---

## TDD as Guardrail

TDD is not the primary methodology — it's a guardrail against agent non-determinism:

| Benefit | How GDD Uses It |
|---------|----------------|
| Forces explicit success criteria | Test must exist before implementation |
| Prevents "run along" behavior | Test failure = stop and fix |
| Provides verification loop | Tests pass = goal met |
| Catches regressions early | Full suite must pass |
