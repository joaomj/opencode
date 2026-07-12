---
name: code-review
description: Review changes since a fixed point along two axes — Standards (coding standards compliance) and Spec (correctness against requirements). Runs both reviews in parallel sub-agents.
---

Two-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating spec or ticket?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

## Process

### 1. Pin the fixed point

Whatever the user says is the fixed point — a commit SHA, branch name, tag, `main`, etc. Capture `git diff <fixed-point>...HEAD`.

### 2. Identify the spec source

Look for the originating spec: issue references in commit messages, a path the user passed, or a spec file under `docs/` or `specs/`.

### 3. Identify standards sources

Anything in the repo that documents how code should be written (`CODING_STANDARDS.md`, `CONTRIBUTING.md`).

### 4. Smell baseline

On top of whatever the repo documents, the Standards axis always carries these Fowler code smells (*Refactoring*, ch.3):

- **Mysterious Name** — rename to reveal purpose
- **Duplicated Code** — extract shared shape
- **Feature Envy** — move method onto the data it envies
- **Data Clumps** — bundle into one type
- **Primitive Obsession** — create a domain type
- **Repeated Switches** — polymorphism or shared map
- **Shotgun Surgery** — gather scattered changes into one module
- **Divergent Change** — split for single-responsibility
- **Speculative Generality** — delete unused abstraction
- **Message Chains** — hide walk behind one method
- **Middle Man** — call the real target directly
- **Refused Bequest** — use composition over inheritance

Two rules: the repo's documented standards always override the baseline; each smell is a labelled heuristic, never a hard violation.

### 5. Spawn both sub-agents in parallel

**Standards sub-agent**: include the diff, standards-source files, and the full smell baseline. Report violations per file/hunk, distinguish hard violations from judgement calls.

**Spec sub-agent**: include the diff and the spec. Report missing requirements, scope creep, and wrong implementations.

### 6. Aggregate

Present two reports under `## Standards` and `## Spec` headings. Do NOT merge or rerank findings. End with one-line summary: total findings per axis and the worst issue within each.

## Why two axes

A change can pass one and fail the other:
- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail**
- Code that does exactly what was asked but breaks conventions → **Spec pass, Standards fail**

Reporting separately stops one axis from masking the other.
