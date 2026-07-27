---
name: diagnosing-bugs
description: Diagnosis loop for hard bugs and performance regressions. Use when the user says "diagnose"/"debug this", or reports something broken/throwing/failing/slow.
metadata:
  credit: Matt Pocock (https://github.com/mattpocock/skills)
---

# Diagnosing Bugs

A discipline for hard bugs. Skip phases only when explicitly justified.

When exploring the codebase, read `CONTEXT.md` (if it exists) to get a clear mental model of the relevant modules, and check ADRs in the area you're touching.

## Phase 1 — Build a feedback loop

**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug — one that goes red on *this* bug — you will find the cause. If you don't have one, no amount of staring at code will save you.

Spend disproportionate effort here. Be aggressive. Be creative. Refuse to give up.

### Ways to construct one — try in this order

1. **Failing test** at whatever seam reaches the bug
2. **Curl / HTTP script** against a running dev server
3. **CLI invocation** with a fixture input, diffing stdout against known-good
4. **Headless browser script** (Playwright / Puppeteer)
5. **Replay a captured trace** — save a real request/payload to disk
6. **Throwaway harness** — minimal subset exercising the bug path
7. **Property / fuzz loop** — 1000 random inputs
8. **Bisection harness** — automate boot at state X, check, repeat
9. **Differential loop** — old vs new, diff outputs
10. **HITL bash script** — last resort

### Tighten the loop

Treat the loop as a product. Once you have *a* loop, tighten it:
- Make it faster (cache setup, skip unrelated init)
- Sharper signal (assert on specific symptom)
- More deterministic (pin time, seed RNG)

### Non-deterministic bugs

Goal is not a clean repro but a **higher reproduction rate**. Loop 100x, parallelise, add stress. A 50% flake is debuggable; 1% is not.

### Completion criterion

Phase 1 is done when you have a command that is **red-capable** (drives the actual bug path), **deterministic**, **fast**, and **agent-runnable**.

## Phase 2 — Reproduce + minimise

Run the loop, confirm the failure matches the user's symptom, then minimise the repro to the smallest scenario that still goes red.

## Phase 3 — Hypothesise

Generate **3-5 ranked hypotheses** before testing any. Each must be falsifiable with a prediction. Show the ranked list to the user before testing.

## Phase 4 — Instrument

Change one variable at a time. Prefer debugger/REPL over logs. Tag debug logs with a unique prefix for cleanup.

## Phase 5 — Fix + regression test

Write the regression test **before the fix**, at the correct seam. If no correct seam exists, that itself is the finding — the codebase prevents the bug from being locked down.

## Phase 6 — Cleanup + post-mortem

- Original repro no longer reproduces
- Regression test passes
- All debug instrumentation removed
- Record what would have prevented this bug
