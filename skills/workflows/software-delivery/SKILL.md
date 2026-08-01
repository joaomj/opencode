---
name: software-delivery
description: Orchestrate an approved feature, refactor, configuration, or infrastructure change from intent through verification and optional review or pull request.
---

# Software Delivery

Use this workflow when the user wants a repository change delivered. The
request may be a direct change, a ticket, an approved specification, or an
approved plan. The workflow chooses preparation depth from uncertainty, risk,
reversibility, impact, scope, and evidence.

## Ordered Steps

1. State the selected workflow, intended deliverable, and allowed side effects.
2. Read the request, acceptance criteria, current code, relevant glossary,
   ADRs, `tech-context.md`, and available remote behavior.
3. Classify the route:
   - Direct: behavior and implementation are clear, local, and reversible.
   - Planned: behavior is clear but implementation is complex.
   - Discovery: behavior, terms, feasibility, or architecture is unresolved.
4. For Discovery, invoke only the needed `focused-exploration`, `research`,
   `domain-modeling`, `grill-with-docs`, or `prototype` workflow or skill.
5. Create or update a specification only when accepted behavior needs a durable
   contract. Obtain approval before treating it as the delivery contract.
6. For complex work, invoke `implementation-planning`. Obtain approval before
   editing code.
7. Invoke `implement` for the approved scope.
8. Load `coding-standards`, `error-handling`, `python-tooling`, and
   `testing-best-practices` when applicable.
9. Verify acceptance criteria at the highest useful seam and report every
   failure or verification gap.
10. Invoke `code-review` when review is requested or required by the delivery
    path. Invoke `create-pull-request` only when the user requests a PR.

## Approval Boundaries

- Small, clear, reversible work may proceed directly.
- Substantial feature and architecture work needs user approval before edits.
- A specification and implementation plan need approval before delivery when
  they define the behavior or implementation contract.
- Do not commit or create a PR unless the user explicitly requests it.

## Deliverable

Return the requested change, verification evidence, and remaining gaps. If the
workflow stops before implementation, return the discovery result or approved
plan and state the next handoff.

## Side Effects

Only perform side effects allowed by the user's request and the selected route.
Do not infer permission for a branch, persistent document, commit, or PR from a
general request to discuss a feature.
