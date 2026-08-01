---
name: diagnosing-bugs
description: Diagnose hard bugs and performance regressions by building a tight black-box feedback loop, testing ranked hypotheses, and preserving a regression test. Use when behavior is broken, failing, incorrect, or slow.
---

# Diagnosing Bugs

Do not begin with a theory. Build a feedback loop that can show the user's
exact symptom first.

## Loop

Use this order:

1. Build a red-capable command or test at the highest useful seam.
2. Reproduce the reported symptom.
3. Minimize the reproduction without losing the failure.
4. Generate three to five ranked, falsifiable hypotheses.
5. Test one variable at a time.
6. Turn the minimized reproduction into one black-box regression test when a
   correct seam exists.
7. Apply the smallest fix.
8. Re-run the original and minimized scenarios.
9. Remove tagged diagnostic instrumentation and throwaway artifacts.

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
- Root cause
- Fix
- Regression test seam
- Verification evidence
- Any remaining verification gap
