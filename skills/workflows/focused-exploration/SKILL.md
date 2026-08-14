---
name: focused-exploration
description: Explore an idea, option space, or design question and deliver useful clarity without starting implementation or creating durable delivery artifacts.
---

# Focused Exploration

Use this workflow when the user wants to develop an idea, compare possible
directions, challenge assumptions, or understand a decision space. Infer this
from the expected result and conversation context. Do not require a literal
keyword.

## Exclude

Use another workflow when the user asks for current-system facts, external
evidence, a feasibility experiment, an architecture record, a repository plan,
code changes, a bug fix, a review, or a pull request.

## Ordered Steps

1. State the user-visible goal, deliverable, work stages, reason for the chosen
   path, and any decision the user must make.
2. Restate the idea or decision in precise terms.
3. Identify the decision that the exploration should improve.
4. Inspect only the code, documentation, or external facts needed to avoid
   unsupported claims.
5. Produce two to four credible options, or explain why fewer options exist.
6. Compare benefits, costs, risks, assumptions, and reversibility.
7. Give a recommendation only when the evidence supports one. Mark uncertainty.
8. Ask one useful question or state the next decision frontier.
9. Stop.

## Allowed Skills

Invoke `domain-modeling` for ambiguous terms, `codebase-design` for current
interfaces and seams, `research` for external facts, or `prototype` when a
small experiment is the cheapest way to answer one feasibility question.

These skills support the exploration. They do not authorize implementation or
change the deliverable without an explicit handoff.

## Deliverable

Return a concise option map, trade-off analysis, assumptions, recommendation
when justified, and one useful question. The default output is conversation.

## Side Effects

Do not create or modify tickets, specifications, ADRs, plans, branches, source
files, tests, commits, or pull requests. Temporary prototype artifacts require
explicit permission and must be disposable and cleaned up.

## Handoff

Offer, but do not start, a next workflow such as research, prototype,
architecture-decision, specification, or implementation-planning.
