---
name: workflow
description: Classify the user's intent and select the smallest workflow that delivers the requested result. Use for every substantial user request before execution.
---

# Workflow Router

Read the complete request and current conversation. Classify the intended
result, requested action, side-effect boundary, and stopping point. Select the
smallest workflow that can deliver that result.

| Intended result | Workflow |
|---|---|
| Safe one-command task or simple answer | `direct-assistance` |
| Explore an idea or unresolved option | `focused-exploration` |
| Explain current repository behavior | `codebase-investigation` |
| Find and rank project opportunities | `project-opportunities` |
| Produce repository-backed delivery steps | `implementation-planning` |
| Define substantial product behavior and requirements | `product-definition` |
| Deliver an approved feature, refactor, or configuration change | `software-delivery` |
| Diagnose and fix broken behavior | `bug-resolution` |
| Review a change for P0 and P1 risks | `code-review` |
| Establish external or unfamiliar facts | `research` |
| Audit the global agent setup | `improve-agent` |
| Create a pull request | `create-pull-request` |
| Record a qualifying incident or complex bug fix | `write-postmortem` |
| Record a hard-to-reverse architecture choice | `architecture-decision` |
| Maintain project documentation | `doc-maintenance` |

If two workflows would produce materially different results or side effects,
ask one focused question. Otherwise, call `select_workflow` with the selected
workflow, reason, deliverable, side-effect boundary, and plan path when
applicable. Follow the workflow instructions returned by the tool.
