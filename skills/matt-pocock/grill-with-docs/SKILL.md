---
name: grill-with-docs
description: Interview-driven design alignment that sharpens domain language and records decisions into CONTEXT.md glossary and ADRs. Invoke at the start of a change when the plan is fuzzy.
metadata:
  credit: Matt Pocock (https://github.com/mattpocock/skills)
---

# grill-with-docs

Run `/grill-with-docs` to start a relentless one-question-at-a-time interview that stress-tests a plan or design, resolving domain terms into a `CONTEXT.md` glossary and hard decisions into ADRs under `docs/adr/`.

## Workflow position

First step of the build chain:

```
grill-with-docs → to-spec → to-tickets → implement → code-review
```

## What it produces

- **CONTEXT.md** — glossary of resolved canonical terms (vocabulary only, no implementation details)
- **docs/adr/NNNN-title.md** — ADRs for genuinely hard-to-reverse decisions with real trade-offs

## Rules

- Asks **one question at a time** and waits — never dumps a questionnaire
  - Asking multiple questions at once is bewildering and prevents the user from giving full, considered answers to each
- Reads the codebase to answer questions it can resolve without the user
- Writes terms to CONTEXT.md the moment they resolve, not batched at the end
- ADRs are rare — only for surprising, hard-to-reverse decisions

## Distinguish Facts from Decisions

The model explores the codebase to find **Facts** (code patterns, existing implementations) and asks the user for **Decisions** (architecture choices, feature scope). It does NOT answer its own questions or grill itself — if it can find the answer by reading code, it does so. If it needs human input, it asks the user one question at a time.

## Confirmation Gate

Before moving to implementation, ask: "Do you confirm we've reached a shared understanding?" Do NOT enact the plan or start implementing until the user explicitly confirms.

## Prerequisites

Must be run inside a repo where writing CONTEXT.md and docs/adr/ is safe.
