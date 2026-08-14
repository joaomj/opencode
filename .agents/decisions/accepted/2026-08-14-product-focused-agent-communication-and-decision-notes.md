# Decision: Product-focused agent communication and material decision notes

Status: accepted
Owner: user and agent

## Problem

The user needs agent work to stay focused on the product result, not coding
details. The user also needs clear progress updates and durable context for
material choices. The current rules cover some of this behavior but do not set
one complete standard or define a decision-note process.

## Decision

Use three layers:

- Always-on rules in `AGENTS.md` for product-focused communication, plain
  language, reasons for recommendations, progress updates, and no time
  estimates.
- The `decision-notes` skill for material decisions that need durable context.
- The linter for decision-note structure, lifecycle, filename, and approval
  checks.

Record material decisions only. Do not record routine or small reversible
choices. Use `.agents/decisions/{proposed,accepted,rejected,archived}/` in the
target repository. Do not use a hook to force progress messages or decide
whether a choice is material.

## Why

Always-on rules are suitable for behavior that must apply in every task. A skill
can describe the judgment needed to identify a material decision without adding
the same procedure to every rule. A linter can check structure reliably, but it
cannot judge product importance or send a useful update during a long command.

The materiality threshold keeps the record useful. A record for every small
choice would create noise and duplicate tickets, specifications, plans, and
architecture records.

## Alternatives

**Instructions only:** This would be simple, but it would not provide a shared
record format or automatic quality checks.

**Hook only:** A hook could inspect files, but it could not judge product impact
or provide a useful live progress update. It would also risk interrupting work.

**Record every decision:** This would provide more history, but the log would
become noisy and would repeat routine implementation details.

## Product impact

Users receive product-first openings, useful progress updates during substantial
work, plain language outside engineering material, and a reason for each
recommendation. Future agents can find the context for material choices without
searching conversation history.

## Risks

An agent may still miss a decision that should have a note because materiality
requires judgment. The linter reduces format errors but does not replace review.
The process adds a small documentation step for material work.

## Approval

Approved by the user in the session that introduced this change. The accepted
status authorizes these local configuration and documentation changes. It does
not authorize commits, branches, pull requests, or remote actions.
