---
name: fetch-x-posts
description: Fetch X (Twitter) posts and long-form Note Tweets, or sync all bookmarks, via the official X API v2 XDK and save as local markdown files with frontmatter.
license: MIT
---

# Fetch X Posts

Three scripts:

- `fetch_x_posts.py` -- fetch a single X post by URL.
- `auth_x.py` -- one-time OAuth 2.0 PKCE setup for bookmark sync.
- `sync_x_bookmarks.py` -- periodic sync of your X bookmarks.

No AI tokens consumed. All use the official X API v2 Python XDK.

## When to Use This Skill

Use when the user says:

- "save this X content: <url>"
- "fetch this post: <url>"
- "save this tweet: <url>"
- "download this X post: <url>"
- "save this article: <url>" (if it is an X Article or Note Tweet)
- "sync my bookmarks"
- "save my bookmarks"
- "back up my bookmarks"
- "mirror my X bookmarks"

Do NOT use for: external articles, blog posts, news sites. For those, delegate
to `firecrawl-web-scraper`.

## Requirements

- Python 3.11+ with `uv`
- `.env` file with one of:
  - `X_API_BEARER_TOKEN` (for single-post fetches)
  - `X_API_CLIENT_ID` and `X_API_CLIENT_SECRET` (OAuth 2.0, for bookmark sync)
- OAuth 2.0 redirect URI registered as `http://localhost:8080/callback`

## Workflow (Single Post)

1. Validate the URL matches the canonical pattern
   `x.com/{username}/status/{id}` or `twitter.com/{username}/status/{id}`.
   Reject anything that does not match exactly.

2. Decide the working directory for the output. Pass `--output-dir` or run
   from the directory where you want the file saved.

3. Run the script:

   ```bash
   cd skills/fetch-x-posts && uv run python fetch_x_posts.py <url>
   ```

   Or with an explicit output directory:

   ```bash
   cd skills/fetch-x-posts && uv run python fetch_x_posts.py <url> --output-dir ~/notes
   ```

4. Report the saved file path to the user. If an error occurs, display the
   error message.

## Workflow (Bookmark Sync)

### One-time authentication

1. Generate the authorization URL:

   ```bash
   cd skills/fetch-x-posts && uv run python auth_x.py --token-file ./x-bookmarks/.tokens.json
   ```

   This prints a URL and saves the PKCE verifier for the exchange step.

2. Open the URL in a browser, authorize the app.

3. After authorization, the browser redirects to
   `http://localhost:8080/callback?code=...` (page may fail to load
   -- avoid this). Copy the full URL from the address bar.

4. Exchange the code for tokens:

   ```bash
   cd skills/fetch-x-posts && uv run python auth_x.py --token-file ./x-bookmarks/.tokens.json --callback-url "<URL>"
   ```

### Sync

Once authenticated, run the sync from any directory:

```bash
cd skills/fetch-x-posts && uv run python sync_x_bookmarks.py
```

Options:
- `--output-dir DIR` (default `x-bookmarks/`)
- `--max-bookmarks N` (limit for testing, default 0 = unlimited)
- `--dry-run` (preview without saving)

The token auto-refreshes on each run. No re-authentication needed unless the
refresh token is revoked.

### Cron

```cron
0 9 * * * cd /path/to/skills/fetch-x-posts && uv run python sync_x_bookmarks.py --output-dir /path/to/x-bookmarks
```

Cost: ~$0.001 per new bookmark (Owned Reads pricing). Same bookmark within
24h UTC window is not charged again.

## Scope

In scope (single post):
- Canonical X/Twitter post URLs
- Long-form Note Tweets (full text returned via `note_tweet` field)
- X Articles (if `article` field is present on the post object)
- Media URLs (photos, videos, GIFs) listed in a Media section
- Referenced tweets (quotes, replies) listed in a References section

In scope (bookmark sync):
- All bookmarks (paginated, up to X API limits)
- Bookmark folder structure mirrored as local directories
- Media downloads per bookmark
- Append-only state file tracks processed tweet IDs
- Folder membership: each bookmark saved to its first folder only
- Uncategorized bookmarks go to `Uncategorized/`

Out of scope:
- Profile pages, timelines, search results
- Direct Messages
- External articles or blog posts
- Threads beyond the single post
- Batch multiple URLs (use bookmark sync or shell loop)

## Output

Single post: saved to the current working directory (or `--output-dir`) as
`{username}_{created_at}_{tweet_id}.md`.

Bookmark sync: saved under `--output-dir` (default `x-bookmarks/`) with the
folder structure mirroring X bookmark folders:

```
x-bookmarks/
├── Uncategorized/
├── Folder Name/
├── .sync-state.json
└── .tokens.json
```

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

- Both scripts use the official X API v2 XDK (`xdk`).
- Single post: Bearer Token auth (`X_API_BEARER_TOKEN`).
- Bookmark sync: OAuth 2.0 PKCE auth (`X_API_CLIENT_ID`, `X_API_CLIENT_SECRET`).
- `auth_x.py` persists the PKCE verifier to a sidecar file so the two-step
  auth flow (generate URL, exchange code) works across script invocations.
- Rate limits: exponential backoff with max 3 retries (both scripts).
- Non-canonical URLs are rejected with an error (single post).
- Bookmark sync is append-only: never deletes local files on reorganisation.
- State file `.sync-state.json` tracks processed tweet IDs for deduplication.
- Token file `.tokens.json` stores OAuth 2.0 tokens (auto-refreshed).
