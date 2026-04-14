---
name: jira-issues
description: Fetch, create, and search Jira issues using Atlassian CLI (acli). ADF descriptions/comments are rendered to markdown by the LLM.
compatibility: opencode
---

## Triggers

| User says | Command invoked |
|-----------|----------------|
| "get issue ML-502" / "fetch PROJ-123" | `acli jira workitem view <key>` |
| "create jira issue" / "/create-jira" | `acli jira workitem create` |
| "search jira" / "jira search" | `acli jira workitem search --jql` |
| "list comments ML-511" / "fetch comments" | `acli jira workitem comment list <key>` |

---

## Authentication

Before any Jira operation, check if `acli` is already authenticated:

```bash
acli jira workitem search --jql "assignee = currentUser()" --limit 1
```

**If it returns results:** `acli` is authenticated. Proceed with the command.

**If it returns "Authentication required" or similar error:**
1. Check if the **project's `.env`** file exists in the repo root:
   ```
   .env
   ```
   The file should contain:
   ```
   JIRA_BASE_URL=https://yourcompany.atlassian.net
   JIRA_EMAIL=your.email@company.com
   JIRA_API_KEY=your_api_token_here
   ```
2. If the `.env` exists, authenticate using those credentials:
   ```bash
   # Parse .env and login (do NOT echo the actual token value -- use the variable)
   JIRA_API_KEY=$(grep '^JIRA_API_KEY=' .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
   JIRA_BASE_URL=$(grep '^JIRA_BASE_URL=' .env | cut -d'=' -f2- | tr -d '"' | tr -d "'" | sed 's|https://||' | sed 's|/.*||')
   JIRA_EMAIL=$(grep '^JIRA_EMAIL=' .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
   echo "$JIRA_API_KEY" | acli jira auth login --site "$JIRA_BASE_URL" --email "$JIRA_EMAIL" --token
   ```
3. If the `.env` does **not** exist, show the user these commands to run first:

   **Step 1 -- Install acli:**
   ```bash
   brew tap atlassian/homebrew-acli && brew install acli
   ```

   **Step 2 -- Create a `.env` file in your project root** with:
   ```
   JIRA_BASE_URL=https://yourcompany.atlassian.net
   JIRA_EMAIL=your.email@company.com
   JIRA_API_KEY=your_api_token_here
   ```

   **Step 3 -- Authenticate:**
   ```bash
   JIRA_API_KEY=$(grep '^JIRA_API_KEY=' .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
   JIRA_BASE_URL=$(grep '^JIRA_BASE_URL=' .env | cut -d'=' -f2- | tr -d '"' | tr -d "'" | sed 's|https://||' | sed 's|/.*||')
   JIRA_EMAIL=$(grep '^JIRA_EMAIL=' .env | cut -d'=' -f2- | tr -d '"' | tr -d "'")
   echo "$JIRA_API_KEY" | acli jira auth login --site "$JIRA_BASE_URL" --email "$JIRA_EMAIL" --token
   ```

   **Step 4 -- Verify:**
   ```bash
   acli jira workitem search --jql "assignee = currentUser()" --limit 1
   ```

---

## Fetch Issue

**Trigger:** "get issue ML-502" or "fetch PROJ-123"

**Workflow:**
1. Ensure `acli` is authenticated (see Authentication section).
2. Run: `acli jira workitem view <KEY> --json --fields key,issuetype,summary,status,assignee,description,created,updated,priority,labels,components,comment`
3. Parse the JSON response.
4. Convert ADF description and comments to markdown (see ADF Rendering section).
5. Write issue details to `{key.lower()}.md` in the current directory.

**Fetch command:**
```bash
acli jira workitem view <KEY> --json --fields key,issuetype,summary,status,assignee,description,created,updated,priority,labels,components,comment
```

**Output file format (`{key}.md`):**
```markdown
# KEY: Summary

| Field | Value |
|-------|-------|
| **Type** | Story |
| **Status** | In Progress |
| **Priority** | High |
| **Assignee** | Joao Marcos |
| **Created** | 2025-03-15 |
| **Updated** | 2025-04-10 |
| **Labels** | ml, backend |
| **Components** | API |

---

## Description

[ADF rendered as markdown]

---

## Comments

### Author - 2025-04-10

Comment body rendered as markdown.

---
```

---

## Create Issue

**Trigger:** "create jira issue" or "/create-jira"

**Workflow:**
1. Ensure `acli` is authenticated (see Authentication section).
2. Ask the user for required fields: `project key` and `summary`.
3. Ask for optional fields: `description`, `type` (default: Story), `labels`, `assignee`.
4. Run the create command.
5. Report the created issue key.

**Non-interactive (all flags):**
```bash
acli jira workitem create \
  --project <PROJECT_KEY> \
  --summary "Issue summary" \
  --type Story \
  --description "Description text" \
  --label ml --label backend \
  --yes
```

**Options:**
| Flag | Description |
|------|-------------|
| `--project KEY` | Jira project key (required) |
| `--summary "text"` | Issue summary (required) |
| `--type Story` | Issue type: Epic, Story, Task, Bug (default: Story) |
| `--description "text"` | Description text (plain text) |
| `--label x --label y` | Labels (repeat for multiple) |
| `--assignee x` | Assign to user (account ID, email, or @me for self) |
| `--yes` | Skip confirmation |

---

## Search Issues

**Trigger:** "search jira" or "jira search"

**Command:**
```bash
acli jira workitem search --jql "project = MYPROJ AND status = Open" --limit 50 --json
```

**Options:**
| Flag | Description |
|------|-------------|
| `--jql "JQL"` | JQL query (required) |
| `--limit N` | Max results (default: 50) |
| `--fields x,y,z` | Fields to display |
| `--csv` | Output as CSV |
| `--json` | Output as JSON |
| `--paginate` | Fetch all pages |

---

## List Comments

**Trigger:** "list comments ML-511" or "fetch comments"

**Command:**
```bash
acli jira workitem comment list --key <KEY> --json --limit 50
```

**Workflow:**
1. Ensure `acli` is authenticated.
2. Run the command above.
3. Render each comment's `body` (ADF) as markdown.
4. Output the comments in the conversation (not as a file).

---

## Editing (ASK BEFORE DOING)

**Trigger:** "edit ML-511" or "update issue ML-511"

**IMPORTANT: ALWAYS ask the user for confirmation before running any edit command. Never edit Jira issues without explicit user approval.**

Editing includes: changing summary, description, assignee, adding comments.

**Workflow:**
1. State clearly what you intend to do (e.g., "I will change the status of ML-511 from 'In Progress' to 'Done'").
2. Wait for the user to explicitly say "yes" or "go ahead".
3. If the user says no or asks to modify, update the plan and re-confirm.
4. Only run the command after explicit approval.

**Common edit commands:**
```bash
# Change summary
acli jira workitem edit --key <KEY> --summary "New summary"

# Change status (transition)
acli jira workitem transition --key <KEY> --status "Done"

# Add comment
acli jira workitem comment create --key <KEY> --body "Comment text"

# Change assignee
acli jira workitem assign --key <KEY> --assignee user@email.com
```

---

## ADF Rendering

When fetching or listing comments, the `description` and `comment.body` fields contain Atlassian Document Format (ADF) -- structured JSON.

**LLM rendering rules:**

| ADF node type | Markdown output |
|---------------|-----------------|
| `paragraph` | text (no prefix) |
| `heading` (attrs.level=N) | `#` x N + space + content |
| `bulletList` / `listItem` | `- ` prefix per item |
| `orderedList` / `listItem` | `1.` prefix per item |
| `codeBlock` (attrs.language) | triple backtick + language |
| `blockquote` | `> ` prefix per line |
| `rule` | `---` |
| `table` | pipe table syntax |
| `text` (marks: strong) | `**text**` |
| `text` (marks: em) | `*text*` |
| `text` (marks: code) | `` `text` `` |
| `text` (marks: strike) | `~~text~~` |
| `text` (marks: link) | `[text](href)` |
| `text` (marks: underline) | `<u>text</u>` |
| `emoji` (attrs.shortName) | rendered emoji |
| `mention` (attrs.userName) | `@userName` |
| `hardBreak` | newline |
| `status` (attrs.text) | `` `text` `` |

**Composite example:**
```json
{"type":"doc","content":[
  {"type":"heading","attrs":{"level":2},"content":[{"type":"text","text":"Title"}]},
  {"type":"paragraph","content":[
    {"type":"text","text":"Hello "},
    {"type":"text","marks":[{"type":"strong"}],"text":"world"}
  ]}
]}
```
Renders as:
```markdown
## Title

Hello **world**
```

---

## Error Handling

| Error | Resolution |
|-------|------------|
| "Authentication required" | See Authentication section above |
| "work item not found" | Check the issue key is correct |
| "permission denied" | Your account lacks permission |
| ".env not found" | Create a `.env` in the project root -- see Authentication section |
| "unknown flag" | Update acli: `brew upgrade acli` |
