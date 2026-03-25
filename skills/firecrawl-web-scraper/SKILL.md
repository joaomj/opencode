---
name: firecrawl-web-scraper
description: Scrape single web pages with Firecrawl to markdown and structured JSON, with dynamic-page actions and local .firecrawl output
license: MIT
---

# Firecrawl Web Scraper

Scrape a single URL with Firecrawl and save results to local files.

This skill is intentionally narrow to avoid overengineering:
- Single URL scraping only
- Dynamic pages supported with browser actions
- Structured extraction supported with JSON schema
- Output saved under `.firecrawl/`

## When to Use This Skill

Use when user says:
- "scrape this url"
- "scrape this website"
- "scrape this article"
- "scrape this blog post"
- "save this blog post"
- "save this article"
- "save this newsletter"
- "add to my reading queue"

## Scope

In scope:
- Single URL scraping
- JavaScript-heavy pages (cookie banners, load-more, infinite scroll)
- Structured JSON extraction from a single page

Out of scope:
- PDF scraping
- Site crawling (`crawl`)
- URL discovery (`map`)
- Web search (`search`)

## Requirements

- `FIRECRAWL_API_KEY` environment variable
- Firecrawl Python SDK: `pip install firecrawl-py`
- Add `.firecrawl/` to `.gitignore`

## Workflow

Use this escalation path:
1. Basic scrape (`formats=["markdown"]`)
2. Add dynamic-page options (`waitFor`, `actions`)
3. Add structured extraction (`{"type": "json", ...}`)

Keep requests single-URL and only add options when needed.

## Shared Helpers

```python
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import json
import os
import re

from firecrawl import Firecrawl

app = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s-]", "", value.lower())
    words = [w for w in re.sub(r"\s+", "-", cleaned).split("-") if w]
    if not words:
        return "untitled"
    return "-".join(words[:6])


def output_paths(url: str, title: str) -> tuple[Path, Path]:
    domain = urlparse(url).netloc or "unknown-domain"
    slug = slugify(title)
    root = Path(".firecrawl") / domain
    root.mkdir(parents=True, exist_ok=True)

    md_path = root / f"{slug}.md"
    json_path = root / f"{slug}.json"

    if md_path.exists() or json_path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        md_path = root / f"{slug}-{stamp}.md"
        json_path = root / f"{slug}-{stamp}.json"

    return md_path, json_path


def get_value(doc: object, key: str, default: object = None) -> object:
    if isinstance(doc, dict):
        return doc.get(key, default)
    return getattr(doc, key, default)
```

## Recipe 1: Basic Single-URL Scrape

```python
url = "https://example.com/article"

doc = app.scrape(
    url,
    {
        "formats": ["markdown"],
        "onlyMainContent": True,
        "maxAge": 0,
    },
)

metadata = get_value(doc, "metadata", {}) or {}
title = metadata.get("title", "untitled")
markdown = get_value(doc, "markdown", "") or ""

md_path, _ = output_paths(url, title)
captured_at = datetime.now(timezone.utc).isoformat()

frontmatter = (
    "---\n"
    f"url: {url}\n"
    f"title: {title}\n"
    f"captured_at: {captured_at}\n"
    "---\n\n"
)

md_path.write_text(frontmatter + markdown, encoding="utf-8")
print(f"Saved markdown: {md_path}")
```

## Recipe 2: Dynamic Page Scrape

Use this for cookie banners, delayed rendering, and infinite scroll.

```python
url = "https://example.com/news"

doc = app.scrape(
    url,
    {
        "formats": ["markdown"],
        "onlyMainContent": True,
        "waitFor": 2000,
        "timeout": 30000,
        "actions": [
            {"type": "click", "selector": "#accept-cookies"},
            {"type": "wait", "milliseconds": 1000},
            {"type": "scroll", "direction": "down"},
            {"type": "wait", "selector": "article"},
        ],
    },
)

print(get_value(doc, "markdown", ""))
```

Action limits from Firecrawl docs:
- Maximum 50 actions per request
- Total wait time (`wait` actions + `waitFor`) must stay under 60 seconds

## Recipe 3: Markdown + Structured JSON

Use JSON extraction when you need consistent fields from one page.

```python
url = "https://example.com/article"

doc = app.scrape(
    url,
    {
        "formats": [
            "markdown",
            {
                "type": "json",
                "prompt": "Extract title, author, publishedDate, tags, and summary.",
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "author": {"type": "string"},
                        "publishedDate": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "summary": {"type": "string"},
                    },
                    "required": ["title", "summary"],
                },
            },
        ],
        "onlyMainContent": True,
        "maxAge": 0,
    },
)

metadata = get_value(doc, "metadata", {}) or {}
title = metadata.get("title", "untitled")
markdown = get_value(doc, "markdown", "") or ""
json_data = get_value(doc, "json", {}) or {}

md_path, json_path = output_paths(url, title)
captured_at = datetime.now(timezone.utc).isoformat()

md_frontmatter = (
    "---\n"
    f"url: {url}\n"
    f"title: {title}\n"
    f"captured_at: {captured_at}\n"
    "---\n\n"
)

md_path.write_text(md_frontmatter + markdown, encoding="utf-8")
json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

print(f"Saved markdown: {md_path}")
print(f"Saved structured data: {json_path}")
```

## Content Filtering

Use tag filtering when page output is noisy.

```python
doc = app.scrape(
    "https://example.com/article",
    {
        "formats": ["markdown"],
        "onlyMainContent": False,
        "includeTags": ["article", "h1", "p", ".content"],
        "excludeTags": ["#sidebar", "#comments", ".ad"],
    },
)
```

## Storage Pattern

```
.firecrawl/<domain>/<slug>.md
.firecrawl/<domain>/<slug>.json
```

- `<domain>`: URL domain
- `<slug>`: title in kebab-case (up to 6 words)
- If file exists: append timestamp `-YYYYMMDD-HHMMSS`

## Minimal Triage

If content is empty or incomplete:
1. Increase `waitFor` (for delayed rendering)
2. Add a `wait` action with a selector for the main content
3. Add `click`/`scroll` actions for gates like cookie banners or load-more

If still failing, the page likely requires heavier interaction or authentication.

## Notes

- Use `maxAge=0` when freshness is required; otherwise allow cache for speed
- Keep requests single-URL and avoid crawl/map/search for this skill
- Always quote URLs when passing them in shell commands
- Validate URL format before scraping

## Firecrawl References

- Docs: https://docs.firecrawl.dev
- Advanced Scraping Guide: https://docs.firecrawl.dev/advanced-scraping-guide
- Python SDK: https://docs.firecrawl.dev/sdks/python
