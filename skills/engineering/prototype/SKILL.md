---
name: prototype
description: Build a small throwaway artifact to answer a design, behavior, interface, or feasibility question. Use when prose or code inspection cannot provide enough evidence.
---

# Prototype

Use a prototype to answer one decision question. A prototype is evidence, not
production code and not a test suite.

## Method

1. State the question and the result that would change the decision.
2. Choose the smallest runnable artifact that can produce that result.
3. Use the same user-facing interface when practical: browser, shell, HTTP, or
   real dependency.
4. Surface errors and limitations. Never turn a failed experiment into success.
5. Run the prototype against representative inputs.
6. Record the observation, interpretation, and decision.
7. Delete the artifact or move it to a clearly marked research location.

Do not build deployment infrastructure, a large test harness, or a production
abstraction for a prototype without approval.

## Result

Return:

- Question
- Prototype scope
- Observed result
- Decision supported by the result
- Limitations
- Cleanup status
