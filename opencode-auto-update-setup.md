# OpenCode Auto-Update Setup Guide

This guide configures your shell to automatically sync `~/.config/opencode` from your remote repository while preserving local customizations.

## What It Does

When you type `opencode`:
1. Preserves local `AGENTS.md` and `opencode.json`
2. Fetches remote changes and merges them (appends new content to existing files)
3. Restores your local `AGENTS.md` and `opencode.json`
4. Launches OpenCode in your current working directory

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
        
        PRESERVED_FILES="AGENTS.md opencode.json"
        
        for file in $PRESERVED_FILES; do
            if [ -f "$file" ]; then
                cp "$file" "$file.local.bak"
            fi
        done
        
        echo "[OpenCode Sync] Fetching remote changes..."
        git fetch origin master 2>/dev/null || echo "[OpenCode Sync] Warning: Could not fetch from remote"
        
        for remote_file in $(git ls-tree -r --name-only origin/master); do
            if echo "$PRESERVED_FILES" | grep -qw "$remote_file"; then
                continue
            fi
            
            local_file="./${remote_file}"
            if [ -f "$local_file" ]; then
                remote_content=$(git show "origin/master:${remote_file}" 2>/dev/null)
                if [ -n "$remote_content" ]; then
                    printf '\n\n' >> "$local_file"
                    printf '%s\n' "$remote_content" >> "$local_file"
                fi
            else
                mkdir -p "$(dirname "$local_file")"
                git checkout "origin/master" -- "$remote_file" 2>/dev/null
            fi
        done
        
        for file in $PRESERVED_FILES; do
            if [ -f "$file.local.bak" ]; then
                mv "$file.local.bak" "$file"
                echo "[OpenCode Sync] $file preserved"
            fi
        done
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
    PRESERVED_FILES="AGENTS.md opencode.json";
    for file in $PRESERVED_FILES; do
        if [ -f "$file" ]; then
            cp "$file" "$file.local.bak";
        fi;
    done;
    echo "[OpenCode Sync] Fetching remote changes...";
    git fetch origin master 2> /dev/null || echo "[OpenCode Sync] Warning: Could not fetch from remote";
    for remote_file in $(git ls-tree -r --name-only origin/master); do
        if echo "$PRESERVED_FILES" | grep -qw "$remote_file"; then
            continue;
        fi;
        local_file="./${remote_file}";
        if [ -f "$local_file" ]; then
            remote_content=$(git show "origin/master:${remote_file}" 2>/dev/null);
            if [ -n "$remote_content" ]; then
                printf '\n\n' >> "$local_file";
                printf '%s\n' "$remote_content" >> "$local_file";
            fi;
        else
            mkdir -p "$(dirname "$local_file")";
            git checkout "origin/master" -- "$remote_file" 2>/dev/null;
        fi;
    done;
    for file in $PRESERVED_FILES; do
        if [ -f "$file.local.bak" ]; then
            mv "$file.local.bak" "$file";
            echo "[OpenCode Sync] $file preserved";
        fi;
    done );
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
[OpenCode Sync] Fetching remote changes...
[OpenCode Sync] AGENTS.md preserved
[OpenCode Sync] opencode.json preserved
[OpenCode Sync] Starting OpenCode...
```

If you don't have a local `opencode.json`, you'll only see:
```
[OpenCode Sync] Fetching remote changes...
[OpenCode Sync] AGENTS.md preserved
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
2. **Local backup**: Backs up `AGENTS.md` and `opencode.json` to `.local.bak` files
3. **Silent failures**: `2>/dev/null` suppresses error output for cleaner startup
4. **Merge strategy**: For existing files, appends remote content; for new files, checks them out
5. **Preserve local**: Restores backed-up `AGENTS.md` and `opencode.json` after merge
6. **Preserves working directory**: OpenCode launches from where you invoked it

## Important Notes

✅ **AGENTS.md preserved**: Your local AGENTS.md is backed up and restored after sync.

✅ **opencode.json preserved**: Your local opencode.json is backed up and restored after sync.

⚠️ **Merge, not replace**: Remote changes are appended to existing files (except preserved ones), not wholesale replaced.

⚠️ **No marker needed**: Unlike the previous approach, the entire file is preserved - no marker required.

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

Edit the function and replace `origin master` with your remote and branch:
```bash
git fetch <remote-name> <branch-name>
```

### Add Logging

To see detailed git output, remove the `2>/dev/null` redirects:

```bash
opencode() {
    (
        cd "$HOME/.config/opencode" || exit 0
        
        PRESERVED_FILES="AGENTS.md opencode.json"
        
        for file in $PRESERVED_FILES; do
            if [ -f "$file" ]; then
                cp "$file" "$file.local.bak"
            fi
        done
        
        echo "[OpenCode Sync] Fetching remote changes..."
        git fetch origin master || echo "Warning: fetch failed"
        
        for remote_file in $(git ls-tree -r --name-only origin/master); do
            if echo "$PRESERVED_FILES" | grep -qw "$remote_file"; then
                continue
            fi
            
            local_file="./${remote_file}"
            if [ -f "$local_file" ]; then
                remote_content=$(git show "origin/master:${remote_file}" 2>/dev/null)
                if [ -n "$remote_content" ]; then
                    printf '\n\n' >> "$local_file"
                    printf '%s\n' "$remote_content" >> "$local_file"
                fi
            else
                mkdir -p "$(dirname "$local_file")"
                git checkout "origin/master" -- "$remote_file"
            fi
        done
        
        for file in $PRESERVED_FILES; do
            if [ -f "$file.local.bak" ]; then
                mv "$file.local.bak" "$file"
                echo "[OpenCode Sync] $file preserved"
            fi
        done
    )
    echo "[OpenCode Sync] Starting OpenCode..."
    command opencode "$@"
}
```

### Add More Preserved Files

To preserve additional files, edit the `PRESERVED_FILES` variable:

```bash
PRESERVED_FILES="AGENTS.md opencode.json custom-config.yml secrets.json"
```

---

**Tested on**: Ubuntu 24.04 LTS, macOS Tahoe
