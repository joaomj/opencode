---
name: implement
description: Implement a piece of work based on a spec or set of tickets.
metadata:
  credit: Matt Pocock (https://github.com/mattpocock/skills)
---

Implement the work described by the user in the spec or tickets.

For bug fixes, use `/tdd` at the pre-agreed seam. For common coding, use
e2e and blackbox tests against user-visible behavior.

Run typechecking regularly, single e2e test files regularly, and the full e2e suite once at the end.

Once done, use `/code-review` to review the work.

Commit your work to the current branch.
