---
name: architecture-diagram
description: Generate professional architecture diagrams as self-contained HTML/SVG or ASCII. Use for system, C4, infrastructure, cloud, security, and network diagrams.
license: MIT
---

# Architecture Diagram

Generate a diagram that explains the system and its relationships. Read
`references/output-contract.md` before producing HTML or ASCII output.

## Output

Ask for the format only when the user did not specify it:

- HTML: self-contained dark-themed HTML with inline SVG and CSS.
- ASCII: plain text box drawing that fits within 80 columns.

Default to HTML when no format is requested.

## Analysis

1. Read build manifests, deployment files, API definitions, and runtime
   configuration.
2. Identify users, the main system, deployable containers, components, data
   stores, queues, security boundaries, and external systems.
3. Map each relationship with direction, behavior, and protocol or technology.
4. Choose the smallest useful C4 level: System Context, Container, or Component.
5. Ask only questions that are not discoverable from the repository.
6. State assumptions and unknowns in the output.

## C4 Mapping

| Type | Identify |
|---|---|
| Person | Users and roles |
| Software system | Main project and external integrations |
| Container | Deployable applications, databases, queues, caches, and stores |
| Component | Logical groups inside a container |
| External system | Services outside the team's control |

If a small project has one deployable unit, skip the Container level when the
Component level gives a clearer result.

## Relationship Rules

Every arrow must state what happens, not only that two elements are connected.
Prefer labels such as `HTTPS/REST`, `JDBC`, `AMQP`, or `gRPC` when the code
supports them. Distinguish trust boundaries and external systems clearly.

## Quality Checklist

- The repository was scanned for relevant configuration and deployment files.
- Every important element has a name and a useful description.
- Every relationship has direction and a meaningful label.
- The selected C4 level matches the requested scope.
- The diagram is not too sparse or too crowded.
- The legend is outside system boundaries.
- HTML has no external dependency except optional fonts.
- ASCII output is no wider than 80 columns.
- Assumptions and undiscovered information are explicit.

Always produce one self-contained output file unless the user requests another
format or multiple focused views.
