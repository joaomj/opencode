# OpenCode Auto-Update Setup Guide

This guide configures your shell to automatically sync `~/.config/opencode` from your remote repository every time you start OpenCode.

## What It Does

When you type `opencode`:
1. Syncs `~/.config/opencode` from `origin/master` (remote overwrites local)
2. Launches OpenCode in your current working directory

## Prerequisites

- OpenCode installed and accessible in your PATH
- Git configured with access to `https://github.com/joaomj/opencode.git`
- `~/.config/opencode` directory exists

## Step-by-Step Setup

### Step 1: Identify Your Shell

Run this command to see which shell you're using:

```bash
echo $SHELL
```

- If output contains `bash` → proceed with `.bashrc`
- If output contains `zsh` → proceed with `.zshrc`

### Step 2: Open Your Shell Configuration File

**For Linux (Ubuntu/Debian):**

```bash
nano ~/.bashrc
```

**For macOS:**

```bash
nano ~/.zshrc
```

Or use your preferred text editor (`vim`, `code`, etc.)

### Step 3: Add the OpenCode Wrapper Function

Add this function to the **end** of your configuration file:

```bash
# OpenCode with auto-update from remote repository
opencode() {
    (
        cd "$HOME/.config/opencode" 2>/dev/null || exit 0
        echo "[OpenCode Sync] Fetching remote changes (local files will be overwritten)..."
        git fetch origin master 2>/dev/null || echo "[OpenCode Sync] Warning: Could not fetch from remote"
        git reset --hard origin/master 2>/dev/null || echo "[OpenCode Sync] Warning: Could not reset to remote"
    )
    echo "[OpenCode Sync] Starting OpenCode..."
    command opencode "$@"
}
```

### Step 4: Ensure OpenCode is in Your PATH

Make sure OpenCode binary is accessible. Add this line **before** the function if needed:

```bash
export PATH="$HOME/.opencode/bin:$PATH"
```

**Platform-specific paths:**

| OS | Typical OpenCode Path |
|----|---------------------|
| Linux | `$HOME/.opencode/bin` |
| macOS (Homebrew) | `/opt/homebrew/bin` or `/usr/local/bin` |
| macOS (direct install) | `$HOME/.opencode/bin` |

### Step 5: Save and Reload Shell Configuration

Save the file (in nano: `Ctrl+O`, `Enter`, `Ctrl+X`), then reload:

```bash
# For Linux (Bash)
source ~/.bashrc

# For macOS (Zsh)
source ~/.zshrc
```

Or simply open a new terminal window.

### Step 6: Verify the Setup

Test that the wrapper is active:

```bash
type opencode
```

**Expected output:**
```
opencode is a function
opencode () 
{ 
    ( cd "$HOME/.config/opencode" 2> /dev/null || exit 0;
    echo "[OpenCode Sync] Fetching remote changes (local files will be overwritten)...";
    git fetch origin master 2> /dev/null || echo "[OpenCode Sync] Warning: Could not fetch from remote";
    git reset --hard origin/master 2> /dev/null || echo "[OpenCode Sync] Warning: Could not reset to remote" );
    echo "[OpenCode Sync] Starting OpenCode...";
    command opencode "$@"
}
```

### Step 7: Test Auto-Update

Run OpenCode from any directory:

```bash
opencode
```

**You should see:**
```
[OpenCode Sync] Fetching remote changes (local files will be overwritten)...
[OpenCode Sync] Starting OpenCode...
```

Then OpenCode starts in your current directory (not in `~/.config/opencode`).

## OS-Specific Notes

### Linux (Ubuntu/Debian)

- Uses `~/.bashrc` by default
- Git is usually pre-installed
- No special considerations

### macOS

- Modern macOS uses Zsh by default (`~/.zshrc`)
- If you installed OpenCode via Homebrew, the path might differ:
  ```bash
  which opencode
  # Output: /opt/homebrew/bin/opencode
  ```
- If using older macOS (< 10.15), you might be using Bash (`~/.bash_profile` instead of `~/.bashrc`)

## How It Works

1. **Subshell isolation**: The parentheses `(...)` create a subshell, so `cd` doesn't affect your current directory
2. **Silent failures**: `2>/dev/null` suppresses error output for cleaner startup
3. **Remote wins**: `git reset --hard origin/master` forces remote state, discarding local changes
4. **Preserves working directory**: OpenCode launches from where you invoked it

## Important Warnings

⚠️ **Destructive behavior**: Any tracked changes you make in `~/.config/opencode` will be **permanently lost** every time you run `opencode`.

⚠️ **No local commits**: Do not commit changes in `~/.config/opencode` on this machine. Always push changes from another machine to the remote repository.

## Rollback / Disable Auto-Update

To remove the auto-update behavior and use plain OpenCode:

### Option A: Use Original Binary (Temporary)

```bash
command opencode
```

### Option B: Remove the Wrapper (Permanent)

1. Open your shell config:
   ```bash
   # Linux
   nano ~/.bashrc
   
   # macOS
   nano ~/.zshrc
   ```

2. Find and delete the `opencode()` function (lines starting with `opencode() {` through the closing `}`)

3. Save and reload:
   ```bash
   source ~/.bashrc  # or source ~/.zshrc
   ```

## Troubleshooting

### "opencode is /usr/bin/opencode" (or similar path)

The wrapper isn't loaded. Check:
1. Did you save the file?
2. Did you run `source` on the correct file?
3. Are you editing the right config file for your shell?

### "[OpenCode Sync] Warning: Could not fetch from remote"

- Check internet connection
- Verify you have access to `https://github.com/joaomj/opencode.git`
- Ensure `~/.config/opencode` is a valid git repository with remote set:
  ```bash
  cd ~/.config/opencode
  git remote -v
  ```

### OpenCode starts in ~/.config/opencode instead of current directory

The subshell isolation isn't working. Check that your function uses parentheses `(...)` not braces `{...}` for the cd section.

## Customization

### Change Remote Repository

Edit the function and replace:
```bash
git fetch origin master
```
with:
```bash
git fetch <remote-name> <branch-name>
```

### Add Logging

To see detailed git output, remove the `2>/dev/null` redirects:

```bash
opencode() {
    (
        cd "$HOME/.config/opencode" || exit 0
        echo "[OpenCode Sync] Fetching remote changes..."
        git fetch origin master || echo "Warning: fetch failed"
        git reset --hard origin/master || echo "Warning: reset failed"
    )
    echo "[OpenCode Sync] Starting OpenCode..."
    command opencode "$@"
}
```

---

**Tested on**: Ubuntu 24.04 LTS, macOS Tahoe
