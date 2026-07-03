---
name: fetch-x-posts
description: Fetch X (Twitter) posts and long-form Note Tweets via the official X API v2 XDK and save them as local markdown files with frontmatter.
license: MIT
---

# Fetch X Posts

Fetch a single X post by URL, save it as a markdown file with full body text
(including long-form Note Tweets), media links, references, and public metrics.

No AI tokens consumed. Uses the official X API v2 Python XDK.

## When to Use This Skill

Use when the user says:

- "save this X content: <url>"
- "fetch this post: <url>"
- "save this tweet: <url>"
- "download this X post: <url>"
- "save this article: <url>" (if it is an X Article or Note Tweet)

Do NOT use for: external articles, blog posts, news sites. For those, delegate
to `firecrawl-web-scraper`.

## Requirements

- `X_API_BEARER_TOKEN` in `.env` (at `~/.config/opencode/.env`)
- Python 3.11+ with `uv`

## Workflow

1. Validate the URL matches the canonical pattern
   `x.com/{username}/status/{id}` or `twitter.com/{username}/status/{id}`.
   Reject anything that does not match exactly.

2. Decide the working directory for the output. Run the script from the
   directory where you want the markdown file saved, or pass `--output-dir`.

3. Run the script:

   ```bash
   uv run skills/fetch-x-posts/fetch_x_posts.py <url>
   ```

   Or with an explicit output directory:

   ```bash
   uv run skills/fetch-x-posts/fetch_x_posts.py <url> --output-dir ~/notes
   ```

4. Report the saved file path to the user. If an error occurs, display the
   error message.

## Scope

In scope:
- Canonical X/Twitter post URLs
- Long-form Note Tweets (full text returned via `note_tweet` field)
- X Articles (if `article` field is present on the post object)
- Media URLs (photos, videos, GIFs) listed in a Media section
- Referenced tweets (quotes, replies) listed in a References section

Out of scope:
- Profile pages, timelines, search results
- Direct Messages
- External articles or blog posts
- Threads beyond the single post
- Batch multiple URLs (use a loop in shell if needed)

## Output

The markdown file is written to the current working directory (or
`--output-dir`) with the filename `{username}_{created_at}_{tweet_id}.md`.

### Frontmatter

```yaml
---
url: https://x.com/username/status/123
author: username
created_at: 2026-06-28T20:40:00.000Z
tweet_id: 2071332811001262335
fetched_at: 2026-07-03T17:30:00.000000+00:00
---
```

### Body

- Full text from `note_tweet.text` (if present) or `text`.
- Media section with embedded images (downloaded to `{filename}_media/`).
- References section with quoted/replied-to tweet links.

## Notes

- The script uses the official X API v2 XDK (`pip install xdk`).
- Authentication is via Bearer Token from `.env`.
- Rate limits: exponential backoff with max 3 retries.
- Non-canonical URLs are rejected with an error.
