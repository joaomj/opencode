---
name: architecture-diagram
description: Generate professional dark-themed system architecture diagrams as standalone HTML/SVG files. Use when the user asks for system architecture diagrams, infrastructure diagrams, cloud architecture visualizations, security diagrams, network topology diagrams, or any technical diagram showing system components and their relationships.
license: MIT
metadata:
  version: "1.0"
  author: Cocoon AI (hello@cocoon-ai.com)
  source: https://github.com/Cocoon-AI/architecture-diagram-generator
---

# Architecture Diagram Skill

Generate professional technical architecture diagrams as self-contained HTML files with inline SVG graphics and CSS styling.

## Design System

### Color Palette

Use these semantic colors for component types:

| Component Type | Fill (rgba) | Stroke |
|---------------|-------------|--------|
| Frontend | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (cyan-400) |
| Backend | `rgba(6, 78, 59, 0.4)` | `#34d399` (emerald-400) |
| Database | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (violet-400) |
| AWS/Cloud | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (amber-400) |
| Security | `rgba(136, 19, 55, 0.4)` | `#fb7185` (rose-400) |
| Message Bus | `rgba(251, 146, 60, 0.3)` | `#fb923c` (orange-400) |
| External/Generic | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (slate-400) |

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

### Spacing Rules

**CRITICAL:** When stacking components vertically, ensure proper spacing to avoid overlaps:

- **Standard component height:** 60px for services, 80-120px for larger components
- **Minimum vertical gap between components:** 40px
- **Inline connectors (message buses):** Place IN the gap between components, not overlapping

**Example vertical layout:**
```
Component A: y=70,  height=60  → ends at y=130
Gap:         y=130 to y=170   → 40px gap, place bus at y=140 (20px tall)
Component B: y=170, height=60  → ends at y=230
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
Kubernetes Cluster: y=30, height=460 → ends at y=490
Legend should start at: y=510 or below
SVG viewBox height: at least 560 to fit legend
```

**Wrong:** Legend at y=470 inside a cluster boundary that ends at y=490
**Right:** Legend at y=510, below the cluster boundary, with viewBox height extended

### Layout Structure

1. **Header** - Title with pulsing dot indicator, subtitle
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
    <li>• Item one</li>
    <li>• Item two</li>
  </ul>
</div>
```

## Base Template

Copy and customize this template. Key customization points:

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
        <h1>[PROJECT NAME] Architecture</h1>
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
        <text x="255" y="420" fill="#94a3b8" font-size="8" text-anchor="middle">• bucket-one</text>
        <text x="255" y="434" fill="#94a3b8" font-size="8" text-anchor="middle">• bucket-two</text>
        <text x="255" y="448" fill="#94a3b8" font-size="8" text-anchor="middle">• bucket-three</text>
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

        <!-- Database Component -->
        <rect x="700" y="280" width="120" height="50" rx="6" fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
        <text x="760" y="300" fill="white" font-size="11" font-weight="600" text-anchor="middle">Database</text>
        <text x="760" y="316" fill="#94a3b8" font-size="9" text-anchor="middle">PostgreSQL</text>

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
          <li>• Item one</li>
          <li>• Item two</li>
          <li>• Item three</li>
          <li>• Item four</li>
        </ul>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-dot amber"></div>
          <h3>Card Title 2</h3>
        </div>
        <ul>
          <li>• Item one</li>
          <li>• Item two</li>
          <li>• Item three</li>
          <li>• Item four</li>
        </ul>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-dot violet"></div>
          <h3>Card Title 3</h3>
        </div>
        <ul>
          <li>• Item one</li>
          <li>• Item two</li>
          <li>• Item three</li>
          <li>• Item four</li>
        </ul>
      </div>
    </div>

    <!-- Footer -->
    <p class="footer">
      [Project Name] • [Additional metadata]
    </p>
  </div>
</body>
</html>
```

## Output

Always produce a single self-contained `.html` file with:
- Embedded CSS (no external stylesheets except Google Fonts)
- Inline SVG (no external images)
- No JavaScript required (pure CSS animations)

The file should render correctly when opened directly in any modern browser.
