---
name: domain-modeling
description: Define and sharpen business terms, entities, states, relationships, and invariants. Use when domain language is ambiguous, overloaded, or inconsistent with code.
---

# Domain Modeling

Domain modeling answers: "What concepts exist, and what do their names mean?"
It does not design classes or choose implementation details.
When discussion is the bottleneck, use `grill-with-docs` to ask the questions
and use this skill to record the accepted vocabulary.

## Method

1. Read the existing glossary or `CONTEXT.md` when present.
2. Identify overloaded, vague, or conflicting terms.
3. Propose precise canonical terms.
4. Test terms with concrete user and edge-case scenarios.
5. Compare the stated model with current code and observed behavior.
6. Record only terms and relationships that the user accepts.

Ask one focused question at a time when an answer changes the model. Do not
answer the question for the user.

## Glossary rules

`CONTEXT.md` is a glossary and current domain context. Keep implementation
details out of it. Record:

- Term definition
- Important distinctions
- Relationships
- States and valid transitions
- Explicitly excluded meanings

Update the glossary when a term is resolved, if the target repository uses one.
Create the file lazily. Do not create a glossary for a trivial change.

## ADR boundary

Offer an ADR only when the decision is hard to reverse, surprising without its
context, and the result of a real trade-off. A term definition alone does not
need an ADR.

## Completion

Stop when the terms required for the next decision are precise enough. Return:

- Agreed vocabulary
- Scenarios that validate it
- Conflicts with current code or documentation
- Remaining questions
