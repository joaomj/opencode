---
name: code-review
description: Review a requested code change for P0 and P1 correctness, security, and regression risks. Use ONLY when the user explicitly asks for a code review.
license: MIT
---

# Code Review

Use this skill only when the user explicitly requests a review. Do not run it as an automatic PR gate.

## Review Scope

- Inspect the requested diff and the relevant current code.
- Report only P0 and P1 findings.
- Group findings by file.
- Omit line numbers.
- Use neutral language. Do not write imperatives.
- Explain the current behavior, the impact, and one recommendation that addresses the risk.
- Skip cosmetic, speculative, and non-critical suggestions.

## Evidence

Check deployed or remote behavior first when available, then local code, updated documentation, and Jira tickets. Report conflicts between evidence sources.

## Verification

- Reproduce confirmed bugs at the highest useful black-box seam.
- Do not use internal mocks for user-visible behavior.
- Do not create low-signal tests only to increase coverage.
- A clean review states that no P0 or P1 findings were found and records any verification gap.
