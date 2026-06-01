---
name: research
description: Research procedure: websearch → context7 → synthesize. Use when encountering unfamiliar libraries, APIs, frameworks, or conventions. NEVER answer from memory — always search first.
license: MIT
---

# Research

Read-only research procedure. No file edits, no bash commands. Only searches and reports.

## Rule

**OC015**: Never guess code formats, naming conventions, or library APIs. When uncertain, search the web or load `context7-docs` for up-to-date documentation before answering.

## Workflow

### Step 1: Web Search

Use `websearch` to find official documentation, recent examples, and best practices.

### Step 2: Context7 (for libraries)

If the topic is a specific library, load the `context7-docs` skill for structured API documentation.

### Step 3: Synthesize

Return a concise summary with:
- Correct API signatures and parameters
- Usage examples (copy-paste ready)
- Version compatibility notes
- Links to official docs

## Constraints

- NEVER write code from memory or training data
- NEVER edit files
- NEVER run bash commands
- If search yields conflicting info, report the conflict and recommend the official source
