---
name: jira-issues
description: Fetch Jira issue details and comments, save as markdown to workspace root
compatibility: opencode
---

## Trigger
When user asks to fetch a Jira issue (e.g., "get Jira issue ML-502" or "fetch TDT-2558")

## Steps

### 1. Find .env file
Search upward from current working directory to locate `.env`:

```bash
current_dir="$(pwd)"
env_file=""
while [[ "$current_dir" != "/" ]]; do
  if [[ -f "$current_dir/.env" ]]; then
    env_file="$current_dir/.env"
    break
  fi
  current_dir="$(dirname "$current_dir")"
done

if [[ -z "$env_file" ]]; then
  echo "Error: .env file not found in current directory or parents"
  exit 1
fi

echo "Found .env at: $env_file"
```

### 2. Load credentials
```bash
set +a
source "$env_file"
set -a
```

Verify required variables are set:
- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_KEY`

If any are missing, report: "Missing required Jira credentials in .env (JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_KEY)"

### 3. Fetch issue details
```bash
issue_key="{ISSUE_KEY}"
base_url="${JIRA_BASE_URL%/}"

# Fetch issue
curl -s -u "$JIRA_EMAIL:$JIRA_API_KEY" \
  -H "Accept: application/json" \
  "$base_url/rest/api/3/issue/$issue_key?fields=summary,description,status,assignee,created,updated,project"
```

Save response to variable: `issue_json`

### 4. Fetch comments
```bash
curl -s -u "$JIRA_EMAIL:$JIRA_API_KEY" \
  -H "Accept: application/json" \
  "$base_url/rest/api/3/issue/$issue_key/comment"
```

Save response to variable: `comments_json`

### 5. Parse and create markdown

Use jq to extract fields:

```bash
# Extract issue fields
summary=$(echo "$issue_json" | jq -r '.fields.summary // "No summary"')
status=$(echo "$issue_json" | jq -r '.fields.status.name // "Unknown"')
assignee=$(echo "$issue_json" | jq -r '.fields.assignee.displayName // "Unassigned"')
created=$(echo "$issue_json" | jq -r '.fields.created // ""')
updated=$(echo "$issue_json" | jq -r '.fields.updated // ""')
description_adf=$(echo "$issue_json" | jq '.fields.description')
project_key=$(echo "$issue_json" | jq -r '.fields.project.key // ""')
```

Convert ADF description to markdown:
- Type "paragraph" → text block
- Type "text" → inline text
- Skip other types for basic support

```bash
# Convert basic ADF to markdown
description_md=$(echo "$description_adf" | jq -r '
  if .type == "doc" then
    [.content[]? | select(.type == "paragraph") | 
      (.content // []) | map(select(.type == "text") | .text) | join("")
    ] | join("\n\n")
  else
    ""
  end
')
```

Format comments:
```bash
comments_md=$(echo "$comments_json" | jq -r '
  .comments // [] | map(
    "### " + (.author.displayName // "Unknown") + " - " + (.created // "") + "\n\n" +
    (if .body.type == "doc" then
      (.body.content // []) | map(select(.type == "paragraph") | 
        (.content // []) | map(select(.type == "text") | .text) | join("")
      ) | join("\n\n")
    else
      ""
    end)
  ) | join("\n\n")
')
```

### 6. Write markdown file

Create output at workspace root:

```bash
output_file="$(pwd)/{lowercase_issue_key}.md"

cat > "$output_file" << 'EOF'
# {ISSUE_KEY}: {SUMMARY}

**Status:** {STATUS}  
**Assignee:** {ASSIGNEE}  
**Created:** {CREATED}  
**Updated:** {UPDATED}

## Description

{DESCRIPTION}

## Comments

{COMMENTS}
EOF
```

### 7. Report success

Output:
- "Saved Jira issue {ISSUE_KEY} to {lowercase_issue_key}.md"
- Include file path
- Show summary and status

## Error Handling

If any curl command fails:
1. Show the raw curl error output
2. Report the HTTP status code if available
3. Suggest checking:
   - .env file exists and has correct credentials
   - JIRA_BASE_URL is correct
   - Issue key is valid and accessible
   - Network connectivity

## Example Usage

User: "Get Jira issue ML-502"

Agent:
1. Find .env at `/Users/user/project/.env`
2. Load credentials
3. curl to fetch ML-502
4. curl to fetch comments
5. Create `ml-502.md` with formatted content
6. Report: "Saved Jira issue ML-502 to ml-502.md"

## Output Format Example (ml-502.md)

```markdown
# ML-502: Implement feature X

**Status:** In Progress  
**Assignee:** John Doe  
**Created:** 2024-03-15T10:30:00.000+0000  
**Updated:** 2024-03-22T14:22:00.000+0000

## Description

This feature needs to handle large datasets efficiently.
We should use batching to avoid memory issues.

## Comments

### Jane Smith - 2024-03-20T09:15:00.000+0000

Have you considered using streaming instead of batch loading?

### John Doe - 2024-03-21T16:45:00.000+0000

Good idea, I'll implement that approach.
```
