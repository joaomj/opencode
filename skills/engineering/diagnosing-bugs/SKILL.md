---
name: diagnosing-bugs
description: Diagnose hard bugs and performance regressions through reproduction and ranked hypotheses. Use ONLY when a bug-resolution workflow needs a diagnosis.
---

# Diagnosing Bugs

This skill owns reproduction, minimization, hypothesis testing, and root-cause
evidence. `bug-resolution` owns the fix, regression test, and final verification.
Do not apply a fix from this skill.

## Loop

Use this order:

1. Build a red-capable command or test at the highest useful seam.
2. Reproduce the reported symptom.
3. Minimize the reproduction without losing the failure.
4. Generate three to five ranked, falsifiable hypotheses.
5. Test one variable at a time.
6. Report the diagnosis and the remaining verification gap to the owning
   workflow.

Use a browser, HTTP client, CLI, shell script, or live system when that is the
highest useful seam. Use a property test only for complex pure logic.

## Feedback-loop requirement

Do not proceed to a hypothesis until one command has been run and can fail on
the exact user-visible symptom. If the environment blocks this, report what was
tried, the missing access or artifact, and the cheapest reliable alternative.

## Failure rules

- Preserve exact error messages and outputs.
- Use `rg`, not `grep`, for searches.
- Surface setup failures. Do not replace failures with empty data or success.
- Tag temporary logs with a unique prefix and remove them before completion.
- Do not build a large harness before testing whether a small loop works.

## Completion

Report:

- Reproduction command and result
- Minimized scenario
- Ranked hypotheses and tested predictions
- Root-cause evidence
- Suggested regression-test seam for `bug-resolution`
- Any remaining verification gap
