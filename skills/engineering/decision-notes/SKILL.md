---
name: decision-notes
description: Record material product, process, architecture, or cross-cutting decisions with their reasons and alternatives. Use when a decision needs durable context.
---

# Decision Notes

Use this skill when a decision changes user expectations, shared rules, public
behavior, security or privacy boundaries, working processes, or another area a
maintainer may reasonably revisit.

Do not create a note for a routine implementation choice, a small reversible
change, or a fact discovered during investigation. Do not duplicate a decision
already owned by a ticket, specification, implementation plan, or ADR. Link to
the owning document instead.

## Materiality test

Create or update a note when at least one condition applies:

- The decision changes product behavior or user expectations.
- The decision changes a rule shared by agents or repositories.
- The decision changes a public interface, security boundary, privacy rule, or
  durable configuration format.
- The decision has meaningful alternatives and may be questioned later.
- The decision gives up an important capability or creates a lasting restriction.

## Location and lifecycle

Store notes in the target repository:

```text
.agents/decisions/
  proposed/
  accepted/
  rejected/
  archived/
```

Use `YYYY-MM-DD-<short-title>.md` for the filename. The folder and `Status:`
value must match:

- `proposed`: a material recommendation that still needs approval.
- `accepted`: a material decision approved by the responsible person.
- `rejected`: a material recommendation that was considered and declined.
- `archived`: an old note kept for history and no longer used as current policy.

Check active notes before creating a new note. If a note covers the same
decision, update it or create a linked superseding note. Do not create a central
index.

## Approval

Agents may recommend a material decision. They must not mark it `accepted`
without user or team approval. Record who approved it and what approval means.
Small, clear, reversible delivery choices may proceed after the product outcome
is approved.

## Record format

Use this format for a proposed or rejected note:

```markdown
# Decision: <title>

Status: proposed
Owner: agent | user | team

## Problem

What problem requires a choice?

## Recommendation

What option is recommended?

## Why

Why is this option suitable?

## Alternatives

What credible options were considered, and why did each lose?

## Product impact

What changes for users, maintainers, or other agents?

## Risks

What risks and accepted costs remain?

## Approval

What approval is needed or what decision was made?
```

For an accepted note, replace `## Recommendation` with `## Decision` and record
the approval. For an archived note, preserve the accepted or rejected decision
and mark the note as historical.

Keep the note factual. Record the reason for the choice, the alternatives that
lost, the product impact, and the conditions that could justify a later change.
