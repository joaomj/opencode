---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered:

- **"Does this logic / state model feel right?"** → Build a tiny interactive terminal app that pushes the state machine through cases hard to reason about on paper.
- **"What should this look like?"** → Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

The two branches produce very different artifacts — getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code and state the assumption.

## Rules

1. **Throwaway from day one.** Name it so a casual reader sees it's a prototype, not production.
2. **One command to run.** Whatever the project's task runner supports.
3. **No persistence by default.** State lives in memory. If the question explicitly involves a database, hit a scratch DB with a clear "PROTOTYPE — wipe me" name.
4. **Skip the polish.** No tests, no error handling beyond what makes it runnable, no abstractions.
5. **Surface the state.** After every action or variant switch, render the full relevant state so the user can see what changed.
6. **Capture it when done.** Fold validated decisions into the real code, capture the prototype as a primary source on a throwaway branch, and leave a context pointer on the implementation issue.
