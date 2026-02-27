---
name: firecrawl-web-scraper
description: Scrape websites to markdown using Firecrawl API, saving blog posts, articles, Arxiv papers, and newsletters to local files
license: MIT
---

# Firecrawl Web Scraper

Scrape websites to clean markdown using Firecrawl API. Saves content locally with metadata frontmatter.

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
- "download this arxiv paper"

## Requirements

- `FIRECRAWL_API_KEY` environment variable
- Firecrawl Python SDK: `pip install firecrawl-py`

## Usage

### Basic Scraping

```python
import os
from firecrawl import Firecrawl

app = Firecrawl(api_key=os.environ.get("FIRECRAWL_API_KEY"))

# Scrape URL to markdown (always fresh)
doc = app.scrape(
    url="https://example.com/article",
    formats=["markdown"],
    only_main_content=True,
    max_age=0
)

print(doc.markdown)
print(doc.metadata)
```

### With Retry for Protected Sites

```python
from firecrawl import Firecrawl
import os

app = Firecrawl(api_key=os.environ.get("FIRECRAWL_API_KEY"))

def scrape_with_retry(url: str) -> dict:
    try:
        doc = app.scrape(url, formats=["markdown"], max_age=0)
        return doc
    except Exception as e:
        if "403" in str(e) or "401" in str(e) or "cloudflare" in str(e).lower():
            doc = app.scrape(
                url,
                formats=["markdown"],
                max_age=0,
                proxy="stealth"
            )
            return doc
        raise
```

### Save to File with Metadata

```python
import os
from firecrawl import Firecrawl
from datetime import datetime
from pathlib import Path
import re

app = Firecrawl(api_key=os.environ.get("FIRECRAWL_API_KEY"))

def slugify(title: str) -> str:
    title = title.lower()
    title = re.sub(r'[^a-z0-9\s-]', '', title)
    title = re.sub(r'\s+', '-', title)
    words = title.split('-')
    if len(words) > 6:
        title = '-'.join(words[:6])
    return title.strip('-')

def save_scraped_content(url: str) -> str:
    doc = app.scrape(url, formats=["markdown"], only_main_content=True, max_age=0)
    
    domain = url.split('/')[2]
    title = doc.metadata.get('title', 'untitled')
    slug = slugify(title)
    
    output_dir = Path("scraped-content") / domain
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{slug}.md"
    
    if output_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = output_dir / f"{slug}-{timestamp}.md"
    
    frontmatter = f"""---
url: {url}
title: {title}
author: {doc.metadata.get('author', 'Unknown')}
published: {doc.metadata.get('publishedDate', 'Unknown')}
description: {doc.metadata.get('description', '')}
captured_at: {datetime.now().isoformat()}Z
---

{doc.markdown}
"""
    
    output_path.write_text(frontmatter)
    return str(output_path)

# Usage
path = save_scraped_content("https://example.com/article")
print(f"Saved to: {path}")
```

## Storage Pattern

```
scraped-content/<domain>/<slug>.md
```

- `<domain>`: Extracted from URL (e.g., `example.com`)
- `<slug>`: Page title → kebab-case, 2-6 words
- Conflict: Append timestamp `<slug>-YYYYMMDD-HHMMSS.md`

## Frontmatter Format

Every saved file includes YAML frontmatter:

```yaml
---
url: https://example.com/article
title: Article Title
author: Author Name
published: 2026-01-20
description: Article description
captured_at: 2026-02-25T15:30:00Z
---
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| DNS resolution failure | Invalid domain | Check URL, retry |
| Cloudflare/bot detection | Anti-scraping | Use `proxy="stealth"` |
| Timeout | Slow page | Increase `timeout` |
| Rate limit exceeded | Too many requests | Wait and retry |
| Empty content | JS not loaded | Add `wait_for` parameter |

## Common Issues

### Stealth Mode Pricing

Stealth mode costs **5 credits per request**. Only use it when basic scraping fails:

```python
# Default - auto retries with stealth only if needed
doc = app.scrape(url, formats=["markdown"])

# Or manually retry only on specific errors
try:
    doc = app.scrape(url, formats=["markdown"], proxy="basic")
except Exception as e:
    if e.status_code in [401, 403, 500]:
        doc = app.scrape(url, formats=["markdown"], proxy="stealth")
```

### Job Status Race Condition

When checking async jobs, wait 1-3 seconds before first status check:

```python
import time
job = app.start_crawl(url="https://example.com")
time.sleep(2)  # Wait before checking status
status = app.get_crawl_status(job.id)
```

## Firecrawl API Reference

- **Documentation**: https://docs.firecrawl.dev
- **Python SDK**: https://docs.firecrawl.dev/sdks/python
- **API Reference**: https://docs.firecrawl.dev/api-reference

## Notes

- Always use `max_age=0` for fresh scrapes (no cache)
- Use `only_main_content=True` to avoid navigation/sidebar clutter
- Validate URL format before scraping
- Check for existing files before writing to avoid overwrites
