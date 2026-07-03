---
name: architecture-diagram
description: Generate professional dark-themed architecture diagrams as standalone HTML/SVG files or ASCII box-drawing. Supports general system architecture diagrams (infrastructure, cloud, security, network) and C4 model diagrams (System Context, Container, Component levels). Use when the user asks for system architecture diagrams, C4 diagrams, infrastructure diagrams, cloud architecture visualizations, security diagrams, network topology diagrams, or any technical diagram showing system components and their relationships.
license: MIT
metadata:
  version: "2.0"
  author: Cocoon AI (hello@cocoon-ai.com)
  source: https://github.com/Cocoon-AI/architecture-diagram-generator
  c4-levels: "L1 (System Context), L2 (Container), L3 (Component)"
  outputs: "HTML, ASCII"
---

# Architecture Diagram Skill

Generate professional technical architecture diagrams as self-contained HTML files with inline SVG graphics and CSS styling, or as plain ASCII box-drawing for terminal/markdown output.

## When To Use

This skill activates when the user's intent matches any of the following:

- "Create an architecture diagram" / "system architecture" / "infrastructure diagram"
- "Cloud architecture" / "security diagram" / "network topology"
- "Create a C4 diagram" / "C4 model" / "C4 architecture"
- "System Context diagram" / "Container diagram" / "Component diagram"
- "Architecture visualization" / "document the architecture"
- "Show how the system fits together" / "show system relationships"
- The user opens a workspace and asks to understand the project's architecture

## Output Format Selection

Ask the user which output format they want if they do not specify:

1. **HTML** -- Self-contained dark-themed HTML file with inline SVG. Rich visual, C4-standard colors, Person silhouettes, Cylinder databases. Opens in any browser.
2. **ASCII** -- Plain text box-drawing using `+`, `-`, `|`. Maximum compatibility -- renders in terminals, code comments, markdown docs, or pull request descriptions.

If the user does not state a preference, default to **HTML**.

## Architecture Analysis Process

When auto-analysing a codebase for architecture diagrams, follow these steps.

### Step 1: Identify Entry Points and Configuration

Read key project files to understand scope:
- **Build/manifest files**: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `build.gradle`, `CMakeLists.txt`, `requirements.txt`
- **Deployment config**: `docker-compose.yml`, `Dockerfile`, `kubernetes/*.yml`, `serverless.yml`, `terraform/*.tf`
- **API/service definitions**: OpenAPI specs (`openapi.yml`, `swagger.yml`), GraphQL schemas, gRPC protobufs
- **Runtime config**: `.env.example`, application config files, nginx/apache configs

### Step 2: Identify Architectural Elements

For C4 diagrams, map every discovered element to a C4 type:

| C4 Type | What to Look For | Example |
|---------|-----------------|---------|
| **Person** | Users, roles, external actors mentioned in docs or config | "end user", "admin", "customer" |
| **Software System** | The main project + external integrations | payment gateway, auth provider, the system itself |
| **Container** (L2) | Deployable processes: web apps, APIs, databases, queues, caches, file stores | Express app, PostgreSQL, Redis, RabbitMQ, S3 |
| **Component** (L3) | Logical groupings inside a container: controllers, services, repositories, middleware | UserController, PaymentService, OrderRepository |
| **External** | Third-party systems outside the team's control | Stripe, GitHub OAuth, SendGrid, AWS RDS |

If the project is small and only has one deployable unit, skip L2 (Container) and go directly to L3 (Component) inside that single container.

For general (non-C4) architecture diagrams, map elements to the component types in the Design System color palette below (Frontend, Backend, Database, AWS/Cloud, Security, Message Bus, External/Generic).

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
3. "For C4 diagrams: Which C4 level(s) do you need? (L1 System Context, L2 Container, L3 Component)"
4. "Do you want HTML or ASCII output?"
5. "Any specific areas of the architecture you want to highlight or omit?"

If the user is not available to answer, make reasonable assumptions based on the codebase and state them in the output.

## General Design System (HTML Output)

### Color Palette

Use these semantic colors for component types in general architecture diagrams:

| Component Type | Fill (rgba) | Stroke |
|---------------|-------------|--------|
| Frontend | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (cyan-400) |
| Backend | `rgba(6, 78, 59, 0.4)` | `#34d399` (emerald-400) |
| Database | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (violet-400) |
| AWS/Cloud | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (amber-400) |
| Security | `rgba(136, 19, 55, 0.4)` | `#fb7185` (rose-400) |
| Message Bus | `rgba(251, 146, 60, 0.3)` | `#fb923c` (orange-400) |
| External/Generic | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (slate-400) |

### C4 Color Palette

When generating C4 model diagrams, use these C4-standard colors:

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

### Typography

Use JetBrains Mono for all text (monospace, technical aesthetic):
```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
```

Font sizes: 12px for component names, 9px for sublabels, 8px for annotations, 7px for tiny labels.

### Visual Elements

**Background:** `#020617` (slate-950) with subtle grid pattern:
```svg
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
</pattern>
```

**Component boxes:** Rounded rectangles (`rx="6"`) with 1.5px stroke, semi-transparent fills.

**Security groups:** Dashed stroke (`stroke-dasharray="4,4"`), transparent fill, rose color.

**Region boundaries:** Larger dashed stroke (`stroke-dasharray="8,4"`), amber color, `rx="12"`.

**Arrows:** Use SVG marker for arrowheads:
```svg
<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
</marker>
```

**Arrow z-order:** Draw connection arrows early in the SVG (after the background grid) so they render behind component boxes. SVG elements are painted in document order, so arrows drawn first will appear behind shapes drawn later.

**Masking arrows behind transparent fills:** Since component boxes use semi-transparent fills (`rgba(..., 0.4)`), arrows behind them will show through. To fully mask arrows, draw an opaque background rect (e.g., `fill="#0f172a"`) at the same position before drawing the semi-transparent styled rect on top:
```svg
<!-- Opaque background to mask arrows -->
<rect x="X" y="Y" width="W" height="H" rx="6" fill="#0f172a"/>
<!-- Styled component on top -->
<rect x="X" y="Y" width="W" height="H" rx="6" fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
```

**Auth/security flows:** Dashed lines in rose color (`#fb7185`).

**Message buses / Event buses:** Small connector elements between services. Use orange color (`#fb923c` stroke, `rgba(251, 146, 60, 0.3)` fill):
```svg
<rect x="X" y="Y" width="120" height="20" rx="4" fill="rgba(251, 146, 60, 0.3)" stroke="#fb923c" stroke-width="1"/>
<text x="CENTER_X" y="Y+14" fill="#fb923c" font-size="7" text-anchor="middle">Kafka / RabbitMQ</text>
```

### C4-Specific SVG Shapes

**Person shape (for C4 diagrams):**
```svg
<!-- Person silhouette: circle head + trapezoid body -->
<ellipse cx="X+25" cy="Y+12" rx="8" ry="10" fill="#08427b" stroke="#ffffff" stroke-width="1.5"/>
<path d="M X+10 Y+28 Q X+25 Y+36 X+40 Y+28 L X+36 Y+52 L X+14 Y+52 Z" fill="#08427b" stroke="#ffffff" stroke-width="1.5"/>
<text x="X+25" y="Y+68" fill="#ffffff" font-size="9" text-anchor="middle">Person Name</text>
```

**Database (Cylinder shape, for C4 diagrams):**
```svg
<ellipse cx="CX" cy="Y+8" rx="W/2" ry="8" fill="DB_FILL" stroke="DB_STROKE" stroke-width="1.5"/>
<rect x="X" y="Y+8" width="W" height="H-16" fill="DB_FILL" stroke="DB_STROKE" stroke-width="1.5"/>
<line x1="X" y1="Y+12" x2="X" y2="Y+H-8" stroke="DB_STROKE" stroke-width="1.5"/>
<line x1="X+W" y1="Y+12" x2="X+W" y2="Y+H-8" stroke="DB_STROKE" stroke-width="1.5"/>
<ellipse cx="CX" cy="Y+H-8" rx="W/2" ry="8" fill="DB_FILL" stroke="DB_STROKE" stroke-width="1.5"/>
<text x="CX" y="Y+28" fill="#ffffff" font-size="9" font-weight="600" text-anchor="middle">Database Name</text>
<text x="CX" y="Y+42" fill="#94a3b8" font-size="8" text-anchor="middle">PostgreSQL</text>
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

### Spacing Rules

**CRITICAL:** When stacking components vertically, ensure proper spacing to avoid overlaps:

- **Standard component height:** 60px for services, 80-120px for larger components
- **Minimum vertical gap between components:** 40px
- **Inline connectors (message buses):** Place IN the gap between components, not overlapping

**Example vertical layout:**
```
Component A: y=70,  height=60  -> ends at y=130
Gap:         y=130 to y=170   -> 40px gap, place bus at y=140 (20px tall)
Component B: y=170, height=60  -> ends at y=230
```

**Wrong:** Placing a message bus at y=160 when Component B starts at y=170 (causes overlap)
**Right:** Placing a message bus at y=140, centered in the 40px gap (y=130 to y=170)

### Legend Placement

**CRITICAL:** Place legends OUTSIDE all boundary boxes (region boundaries, cluster boundaries, security groups).

- Calculate where all boundaries end (y position + height)
- Place legend at least 20px below the lowest boundary
- Expand SVG viewBox height if needed to accommodate

**Example:**
```
Kubernetes Cluster: y=30, height=460 -> ends at y=490
Legend should start at: y=510 or below
SVG viewBox height: at least 560 to fit legend
```

**Wrong:** Legend at y=470 inside a cluster boundary that ends at y=490
**Right:** Legend at y=510, below the cluster boundary, with viewBox height extended

- Include a colored swatch + label for each element type present

### Layout Structure

1. **Header** - Title with pulsing dot indicator, subtitle (add C4 level badge for C4 diagrams)
2. **Main SVG diagram** - Contained in rounded border card
3. **Summary cards** - Grid of 3 cards below diagram with key details
4. **Footer** - Minimal metadata line

### Component Box Pattern

```svg
<rect x="X" y="Y" width="W" height="H" rx="6" fill="FILL_COLOR" stroke="STROKE_COLOR" stroke-width="1.5"/>
<text x="CENTER_X" y="Y+20" fill="white" font-size="11" font-weight="600" text-anchor="middle">LABEL</text>
<text x="CENTER_X" y="Y+36" fill="#94a3b8" font-size="9" text-anchor="middle">sublabel</text>
```

### Info Card Pattern

```html
<div class="card">
  <div class="card-header">
    <div class="card-dot COLOR"></div>
    <h3>Title</h3>
  </div>
  <ul>
    <li>* Item one</li>
    <li>* Item two</li>
  </ul>
</div>
```

## Base Template (General Architecture)

Copy and customize this template for general (non-C4) architecture diagrams. Key customization points:

1. Update the `<title>` and header text
2. Modify SVG viewBox dimensions if needed (default: `1000 x 680`)
3. Add/remove/reposition component boxes
4. Draw connection arrows between components
5. Update the three summary cards
6. Update footer metadata

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[PROJECT NAME] Architecture Diagram</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'JetBrains Mono', monospace;
      background: #020617;
      min-height: 100vh;
      padding: 2rem;
      color: white;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
    }

    .header {
      margin-bottom: 2rem;
    }

    .header-row {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 0.5rem;
    }

    .pulse-dot {
      width: 12px;
      height: 12px;
      background: #22d3ee;
      border-radius: 50%;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    h1 {
      font-size: 1.5rem;
      font-weight: 700;
      letter-spacing: -0.025em;
    }

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

    .subtitle {
      color: #94a3b8;
      font-size: 0.875rem;
      margin-left: 1.75rem;
    }

    .diagram-container {
      background: rgba(15, 23, 42, 0.5);
      border-radius: 1rem;
      border: 1px solid #1e293b;
      padding: 1.5rem;
      overflow-x: auto;
    }

    svg {
      width: 100%;
      min-width: 900px;
      display: block;
    }

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

    .card-header {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.75rem;
    }

    .card-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    .card-dot.cyan { background: #22d3ee; }
    .card-dot.emerald { background: #34d399; }
    .card-dot.violet { background: #a78bfa; }
    .card-dot.amber { background: #fbbf24; }
    .card-dot.rose { background: #fb7185; }
    .card-dot.blue { background: #438dd5; }
    .card-dot.gray { background: #94a3b8; }
    .card-dot.orange { background: #fb923c; }

    .card h3 {
      font-size: 0.875rem;
      font-weight: 600;
    }

    .card ul {
      list-style: none;
      color: #94a3b8;
      font-size: 0.75rem;
    }

    .card li {
      margin-bottom: 0.375rem;
    }

    .footer {
      text-align: center;
      margin-top: 1.5rem;
      color: #475569;
      font-size: 0.75rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <div class="header-row">
        <div class="pulse-dot"></div>
        <h1>[PROJECT NAME] Architecture <span class="c4-level-badge"><!-- L1/L2/L3 badge for C4, remove for general --></span></h1>
      </div>
      <p class="subtitle">[Subtitle description]</p>
    </div>

    <!-- Main Diagram -->
    <div class="diagram-container">
      <svg viewBox="0 0 1000 680">
        <!-- Definitions -->
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#64748b" />
          </marker>
          <marker id="arrow-dashed" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#fb7185" />
          </marker>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
          </pattern>
        </defs>

        <!-- Background Grid -->
        <rect width="100%" height="100%" fill="url(#grid)" />

        <!-- =================================================================
             COMPONENT EXAMPLES - Copy and customize these patterns
             ================================================================= -->

        <!-- External/Generic Component -->
        <rect x="30" y="280" width="100" height="50" rx="6" fill="rgba(30, 41, 59, 0.5)" stroke="#94a3b8" stroke-width="1.5"/>
        <text x="80" y="300" fill="white" font-size="11" font-weight="600" text-anchor="middle">Users</text>
        <text x="80" y="316" fill="#94a3b8" font-size="9" text-anchor="middle">Browser/Mobile</text>

        <!-- C4 Person shape (for C4 diagrams) -->
        <!--
        <ellipse cx="80" cy="92" rx="8" ry="10" fill="#08427b" stroke="#ffffff" stroke-width="1.5"/>
        <path d="M 65 Y+28 Q 80 Y+36 95 Y+28 L 91 Y+52 L 69 Y+52 Z" fill="#08427b" stroke="#ffffff" stroke-width="1.5"/>
        <text x="80" y="68" fill="#ffffff" font-size="9" text-anchor="middle">Person Name</text>
        -->

        <!-- Security Component -->
        <rect x="30" y="80" width="100" height="60" rx="6" fill="rgba(136, 19, 55, 0.4)" stroke="#fb7185" stroke-width="1.5"/>
        <text x="80" y="105" fill="white" font-size="11" font-weight="600" text-anchor="middle">Auth Provider</text>
        <text x="80" y="121" fill="#94a3b8" font-size="9" text-anchor="middle">OAuth 2.0</text>

        <!-- Region/Cloud Boundary -->
        <rect x="160" y="40" width="820" height="620" rx="12" fill="rgba(251, 191, 36, 0.05)" stroke="#fbbf24" stroke-width="1" stroke-dasharray="8,4"/>
        <text x="172" y="58" fill="#fbbf24" font-size="10" font-weight="600">AWS Region: us-west-2</text>

        <!-- AWS/Cloud Service -->
        <rect x="200" y="280" width="110" height="50" rx="6" fill="rgba(120, 53, 15, 0.3)" stroke="#fbbf24" stroke-width="1.5"/>
        <text x="255" y="300" fill="white" font-size="11" font-weight="600" text-anchor="middle">CloudFront</text>
        <text x="255" y="316" fill="#94a3b8" font-size="9" text-anchor="middle">CDN</text>

        <!-- Multi-line AWS Component (S3 Buckets example) -->
        <rect x="200" y="380" width="110" height="100" rx="6" fill="rgba(120, 53, 15, 0.3)" stroke="#fbbf24" stroke-width="1.5"/>
        <text x="255" y="400" fill="white" font-size="11" font-weight="600" text-anchor="middle">S3 Buckets</text>
        <text x="255" y="420" fill="#94a3b8" font-size="8" text-anchor="middle">* bucket-one</text>
        <text x="255" y="434" fill="#94a3b8" font-size="8" text-anchor="middle">* bucket-two</text>
        <text x="255" y="448" fill="#94a3b8" font-size="8" text-anchor="middle">* bucket-three</text>
        <text x="255" y="466" fill="#fbbf24" font-size="7" text-anchor="middle">OAI Protected</text>

        <!-- Security Group (dashed boundary) -->
        <rect x="350" y="265" width="120" height="80" rx="8" fill="transparent" stroke="#fb7185" stroke-width="1" stroke-dasharray="4,4"/>
        <text x="358" y="279" fill="#fb7185" font-size="8">sg-name :port</text>

        <!-- Component inside security group -->
        <rect x="360" y="280" width="100" height="50" rx="6" fill="rgba(120, 53, 15, 0.3)" stroke="#fbbf24" stroke-width="1.5"/>
        <text x="410" y="300" fill="white" font-size="11" font-weight="600" text-anchor="middle">Load Balancer</text>
        <text x="410" y="316" fill="#94a3b8" font-size="9" text-anchor="middle">HTTPS :443</text>

        <!-- Backend Component -->
        <rect x="510" y="280" width="110" height="50" rx="6" fill="rgba(6, 78, 59, 0.4)" stroke="#34d399" stroke-width="1.5"/>
        <text x="565" y="300" fill="white" font-size="11" font-weight="600" text-anchor="middle">API Server</text>
        <text x="565" y="316" fill="#94a3b8" font-size="9" text-anchor="middle">FastAPI :8000</text>

        <!-- Database Component (simple rect) -->
        <rect x="700" y="280" width="120" height="50" rx="6" fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
        <text x="760" y="300" fill="white" font-size="11" font-weight="600" text-anchor="middle">Database</text>
        <text x="760" y="316" fill="#94a3b8" font-size="9" text-anchor="middle">PostgreSQL</text>

        <!-- Database Cylinder shape (for C4 diagrams) -->
        <!--
        <ellipse cx="760" cy="288" rx="60" ry="8" fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
        <rect x="700" y="288" width="120" height="34" fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
        <line x1="700" y1="292" x2="700" y2="322" stroke="#a78bfa" stroke-width="1.5"/>
        <line x1="820" y1="292" x2="820" y2="322" stroke="#a78bfa" stroke-width="1.5"/>
        <ellipse cx="760" cy="322" rx="60" ry="8" fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
        <text x="760" y="310" fill="white" font-size="9" font-weight="600" text-anchor="middle">Database</text>
        <text x="760" y="324" fill="#94a3b8" font-size="8" text-anchor="middle">PostgreSQL</text>
        -->

        <!-- Frontend Component -->
        <rect x="200" y="520" width="200" height="110" rx="8" fill="rgba(8, 51, 68, 0.4)" stroke="#22d3ee" stroke-width="1.5"/>
        <text x="300" y="545" fill="white" font-size="12" font-weight="600" text-anchor="middle">Frontend</text>
        <text x="300" y="565" fill="#94a3b8" font-size="9" text-anchor="middle">React + TypeScript</text>
        <text x="300" y="580" fill="#94a3b8" font-size="9" text-anchor="middle">Additional detail</text>
        <text x="300" y="595" fill="#94a3b8" font-size="9" text-anchor="middle">More info</text>
        <text x="300" y="615" fill="#22d3ee" font-size="8" text-anchor="middle">domain.example.com</text>

        <!-- =================================================================
             ARROW EXAMPLES
             ================================================================= -->

        <!-- Standard arrow with label -->
        <line x1="130" y1="305" x2="198" y2="305" stroke="#22d3ee" stroke-width="1.5" marker-end="url(#arrowhead)"/>
        <text x="164" y="299" fill="#94a3b8" font-size="9" text-anchor="middle">HTTPS</text>

        <!-- Simple arrow (no label) -->
        <line x1="310" y1="305" x2="358" y2="305" stroke="#22d3ee" stroke-width="1.5" marker-end="url(#arrowhead)"/>

        <!-- Vertical arrow -->
        <line x1="255" y1="330" x2="255" y2="378" stroke="#fbbf24" stroke-width="1.5" marker-end="url(#arrowhead)"/>
        <text x="270" y="358" fill="#94a3b8" font-size="9">OAI</text>

        <!-- Dashed arrow (for auth/security flows) -->
        <line x1="460" y1="305" x2="508" y2="305" stroke="#34d399" stroke-width="1.5" marker-end="url(#arrowhead)"/>
        <line x1="620" y1="305" x2="698" y2="305" stroke="#a78bfa" stroke-width="1.5" marker-end="url(#arrowhead)"/>
        <text x="655" y="299" fill="#94a3b8" font-size="9">TLS</text>

        <!-- Curved path for auth flow -->
        <path d="M 80 140 L 80 200 Q 80 220 100 220 L 200 220 Q 220 220 220 240 L 220 278" fill="none" stroke="#fb7185" stroke-width="1.5" stroke-dasharray="5,5"/>
        <text x="150" y="210" fill="#fb7185" font-size="8">JWT + PKCE</text>

        <!-- =================================================================
             LEGEND
             ================================================================= -->
        <text x="720" y="70" fill="white" font-size="10" font-weight="600">Legend</text>

        <rect x="720" y="82" width="16" height="10" rx="2" fill="rgba(8, 51, 68, 0.4)" stroke="#22d3ee" stroke-width="1"/>
        <text x="742" y="90" fill="#94a3b8" font-size="8">Frontend</text>

        <rect x="720" y="98" width="16" height="10" rx="2" fill="rgba(6, 78, 59, 0.4)" stroke="#34d399" stroke-width="1"/>
        <text x="742" y="106" fill="#94a3b8" font-size="8">Backend</text>

        <rect x="720" y="114" width="16" height="10" rx="2" fill="rgba(120, 53, 15, 0.3)" stroke="#fbbf24" stroke-width="1"/>
        <text x="742" y="122" fill="#94a3b8" font-size="8">Cloud Service</text>

        <rect x="720" y="130" width="16" height="10" rx="2" fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1"/>
        <text x="742" y="138" fill="#94a3b8" font-size="8">Database</text>

        <rect x="720" y="146" width="16" height="10" rx="2" fill="rgba(136, 19, 55, 0.4)" stroke="#fb7185" stroke-width="1"/>
        <text x="742" y="154" fill="#94a3b8" font-size="8">Security</text>

        <line x1="720" y1="168" x2="736" y2="168" stroke="#fb7185" stroke-width="1" stroke-dasharray="3,3"/>
        <text x="742" y="171" fill="#94a3b8" font-size="8">Auth Flow</text>

        <rect x="720" y="178" width="16" height="10" rx="2" fill="transparent" stroke="#fb7185" stroke-width="1" stroke-dasharray="3,3"/>
        <text x="742" y="186" fill="#94a3b8" font-size="8">Security Group</text>
      </svg>
    </div>

    <!-- Info Cards -->
    <div class="cards">
      <div class="card">
        <div class="card-header">
          <div class="card-dot rose"></div>
          <h3>Card Title 1</h3>
        </div>
        <ul>
          <li>* Item one</li>
          <li>* Item two</li>
          <li>* Item three</li>
          <li>* Item four</li>
        </ul>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-dot amber"></div>
          <h3>Card Title 2</h3>
        </div>
        <ul>
          <li>* Item one</li>
          <li>* Item two</li>
          <li>* Item three</li>
          <li>* Item four</li>
        </ul>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-dot violet"></div>
          <h3>Card Title 3</h3>
        </div>
        <ul>
          <li>* Item one</li>
          <li>* Item two</li>
          <li>* Item three</li>
          <li>* Item four</li>
        </ul>
      </div>
    </div>

    <!-- Footer -->
    <p class="footer">
      [Project Name] * [Additional metadata]
    </p>
  </div>
</body>
</html>
```

When generating the SVG viewBox dimensions:
- **General architecture diagrams**: viewBox `0 0 1000 680` (default)
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
  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
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

- [ ] Codebase was scanned for config, build, and deployment files (if applicable)
- [ ] All discovered systems, containers, and components are modelled
- [ ] Every element has a name and technology/description label
- [ ] Relationships have meaningful descriptions (not just "uses")
- [ ] External systems are clearly distinguished
- [ ] Database elements use cylinder shape (HTML) or `( )` style (ASCII) for C4 diagrams
- [ ] The correct C4 level(s) were generated (if C4 diagram)
- [ ] Views are neither too sparse nor too crowded
- [ ] Legend is present and outside all boundaries
- [ ] HTML file is self-contained (no external deps except Google Fonts)
- [ ] ASCII diagram fits within 80 columns
- [ ] Styling is consistent and follows the appropriate color conventions
- [ ] Unclear discoveries were noted for the user

## Output

Always produce a single self-contained `.html` file with:
- Embedded CSS (no external stylesheets except Google Fonts)
- Inline SVG (no external images)
- No JavaScript required (pure CSS animations)

The file should render correctly when opened directly in any modern browser.
