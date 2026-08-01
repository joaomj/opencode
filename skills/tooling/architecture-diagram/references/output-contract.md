# Architecture Diagram Output Contract

## HTML

- Use a dark background, clear contrast, and a readable monospace or sans-serif
  font.
- Use inline SVG. Do not depend on external stylesheets or image files.
- Use labeled boxes for systems and containers, cylinders for databases, and
  explicit boundaries for trust or system boundaries.
- Use arrowheads and relationship labels. Avoid crossing arrows when a clearer
  layout is possible.
- Use a viewBox suited to the diagram: approximately `1000 x 600` for System
  Context and `1000 x 800` for Container or Component views.
- Include a title, legend, and a short summary of scope.

## ASCII

Use these shapes:

```text
[Person]       +== System ==+       +-- Container --+
( Database )   { Queue }            [External system]
. . . . . . .  System boundary
```

Use arrows with a separate protocol label:

```text
[User] -- HTTPS/REST --> +== System ==+
```

Keep one-character gaps between boxes. Put the legend outside all boundaries.
Split a large diagram into focused views instead of exceeding 80 columns.

## C4 Levels

```text
L1 System Context: people, the system, and external systems
L2 Container: deployable applications and data stores inside the system
L3 Component: logical components inside one container
```

Do not include implementation details that do not help explain the selected
level.
