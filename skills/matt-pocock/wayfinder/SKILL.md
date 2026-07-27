---
name: wayfinder
description: Plan a huge chunk of work — more than one agent session can hold — as a shared map of investigation tickets on your issue tracker, and resolve them one at a time until the way to the destination is clear.
metadata:
  credit: Matt Pocock (https://github.com/mattpocock/skills)
---

A loose idea has arrived — too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** on the repo's issue tracker, then works its tickets one at a time until the route is clear.

## Plan, don't do

Wayfinder is **planning** by default: each ticket resolves a decision, and the map is done when the way is clear — nothing left to decide before someone goes and does the thing. Produce decisions, not deliverables.

## Ticket Types

- **Research** (AFK): Reading docs, APIs, or resources. Creates a markdown summary.
- **Prototype** (HITL): Raise the fidelity of the discussion via the `/prototype` skill.
- **Grilling** (HITL): Conversation via `/grill-with-docs`, one question at a time.
- **Task** (HITL or AFK): Config, provisioning, or other work that unblocks a decision.

## Fog of war

Beyond the live tickets lies the **fog of war** — decisions you can tell are coming but can't yet pin down. Resolving a ticket clears the fog ahead, graduating specifiable questions into fresh tickets. The map's **Not yet specified** section captures this dim view.

## Process

### Chart the map

1. **Name the destination.** Run a grilling session to pin down what this map is finding its way to.
2. **Map the frontier.** Grill breadth-first across the whole space.
3. **Create the map issue** with Destination, Notes, Decisions-so-far, Not yet specified, Out of scope.
4. **Create tickets** you can specify now as child issues, wire blocking edges in a second pass.
5. Stop — charting is one session's work; do not also resolve tickets.

### Work through the map

1. Load the map and choose a ticket from the **frontier** (open, unblocked, unclaimed).
2. **Claim it** — assign it to yourself before any work.
3. Resolve it using the appropriate skill for its type.
4. Record the answer, close the issue, append to Decisions-so-far on the map.
5. Add newly-surfaced tickets and graduate fog from Not yet specified.

Never resolve more than one ticket per session.
