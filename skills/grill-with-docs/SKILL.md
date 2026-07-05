---
name: grill-with-docs
description: Interview-driven design alignment that sharpens domain language and records decisions into CONTEXT.md glossary and ADRs. Invoke via /grill-with-docs at the start of a change when the plan is fuzzy.
license: MIT
---

# grill-with-docs

Run `/grill-with-docs` to start a relentless one-question-at-a-time interview that stress-tests a plan or design, resolving domain terms into a `CONTEXT.md` glossary and hard decisions into ADRs under `docs/adr/`.

## Workflow position

First step of the build chain:

```
grill-with-docs → to-prd → to-issues → implement/tdd → code-review
```

## What it produces

- **CONTEXT.md** — glossary of resolved canonical terms (vocabulary only, no implementation details)
- **docs/adr/NNNN-title.md** — ADRs for genuinely hard-to-reverse decisions with real trade-offs

## Rules

- Asks one question at a time and waits — never dumps a questionnaire
- Reads the codebase to answer questions it can resolve without the user
- Writes terms to CONTEXT.md the moment they resolve, not batched at the end
- ADRs are rare — only for surprising, hard-to-reverse decisions

## Prerequisites

Must be run inside a repo where writing CONTEXT.md and docs/adr/ is safe.
