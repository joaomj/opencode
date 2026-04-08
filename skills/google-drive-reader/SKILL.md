---
name: google-drive-reader
description: Read and fetch content from Google Drive files via Google Drive API with OAuth desktop app auth. Supports Google Docs (markdown), Sheets (CSV), and generic file downloads.
license: MIT
compatibility: opencode
---

# Google Drive Reader

Read content from your corporate Google Drive account. Read-only access via OAuth 2.0 desktop app flow.

## Triggers

| User says | Action |
|-----------|--------|
| "read drive file" / "fetch from drive" / "read google doc" | `drive_reader.py read <file-id-or-url>` |
| "list drive files" / "search drive" / "find drive file" | `drive_reader.py list <query>` |
| "read google sheet" / "export sheet" | `drive_reader.py read <url>` |

## Workflow

### Setup: First-time Authentication

Before first use, the user must create OAuth credentials:

1. Go to `console.cloud.google.com` and create a new project (any user can do this)
2. Enable the **Google Drive API** in the project
3. Configure the **OAuth consent screen**:
   - User type: **External**
   - In testing mode (unverified is fine for personal/corporate use, up to 100 users)
4. Create **OAuth 2.0 Desktop app** credentials
5. Store `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env` in the skill directory
6. First invocation opens a browser for consent -- authorize with your corporate Google account
7. `token.json` is saved locally and auto-refreshed

### Setup: Venv Detection

When first using the skill, check for a Python virtual environment.

**Search order:**
1. `$HOME/.config/opencode/skills/google-drive-reader/.venv`
2. `.venv` in current directory
3. `venv` in current directory

If not found, create `.venv` in `$HOME/.config/opencode/skills/google-drive-reader/.venv` and install dependencies:

```bash
python3 -m venv $HOME/.config/opencode/skills/google-drive-reader/.venv
source $HOME/.config/opencode/skills/google-drive-reader/.venv/bin/activate
pip install google-auth-oauthlib google-api-python-client
```

**To activate venv before running scripts:**
```bash
source $HOME/.config/opencode/skills/google-drive-reader/.venv/bin/activate
```

---

### Read File

**Trigger:** "read drive file", "fetch from drive", "read google doc"

**Command:**
```bash
$HOME/.config/opencode/skills/google-drive-reader/.venv/bin/python \
  $HOME/.config/opencode/skills/google-drive-reader/drive_reader.py read <file-id-or-url>
```

**Accepts:** Google Drive file URL or file ID.

Supported URL formats:
- `https://docs.google.com/document/d/<ID>/edit`
- `https://docs.google.com/spreadsheets/d/<ID>/edit`
- `https://drive.google.com/file/d/<ID>/view`
- `https://drive.google.com/open?id=<ID>`
- Raw file ID string

**What it does:**
1. Loads credentials from `.env` and `token.json`
2. Fetches file metadata (name, mime type, modified time)
3. Exports based on type:
   - Google Docs (`application/vnd.google-apps.document`) -> markdown
   - Google Sheets (`application/vnd.google-apps.spreadsheet`) -> CSV
   - Google Slides (`application/vnd.google-apps.presentation`) -> plain text
   - Other files -> downloads raw content
4. Saves to `.gdrive/<filename>` in current directory

**Options:**
| Flag | Description |
|------|-------------|
| `--output` | Custom output file path |
| `--format` | Override export format (markdown, csv, txt, pdf) |

---

### List/Search Files

**Trigger:** "list drive files", "search drive", "find drive file"

**Command:**
```bash
$HOME/.config/opencode/skills/google-drive-reader/.venv/bin/python \
  $HOME/.config/opencode/skills/google-drive-reader/drive_reader.py list "name contains 'report'"
```

**What it does:**
1. Searches Drive using Google Drive query syntax
2. Lists results: file name, type, last modified, ID

**Options:**
| Flag | Description |
|------|-------------|
| `--max-results` | Max results (default: 20) |
| `--folder` | Restrict to a folder ID |
| `--mime-type` | Filter by MIME type |

---

## Requirements

- `.env` file in skill directory (`~/.config/opencode/skills/google-drive-reader/`) with:
  ```
  GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET=your-client-secret
  ```
- Python 3.11+
- Dependencies: `google-auth-oauthlib`, `google-api-python-client`

Note: Credentials are loaded from `.env` programmatically -- never logged or displayed per OC002.

## Output Formats

### Read Output
- `.gdrive/<sanitized-filename>.md` (Google Docs)
- `.gdrive/<sanitized-filename>.csv` (Google Sheets)
- `.gdrive/<sanitized-filename>.txt` (Google Slides)
- `.gdrive/<sanitized-filename>.<ext>` (other files)

Output directory `.gdrive/` is created automatically. Add `.gdrive/` to `.gitignore`.

### List Output (stdout)
- One line per file: `<name> | <type> | <modified> | <id>`

## Error Handling

| Error | Resolution |
|-------|------------|
| "Missing credentials" | Set GOOGLE_CLIENT_ID/SECRET in skill .env |
| "Token expired or revoked" | Delete token.json, re-auth via browser |
| "Access denied for file" | Check file sharing permissions in Drive |
| "Google API 403" | Consent screen may need publishing, or admin blocks external apps |
| "This app isn't verified" | Click Advanced -> Go to app (unsafe) -- normal for unverified external apps |

## Limitations

- Read-only (no write, create, or delete operations)
- No shared drive traversal (can be added later)
- No recursive folder listing (can be added later)
- Token refresh requires browser interaction if refresh token expires (rare)
