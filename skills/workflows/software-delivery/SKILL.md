---
name: software-delivery
description: Orchestrate an approved feature, refactor, configuration, or infrastructure change from intent through verification and optional review or pull request. Use when approved work needs end-to-end delivery.
---

# Software Delivery

Use this workflow when the user wants a repository change delivered. The
request may be a direct change, a ticket, an approved specification, or an
approved plan. The workflow chooses preparation depth from uncertainty, risk,
reversibility, impact, scope, and evidence.

## Ordered Steps

1. State the product goal, intended deliverable, work stages, reason for the
   chosen path, and any user decision required.
2. Announce the investigation scope, then read the request, acceptance
   criteria, current code, relevant glossary, ADRs, `tech-context.md`, and
   available remote behavior.
3. Classify the route:
   - Direct: behavior and implementation are clear, local, and reversible.
   - Planned: behavior is clear but implementation is complex.
   - Discovery: behavior, terms, feasibility, or architecture is unresolved.
4. For Discovery, invoke only the needed `focused-exploration`, `research`,
    `domain-modeling`, `grill-with-docs`, or `prototype` workflow or skill.
   Invoke `decision-notes` when a material decision needs a durable record.
5. Create or update a specification only when accepted behavior needs a durable
   contract. Obtain approval before treating it as the delivery contract.
6. For complex work, invoke `implementation-planning`. Obtain approval before
   editing code.
7. Announce the exact files and behavior, then invoke `implement` for the
   approved scope.
8. Load `coding-standards`, `error-handling`, `python-tooling`, and
   `testing-best-practices` when applicable.
9. Announce verification, then verify acceptance criteria at the highest useful
   seam and report every failure or verification gap.
10. Invoke `code-review` when review is requested or required by the delivery
    path. Invoke `create-pull-request` only when the user requests a PR.

## Progress Contract

- Report progress after each work stage. Group related reads or searches into
  one stage, then report the result before you start the next stage.
- Report before a large batch of searches, edits, or checks, and when the
  approach, scope, or risk changes.
- Explain findings and outcomes in product terms. Use examples or analogies
  when useful.
- Surface every material decision with a recommendation, its reason, and its
  product impact. Ask for approval before substantial or hard-to-reverse changes.
- Do not state time estimates, duration estimates, delivery dates, deadlines, or
  ETAs.
- Report blockers, failures, and verification gaps immediately. Do not hide
  them inside a final summary.

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
