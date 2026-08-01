---
name: workflow
description: Select a risk-based software delivery route for features, bugs, refactors, architecture work, and unclear requests. Use before non-trivial code changes.
---

# Workflow

Use this skill before non-trivial code changes. It selects the smallest process
that gives enough confidence for the risk.

## First inspect

Read the relevant repository structure and current behavior before making claims.
Use this evidence order:

1. Deployed or remote behavior
2. Local code
3. Updated documentation
4. Jira tickets

Treat Jira as context and intent. Report conflicts between evidence sources.

## Classify the work

Assess these factors:

- Behavior uncertainty: is the desired result clear?
- Implementation uncertainty: is an established code pattern clear?
- Reversibility: can the change be rolled back without data or contract loss?
- Impact: can the change affect security, money, data, or many users?
- Scope: can one focused session hold the work?
- Evidence: is the problem or desired behavior reproduced?

Choose one route.

### Direct route

Use when the behavior and implementation are clear, local, and reversible.

```text
inspect -> implement -> verify -> report
```

Do not create a specification or plan only to satisfy a process.

### Planned route

Use when the behavior is clear but the implementation is complex.

```text
ticket or request -> inspect -> implementation plan -> approval
-> implement -> verify -> review -> PR
```

Use `/implementation-plan`. The plan is repository-specific. It does not replace
the ticket.

### Discovery route

Use when product behavior, domain terms, feasibility, or architecture is unclear.

```text
problem -> research, grilling, domain modeling, or prototype
-> specification when needed -> ADRs when needed
-> implementation plan -> approval -> delivery
```

Load only the discovery skill that matches the uncertainty. Use
`specification` to record accepted behavior. Do not use a plan to hide
unresolved product decisions.

### Bug route

Use when the user reports incorrect, failing, slow, or broken behavior.

```text
report -> reproduce -> failing black-box regression test when possible
-> diagnose -> minimal fix -> verify -> review -> PR
```

Load `diagnosing-bugs` for hard bugs. Use selective TDD. Do not build a large
test harness before a tight feedback loop exists.

### Wayfinding route

Use `wayfinder` only when the work is too large or unclear for one focused plan.
Wayfinding produces a map of decisions. It does not start implementation.

## Artifact selection

Use the smallest artifact that preserves the decision:

| Question | Artifact |
|---|---|
| Why is this needed? | Jira ticket |
| What behavior is required? | Specification |
| How will this repository change? | `PLAN-<ticket-id>.md` |
| Why was a hard-to-reverse design selected? | ADR |
| How does the current system work? | `tech-context.md` |
| What was delivered and verified? | Pull request |

Do not duplicate content. Link artifacts instead.

## Approval gates

- Small, clear, reversible work can proceed directly.
- Substantial feature and architecture work needs user approval before code edits.
- A specification needs approval when it defines behavior or scope for substantial work.
- An implementation plan needs approval before implementation.
- An ADR needs approval when it records a hard-to-reverse choice.

## Required output

Before the next phase, state:

- Selected route
- Evidence and risk that led to the route
- Artifacts required
- Next action
- Any blocker or unresolved decision

Do not implement code while this skill is selecting a route.
