---
name: coding-best-practices
description: Route implementation work to focused coding, error, Python, and testing standards. Use for coding activity when the applicable standards are not yet loaded.
license: MIT
---

# Coding Best Practices

This skill is a small compatibility router. It does not impose a universal
Spec-Driven Development gate or universal TDD.

Load the focused skill that matches the work:

- `coding-standards` for correctness, configuration, security, idempotency, and
  concurrency.
- `error-handling` for exceptions, retries, partial work, and recovery.
- `python-tooling` for Python commands, dependencies, type checks, and OC014.
- `testing-best-practices` for test design, regression tests, and test review.
- `workflow` for route selection and preparation level.
- `code-review` for the explicit review phase.

## Default rule

Use risk-based preparation:

- Small, clear, reversible changes can proceed directly.
- Unclear behavior needs discovery or a specification.
- Complex implementation needs an implementation plan.
- Large, high-risk, or hard-to-reverse work needs both a specification and a
  plan before code edits.

## Universal quality rules

- Read the current code before making claims.
- Prefer composition and established patterns.
- Keep interfaces small and behavior observable.
- Surface every failure.
- Test at the highest useful seam.
- Do not add tests only to increase coverage.
- Do not create large infrastructure without approval.
