---
name: grill-with-docs
description: Resolve unclear product or technical decisions through a focused interview and record accepted domain terms and durable decisions. Use before a specification when important behavior is still unclear.
disable-model-invocation: true
---

# Grill With Docs

Use this skill when discussion, not code, is the current bottleneck. This is a
human-in-the-loop skill.

## Method

1. State the decision that must become clear.
2. Read current code, documentation, glossary, ADRs, and ticket context.
3. Ask one question at a time.
4. Prefer concrete scenarios over abstract questions.
5. Challenge contradictions with observed behavior.
6. Record accepted terms in the glossary immediately when appropriate.
7. Offer an ADR only for a durable architectural trade-off.
8. Stop when the behavior and constraints are clear enough for a specification
   or implementation plan.

Do not interview yourself. Do not invent user answers. Do not implement code.

## Result

Return a concise decision summary containing:

- Problem and desired outcome
- Accepted behavior
- Rejected or out-of-scope behavior
- Domain terms
- Technical constraints
- Open decisions
- Recommended next artifact
