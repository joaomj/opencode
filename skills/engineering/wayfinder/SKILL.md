---
name: wayfinder
description: Map decisions for work that is too large or unclear for one focused planning session. Use for multi-session efforts with unresolved dependencies or architectural choices.
disable-model-invocation: true
---

# Wayfinder

Wayfinding is for finding the route, not implementing the destination. Use it
only when a normal discovery session cannot produce a complete specification or
plan.

## Entry criteria

Use wayfinding when at least one applies:

- The effort spans multiple systems or sessions.
- Important decisions depend on earlier investigations.
- The destination is known but the route is not.
- The work contains several independent decision branches.

Do not use it for a normal feature with a clear plan.

## Map

Define:

- Destination: what completion means.
- Notes: domain, standing policies, and required skills.
- Decisions so far: links to resolved decisions.
- Not yet specified: in-scope questions that are not precise enough to ticket.
- Out of scope: work deliberately excluded.

Each decision ticket contains one question. A ticket is ready only when its
question is precise. Use dependency links or an explicit `Blocked by` section.

Use the configured issue tracker when one exists. Do not create tracker work
without user approval.

## Method

1. Define the destination.
2. Explore broadly enough to identify the first decision frontier.
3. Create only the decisions that are precise now.
4. Record unknown future work as fog, not speculative tickets.
5. Resolve one decision at a time unless independent research can run in
   parallel.
6. Record each resolution and update the map.
7. Stop when the remaining route is clear enough for a specification and plan.

Wayfinder does not implement features. It produces decisions and a clear handoff.
