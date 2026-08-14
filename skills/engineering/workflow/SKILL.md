---
name: workflow
description: Classify the user's intent and select the smallest workflow that delivers the requested result. Use for every substantial user request before execution.
---

# Workflow Router

This is the top-level workflow router. It classifies the meaning of the full
request, selects one workflow, and reports that selection before substantial
work. It is not a keyword matcher.

## Intent Envelope

Read the complete request and current conversation. Determine:

- The result the user expects to receive
- The action the user wants performed
- The maximum side effects the user appears to allow
- The point where the work should stop
- Whether the request concerns understanding, a decision, a change, recovery,
  review, or a remote delivery action

Use the request's meaning, context, and expected result. Words such as
"explore", "plan", or "research" are evidence, not routing rules. A request
can select a workflow without using its name.

## Routing Procedure

1. Read the full request and relevant previous decisions.
2. Identify any explicit workflow, deliverable, or side-effect request.
3. Classify the intended result, not only the subject matter.
4. Select the smallest workflow that can produce that result.
5. Use risk, uncertainty, reversibility, impact, scope, and available evidence
   to choose the depth inside the selected workflow.
6. If two workflows would produce materially different deliverables or side
   effects, ask one focused question before acting.
7. Otherwise, choose the best-supported workflow and state the assumption.
8. Load the selected workflow and follow its ordered steps.

Risk selects preparation and verification depth. Risk does not turn an idea,
question, or exploration request into an implementation plan.

## Required Opening

Before substantial work, write:

```text
Goal: <the user-visible result>
Plan: <the work stages and why this path is suitable>
Decision needed: <what the user must decide, or "none">
```

Do not lead with internal workflow names, implementation details, or side-effect
lists. State those details only when they affect a user decision or risk.

## Progress Reporting

Before substantial work, write:

```text
Goal: <the user-visible result>
Plan: <work stages and why this path is suitable>
Decision needed: <what the user must decide, or "none">
```

After each stage, write:

```text
Result: <what was learned or completed and what it means for the product>
Next: <the next stage and why it is needed>
```

Do not start the next stage before you report the previous result. Group
related reads or searches into one stage. Send an additional update before a
large batch of searches, edits, or checks, and when the approach, scope, or risk
changes.

## Workflow Registry

| Intended result | Workflow | Default boundary |
|---|---|---|
| Find and prioritize improvements or feature opportunities in an existing project | `project-opportunities` | Read-only opportunity map |
| Develop an idea or compare options | `focused-exploration` | Conversation only |
| Explain the current repository or behavior | `codebase-investigation` | Read-only findings |
| Establish external or unfamiliar facts | `research` | Findings and sources |
| Change code, configuration, or infrastructure | `software-delivery` | Approved implementation scope |
| Resolve broken, slow, or incorrect behavior | `bug-resolution` | Fix and verification |
| Produce repository-specific implementation steps | `implementation-planning` | Approved plan only; branch and file require separate approval |
| Select and record a durable architecture choice | `architecture-decision` | Decision record only when justified |
| Evaluate a code change | `code-review` | Review findings only |
| Publish a pull request | `create-pull-request` | Remote PR action with confirmation |
| Record a medium/high complexity bug | `write-postmortem` | Postmortem record only |
| Maintain technical documentation | `doc-maintenance` or `technical-writing` | Requested documentation scope |

Existing capability skills such as `research`, `domain-modeling`,
`codebase-design`, `prototype`, `coding-standards`, `error-handling`, and
`testing-best-practices` are invoked by workflows. They do not replace the
top-level routing decision.

## Handoffs

A workflow may invoke a capability skill or hand off to another workflow when
the user request permits that result. A handoff must state the new workflow and
why it is needed.

Do not escalate automatically from exploration, investigation, or research to
specification, planning, implementation, review, or PR creation. Return the
current deliverable and let the user request or approve the next workflow.

Do not create a ticket, specification, ADR, plan, branch, code, test, commit, or
PR unless the selected workflow and the user's request permit it.

## Completion

Stop when the selected workflow's deliverable and completion condition are met.
Do not continue into a plausible next workflow only because more work is
possible.
