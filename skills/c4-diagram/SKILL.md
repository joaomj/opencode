---
name: c4-diagram
description: >
  Generate C4 model architecture diagrams (System Context, Container, Component
  levels) in HTML/SVG or plain ASCII format. Use when the user asks for C4
  diagrams, architecture visualization, system design documentation, software
  architecture diagrams, structural system views, or wants to document a
  system's architecture using the C4 model.
license: MIT
metadata:
  version: "1.0"
  c4-levels: "L1 (System Context), L2 (Container), L3 (Component)"
  outputs: "HTML, ASCII"
---

# C4 Architecture Diagram Skill

Generate C4 model diagrams in two output formats: **dark-themed HTML/SVG** and **plain ASCII box-drawing**.

C4 levels supported:
- **L1 - System Context**: The system under analysis, its users, and external dependencies
- **L2 - Container**: Deployable units (web apps, APIs, databases, queues, stores)
- **L3 - Component**: Logical groupings inside a container (controllers, services, repositories)

## When To Use

This skill activates when the user's intent matches any of the following (without requiring exact phrasing):

- "Create a C4 diagram" / "C4 model" / "C4 architecture"
- "System Context diagram" / "Container diagram" / "Component diagram"
- "Architecture visualization" / "document the architecture"
- "Show how the system fits together" / "show system relationships"
- Any request that implies structural software architecture documentation
- The user opens a workspace and asks to understand the project's architecture

## Output Format Selection

Ask the user which output format they want if they do not specify:

1. **HTML** -- Self-contained dark-themed HTML file with inline SVG. Rich visual, C4-standard colors, Person silhouettes, Cylinder databases. Opens in any browser.
2. **ASCII** -- Plain text box-drawing using `+`, `-`, `|`. Maximum compatibility -- renders in terminals, code comments, markdown docs, or pull request descriptions.

If the user does not state a preference, default to **HTML**.

## Architecture Analysis Process

When auto-analysing a codebase, follow these steps to discover architectural elements.

### Step 1: Identify Entry Points and Configuration

Read key project files to understand scope:
- **Build/manifest files**: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `CMakeLists.txt`, `requirements.txt`
- **Deployment config**: `docker-compose.yml`, `Dockerfile`, `kubernetes/*.yml`, `serverless.yml`, `terraform/*.tf`
- **API/service definitions**: OpenAPI specs (`openapi.yml`, `swagger.yml`), GraphQL schemas, gRPC protobufs
- **Runtime config**: `.env.example`, application config files, nginx/apache configs

### Step 2: Identify C4 Elements

Map every discovered element to a C4 type:

| C4 Type | What to Look For | Example |
|---------|-----------------|---------|
| **Person** | Users, roles, external actors mentioned in docs or config | "end user", "admin", "customer" |
| **Software System** | The main project + external integrations | payment gateway, auth provider, the system itself |
| **Container** (L2) | Deployable processes: web apps, APIs, databases, queues, caches, file stores | Express app, PostgreSQL, Redis, RabbitMQ, S3 |
| **Component** (L3) | Logical groupings inside a container: controllers, services, repositories, middleware | UserController, PaymentService, OrderRepository |
| **External** | Third-party systems outside the team's control | Stripe, GitHub OAuth, SendGrid, AWS RDS |

If the project is small and only has one deployable unit, skip L2 (Container) and go directly to L3 (Component) inside that single container.

### Step 3: Map Relationships

For each pair of elements, determine:
- **Direction** -- Who initiates the interaction?
- **Description** -- What happens? ("Sends HTTP request to", "Reads from", "Publishes events to")
- **Technology/protocol** -- How do they communicate? ("HTTPS/REST", "JDBC", "AMQP", "gRPC")

Common relationship patterns in codebases:
- `WebApp -> API` via HTTP/REST
- `API -> Database` via JDBC/ODBC/ORM
- `API -> MessageQueue` via AMQP/Kafka protocol
- `Service -> ExternalSystem` via HTTP/GraphQL
- `Person -> WebApp` via browser (HTTPS)

### Step 4: Ask Clarifying Questions

Before generating diagrams, ask the user only if the answers are not discoverable from code:

1. "What is the system name and purpose?"
2. "Are there external systems or user roles not visible in the code?"
3. "Which C4 level(s) do you need? (L1 System Context, L2 Container, L3 Component)"
4. "Do you want HTML or ASCII output?"
5. "Any specific areas of the architecture you want to highlight or omit?"

If the user is not available to answer, make reasonable assumptions based on the codebase and state them in the output.

## C4 Design System (HTML Output)

### Color Palette

| C4 Element | Fill (rgba) | Stroke | Text |
|------------|-------------|--------|------|
| Person | `rgba(8, 66, 123, 0.4)` | `#08427b` | `#ffffff` |
| Software System (L1) | `rgba(17, 104, 189, 0.4)` | `#1168bd` | `#ffffff` |
| Container (L2) | `rgba(67, 141, 213, 0.4)` | `#438dd5` | `#ffffff` |
| Component (L3) | `rgba(133, 187, 240, 0.4)` | `#85bbf0` | `#000000` |
| Database | `rgba(76, 29, 149, 0.4)` | `#a78bfa` | `#ffffff` |
| External/Generic | `rgba(153, 153, 153, 0.3)` | `#999999` | `#ffffff` |
| Queue/Bus | `rgba(251, 146, 60, 0.3)` | `#fb923c` | `#ffffff` |
| Boundary/Group | `rgba(251, 191, 36, 0.05)` | `#fbbf24` | `#fbbf24` |

### C4 SVG Shapes

**Person shape:**
```svg
<!-- Person silhouette: circle head + trapezoid body -->
<ellipse cx="X+25" cy="Y+12" rx="8" ry="10" fill="#08427b" stroke="#ffffff" stroke-width="1.5"/>
<path d="M X+10 Y+28 Q X+25 Y+36 X+40 Y+28 L X+36 Y+52 L X+14 Y+52 Z" fill="#08427b" stroke="#ffffff" stroke-width="1.5"/>
<text x="X+25" y="Y+68" fill="#ffffff" font-size="9" text-anchor="middle">Person Name</text>
```

**Standard box (System / Container / Component):**
```svg
<rect x="X" y="Y" width="W" height="H" rx="6" fill="FILL" stroke="STROKE" stroke-width="1.5"/>
<text x="CX" y="Y+20" fill="TEXT" font-size="11" font-weight="600" text-anchor="middle">Element Name</text>
<text x="CX" y="Y+36" fill="#94a3b8" font-size="9" text-anchor="middle">Description / Tech</text>
```

**Database (Cylinder shape):**
```svg
<ellipse cx="CX" cy="Y+8" rx="W/2" ry="8" fill="DB_FILL" stroke="DB_STROKE" stroke-width="1.5"/>
<rect x="X" y="Y+8" width="W" height="H-16" fill="DB_FILL" stroke="DB_STROKE" stroke-width="1.5"/>
<line x1="X" y1="Y+12" x2="X" y2="Y+H-8" stroke="DB_STROKE" stroke-width="1.5"/>
<line x1="X+W" y1="Y+12" x2="X+W" y2="Y+H-8" stroke="DB_STROKE" stroke-width="1.5"/>
<ellipse cx="CX" cy="Y+H-8" rx="W/2" ry="8" fill="DB_FILL" stroke="DB_STROKE" stroke-width="1.5"/>
<text x="CX" y="Y+28" fill="#ffffff" font-size="9" font-weight="600" text-anchor="middle">Database Name</text>
<text x="CX" y="Y+42" fill="#94a3b8" font-size="8" text-anchor="middle">PostgreSQL</text>
```

**Arrows:**
```svg
<marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
</marker>
<line x1="X1" y1="Y" x2="X2" y2="Y" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>
<text x="CX" y="Y-4" fill="#94a3b8" font-size="8" text-anchor="middle">HTTPS/REST</text>
```

**Background grid** (reuse from architecture-diagram):
```svg
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

### Typography

Use JetBrains Mono (like architecture-diagram skill):
```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Layout Conventions by C4 Level

**L1 - System Context:**
- Center: the primary software system
- Left: people/actors
- Right: external systems
- Top/bottom: any queue/message boundaries
- One boundary box around "External Systems" if there are 3+

**L2 - Container:**
- Inside a dashed boundary labeled with the system name
- Top row: web/UI containers
- Middle row: API/service containers  
- Bottom row: data stores (databases, caches, queues)
- External containers outside the boundary

**L3 - Component:**
- Inside a dashed boundary labeled with the container name
- Left column: controllers/entry points
- Middle column: services/business logic
- Right column: repositories/data access
- Arrows flow left-to-right

### Legend Placement

- Place legend in the top-right or bottom-right corner
- Always place OUTSIDE any dashed boundary boxes
- Include a colored swatch + label for each element type present

### Opaque Background Pattern (Arrow Masking)

When a semi-transparent box overlaps an arrow, add an opaque background rect:
```svg
<rect x="X" y="Y" width="W" height="H" rx="6" fill="#0f172a"/>
<rect x="X" y="Y" width="W" height="H" rx="6" fill="rgba(67, 141, 213, 0.4)" stroke="#438dd5" stroke-width="1.5"/>
```
This prevents arrows behind components from showing through the semi-transparent fill.

## HTML Output Template

Generate a self-contained HTML file following this structure. Adapt for each C4 level:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[System Name] - C4 [View Type] Diagram</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    /* === CORE STYLES === */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'JetBrains Mono', monospace;
      background: #020617;
      min-height: 100vh;
      padding: 2rem;
      color: white;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    .header { margin-bottom: 2rem; }
    .header-row { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem; }
    .pulse-dot {
      width: 12px; height: 12px; background: #22d3ee;
      border-radius: 50%; animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    h1 { font-size: 1.5rem; font-weight: 700; letter-spacing: -0.025em; }
    .subtitle { color: #94a3b8; font-size: 0.875rem; margin-left: 1.75rem; }
    .c4-level-badge {
      display: inline-block;
      background: rgba(67, 141, 213, 0.3);
      color: #438dd5;
      padding: 0.25rem 0.75rem;
      border-radius: 999px;
      font-size: 0.75rem;
      border: 1px solid #438dd5;
      margin-left: 0.5rem;
    }
    .diagram-container {
      background: rgba(15, 23, 42, 0.5);
      border-radius: 1rem;
      border: 1px solid #1e293b;
      padding: 1.5rem;
      overflow-x: auto;
    }
    svg { width: 100%; min-width: 900px; display: block; }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1rem;
      margin-top: 2rem;
    }
    .card {
      background: rgba(15, 23, 42, 0.5);
      border-radius: 0.75rem;
      border: 1px solid #1e293b;
      padding: 1.25rem;
    }
    .card-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem; }
    .card-dot { width: 8px; height: 8px; border-radius: 50%; }
    .card-dot.blue { background: #438dd5; }
    .card-dot.violet { background: #a78bfa; }
    .card-dot.gray { background: #94a3b8; }
    .card-dot.orange { background: #fb923c; }
    .card h3 { font-size: 0.875rem; font-weight: 600; }
    .card ul { list-style: none; color: #94a3b8; font-size: 0.75rem; }
    .card li { margin-bottom: 0.375rem; }
    .footer { text-align: center; margin-top: 1.5rem; color: #475569; font-size: 0.75rem; }
  </style>
</head>
<body>
  <div class="container">
    <!-- HEADER -->
    <div class="header">
      <div class="header-row">
        <div class="pulse-dot"></div>
        <h1>[System Name] <span class="c4-level-badge">L[1|2|3]: [View Type]</span></h1>
      </div>
      <p class="subtitle">[View Description] -- [Technology Stack Summary]</p>
    </div>

    <!-- DIAGRAM SVG -->
    <div class="diagram-container">
      <svg viewBox="0 0 1000 [HEIGHT]">
        <defs>
          <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
          </marker>
          <marker id="arrow-dashed" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#fb7185" />
          </marker>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
          </pattern>
        </defs>

        <rect width="100%" height="100%" fill="url(#grid)" />

        <!-- ===== ELEMENTS ===== -->
        <!-- See patterns in C4 Design System section above -->
        <!-- ... render C4 elements here ... -->

        <!-- ===== ARROWS ===== -->
        <!-- ... render relationships here ... -->

        <!-- ===== LEGEND ===== -->
        <text x="810" y="40" fill="#ffffff" font-size="11" font-weight="600">Legend</text>
        <!-- Legend items based on element types present -->
      </svg>
    </div>

    <!-- INFO CARDS -->
    <div class="cards">
      <div class="card">
        <div class="card-header">
          <div class="card-dot blue"></div>
          <h3>Elements</h3>
        </div>
        <ul>
          <li>[N] Systems</li>
          <li>[N] Containers</li>
          <li>[N] External Dependencies</li>
          <li>[N] Actors</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-header">
          <div class="card-dot violet"></div>
          <h3>Relationships</h3>
        </div>
        <ul>
          <li>[N] HTTP/REST connections</li>
          <li>[N] Database connections</li>
          <li>[N] Async/Message queue links</li>
          <li>[N] External integrations</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-header">
          <div class="card-dot gray"></div>
          <h3>Tech Stack</h3>
        </div>
        <ul>
          <li>• [Runtime language/framework]</li>
          <li>• [Database technology]</li>
          <li>• [Message queue if any]</li>
          <li>• [Infrastructure / cloud]</li>
        </ul>
      </div>
    </div>

    <!-- FOOTER -->
    <p class="footer">[System Name] -- C4 Diagram generated from code analysis</p>
  </div>
</body>
</html>
```

When generating the SVG:
- **L1 System Context**: viewBox height ~600. Center main system at (500, 250). Left actors, right externals.
- **L2 Container**: viewBox height ~800. System boundary box takes up most space. Top/bottom layering.
- **L3 Component**: viewBox height ~800. Container boundary box. Left-to-right flow.

## ASCII Output Specification

Plain ASCII diagrams using `+`, `-`, `|` characters. Maximum width: **80 characters**. Max height: flexible but prefer fitting in one terminal screen (~40 lines).

### ASCII Shape Conventions

```
Person:       [Person Name]
System:       +=== System Name ===+
Container:    +-- Container Name --+
Component:    + Component Name +
Database:     ( Database Name ).....
              ( PostgreSQL    ).....
External:     [External: System Name]
Queue/Bus:    { Queue Name }
Boundary:     . . . . . . . . . . . . . .
              .  System Boundary          .
              . . . . . . . . . . . . . .
```

### ASCII Arrow Conventions

```
One-way:  - - - - - ->  or  = = = = = = >
Two-way:  < - - - - - - >
Label:    | HTTPS/REST |
          v             v
```

### Spacing Rules for ASCII

- Minimum 1-character gap between boxes and boundaries
- Arrow labels go on a separate line starting with `|` or inline if short
- Boundaries use `. . .` (dot-space pattern) for dashed effect
- Database name wraps inside `(  )` -- max 15 chars per line, use 2 lines if needed
- Legend at the bottom, outside any boundary

### ASCII Diagram Templates

**L1 - System Context:**
```
+============================================================================+
|                   System Context - [System Name]                           |
+============================================================================+

  [User]                                     [External: Payment Gateway]
    |                                            |
    |  HTTPS/REST                               |  HTTPS
    v                                            v
  +========================================================================+
  |                        [System Name]                                 |
  |  +------------------------------------------------------------------+ |
  |  |  "Brief description of what the system does"                    | |
  |  +------------------------------------------------------------------+ |
  +========================================================================+
    |
    |  JDBC
    v
  ( Database )...........
  ( PostgreSQL ).........
    |
    |  AMQP
    v
  { Event Queue }
                     . . . . . . . . . . . .
                     .  [Auth Provider]     .
                     .  OAuth 2.0           .
                     . . . . . . . . . . . .

Legend:
  [  ] Person/External     +==+ System     +--+ Container
  (  ) Database            {  } Queue
```

**L2 - Container:**
```
+============================================================================+
|                   Container Diagram - [System Name]                       |
+============================================================================+

                                                    . . . . . . . . . . . . .
  [User]                                            .  External: Auth0      .
    |                                               .  OAuth 2.0            .
    |  HTTPS                                        . . . . . . . . . . . . .
    v                                                    ^
  +========================================================================+
  |  [System Name]                                                          |
  |                                                                         |
  |  +-- Web App --+   HTTPS/REST   +-- API Server --+  JDBC  +----------+ |
  |  | React SPA   |--------------->| FastAPI :8000  |------->| Database | |
  |  | Port 3000   |                | Express :8080  |        | Postgres | |
  |  +--------------+               +-----------------+        +----------+ |
  |                                     |                                  |
  |                                     | AMQP                             |
  |                                     v                                  |
  |                                +------------+                          |
  |                                | Event Bus  |                          |
  |                                | RabbitMQ   |                          |
  |                                +------------+                          |
  +========================================================================+

Legend:
  [  ] Person     +==+ System   +--+ Container   (  ) DB   {  } Queue/AQMP
```

**L3 - Component:**
```
+============================================================================+
|              Component Diagram - API Server Container                      |
+============================================================================+

  [User]
    |
    |  HTTPS
    v
  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
  .                      API Server Container                             .
  .                                                                       .
  .  +--------------+       +------------------+        +---------------+ .
  .  | AuthController|----->| AuthService      |------->| UserRepo      | .
  .  +--------------+       | "Handles login,  |        +---------------+ .
  .  +--------------+       |  registration,   |          |               .
  .  |  ProductCtrl |----->|  password reset" |          |               .
  .  +--------------+       +------------------+          v               .
  .  +--------------+       +------------------+        +---------------+ .
  .  |  OrderCtrl   |----->| OrderService     |------->| OrderRepo     | .
  .  +--------------+       | "Processes       |        +---------------+ .
  .                         |  checkout,       |          |               .
  .                         |  handles         |          v               .
  .                         |  inventory"      |        +---------------+ .
  .                         +------------------+        | ProductRepo   | .
  .                                                      +---------------+ .
  .                                                          |             .
  .                                                          v             .
  .                                                      +---------------+ .
  .                                                      | InventoryRepo| .
  .                                                      +---------------+ .
  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    |
    |  JDBC
    v
  ( Database )...........
  ( PostgreSQL ).........

Legend:
  [  ] Person    Ctrl=Controller   Service=Business Logic   Repo=Data Access
  (  ) Database
```

### ASCII Width Constraint

All ASCII diagrams must fit within **80 columns**. If the architecture is large:
- Split into multiple focused diagrams instead of one huge one
- Omit low-priority elements
- Use abbreviations and add a legend

## Quality Checklist

Before presenting the output to the user, verify:

- [ ] Codebase was scanned for config, build, and deployment files
- [ ] All discovered systems, containers, and components are modelled
- [ ] Every element has a name and technology/description label
- [ ] Relationships have meaningful descriptions (not just "uses")
- [ ] External systems are clearly distinguished
- [ ] Database elements use cylinder shape (HTML) or `( )` style (ASCII)
- [ ] The correct C4 level(s) were generated
- [ ] Views are neither too sparse nor too crowded
- [ ] Legend is present and outside all boundaries
- [ ] HTML file is self-contained (no external deps except Google Fonts)
- [ ] ASCII diagram fits within 80 columns
- [ ] Styling is consistent and follows C4 color conventions
- [ ] Unclear discoveries were noted for the user
