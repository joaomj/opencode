---
name: google-drive-files
description: Google Drive file uploads and downloads through rclone. Use when the user asks to list, upload, or download files or folders from their personal Google Drive.
license: MIT
compatibility: opencode
---

# Google Drive Files

Upload, download, and list files on personal Google Drive via rclone. Google Drive API access requires a Google Cloud project to create OAuth credentials. rclone eliminates the need to write any transfer logic -- it handles authentication, resumable uploads, retries, progress reporting, and checksum verification.

## Safety Boundary

- Only `copyto` (single file) and `copy` (directory contents) are allowed. No `sync`, `delete`, `deletefile`, `purge`, `cleanup`, `move`, `mount`, `serve`, or `rc`.
- Do not run `rclone config show`, `rclone config dump`, or read the rclone config file -- it contains OAuth tokens.
- Check whether the destination path exists before writing. If it does, ask the user to confirm overwrite.
- Quote all local and remote paths.
- Treat any nonzero rclone exit status as a failure and report it to the user.

## Requirements

- `rclone` installed (`brew install rclone`).
- A configured remote named `gdrive` with scope `drive` (full access to all files).
- A custom OAuth client_id and client_secret from Google Cloud Console.

## One-Time GCP Setup

Steps 1-5 are done once in the Google Cloud Console. Steps 6+ are done in rclone.

1. Go to `https://console.cloud.google.com/projectcreate` and create a project.
2. Enable the Google Drive API at `https://console.cloud.google.com/apis/library/drive.googleapis.com`.
3. Go to `https://console.cloud.google.com/apis/credentials/consent`:
   - Choose "External", click Create.
   - Fill in App name (e.g. "rclone"), User support email, Developer contact email.
   - Save and Continue through Scopes.
   - Under Test Users, click "Add Users" and add your own Gmail address.
   - Save and Continue, then Back to Dashboard.
4. Go to `https://console.cloud.google.com/apis/credentials`:
   - Click "+ Create Credentials" > OAuth client ID.
   - Application type: "Desktop app".
   - Name: anything (e.g. "rclone").
   - Click Create and copy the client_id and client_secret.
5. Store the credentials in `.env`:
   ```
   GOOGLE_CLIENT_ID=<your-client-id>
   GOOGLE_CLIENT_SECRET=<your-client-secret>
   ```

## One-Time rclone Setup

`rclone listremotes` prints configured remotes. If `gdrive:` is absent, configure it:

```bash
source .env
rclone config create gdrive drive scope=drive client_id="$GOOGLE_CLIENT_ID" client_secret="$GOOGLE_CLIENT_SECRET"
```

This opens a browser to authenticate. On a headless machine, answer `n` when asked about browser auth -- rclone prints a URL. Open it in any browser, authorize, paste the verification code back.

Answer `n` to Shared Drive (Team Drive).

Resume the user's request only after `gdrive:` appears in `rclone listremotes`.

## Operations

### List a directory

```bash
rclone lsf "gdrive:<path>" --max-depth 1
```

For more detail (size, modtime):

```bash
rclone lsl "gdrive:<path>"
```

### Check if a destination path exists

```bash
rclone lsjson --stat "gdrive:<path>"
```

### Upload one file

Use `copyto` when both source and destination are single file paths:

```bash
rclone copyto "<local-path>" "gdrive:<remote-path>" --progress --no-traverse
```

`--no-traverse` avoids an unnecessary directory listing on large remotes.

### Upload a directory

Use `copy` to transfer the **contents** of a local directory into a remote directory:

```bash
rclone copy "<local-dir>" "gdrive:<remote-dir>" --progress
```

### Download one file

```bash
rclone copyto "gdrive:<remote-path>" "<local-path>" --progress
```

### Download a directory

```bash
rclone copy "gdrive:<remote-dir>" "<local-dir>" --progress
```

## Examples

| Request | Command |
|---|---|
| Upload `report.pdf` to Drive root | `rclone copyto "./report.pdf" "gdrive:report.pdf" --progress --no-traverse` |
| Upload `photos/` to `Backups/photos` | `rclone copy "./photos" "gdrive:Backups/photos" --progress` |
| Download `Notes/ideas.txt` | `rclone copyto "gdrive:Notes/ideas.txt" "./ideas.txt" --progress` |
| Download `Presentations/` | `rclone copy "gdrive:Presentations" "./Presentations" --progress` |
| List root | `rclone lsf "gdrive:" --max-depth 1` |
| List a subfolder | `rclone lsf "gdrive:Documents" --max-depth 1` |

## Why rclone Over Raw Google API

Every tool that accesses Google Drive requires OAuth credentials from a GCP project. rclone's value is not avoiding GCP -- it is handling all transfer complexity after the one-time setup:

- Resumable uploads and downloads
- Automatic token refresh with retry and backoff
- Progress reporting
- Checksum comparison to skip identical files
- Parallel transfers
- Resume interrupted transfers by re-running the same command
- Single binary, zero runtime dependencies

## Notes

- `rclone copy` transfers directory **contents**, not the directory itself (same as rsync trailing-slash behaviour).
- `copyto` always writes to an explicit file path -- useful for single files and renaming during transfer.
- The `drive` scope grants full read/write access to every file in the user's Drive, including files created outside rclone.
- Google Drive has a 750 GiB/day undocumented upload limit and a 10 TiB/day download limit. rclone surfaces these as errors.
- rclone's shared client_id was retired in 2026. Using a custom client_id is required.

## Out of Scope

- Deleting, moving, renaming, sharing, or changing permissions.
- Google Shared Drives.
- Google Docs export/import.
- Continuous sync or bidirectional sync.
- Mounting Drive as a filesystem.
- Exposing Drive through an MCP server, HTTP serve, or remote control.
- Reading the rclone config file or dumping tokens.
