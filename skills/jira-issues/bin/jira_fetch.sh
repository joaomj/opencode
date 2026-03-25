#!/bin/bash
# Fetch Jira issue and save as markdown

set -a && source .env && set +a

issue_key="${1:-TDT-2554}"
base_url="${JIRA_BASE_URL%/}"

echo "Fetching $issue_key..."

# Fetch issue
issue_json=$(curl -s -u "$JIRA_EMAIL:$JIRA_API_KEY" \
  -H "Accept: application/json" \
  "$base_url/rest/api/3/issue/$issue_key?fields=summary,description,status,assignee,created,updated")

# Fetch comments
comments_json=$(curl -s -u "$JIRA_EMAIL:$JIRA_API_KEY" \
  -H "Accept: application/json" \
  "$base_url/rest/api/3/issue/$issue_key/comment")

# Parse fields
jira_key=$(echo "$issue_json" | jq -r '.key')
jira_summary=$(echo "$issue_json" | jq -r '.fields.summary')
jira_status=$(echo "$issue_json" | jq -r '.fields.status.name')
jira_assignee=$(echo "$issue_json" | jq -r '.fields.assignee.displayName // "Unassigned"')
jira_created=$(echo "$issue_json" | jq -r '.fields.created')
jira_updated=$(echo "$issue_json" | jq -r '.fields.updated')

# Convert ADF description to markdown
jira_description=$(echo "$issue_json" | jq -r '
  .fields.description | 
  if .type == "doc" then
    [.content[]? | select(.type == "paragraph") |
      (.content // []) | map(select(.type == "text") | .text) | join("")
    ] | join("\n\n")
  else
    ""
  end
')

# Format comments
jira_comments=$(echo "$comments_json" | jq -r '
  .comments // [] | 
  map(
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

# Create output file
output_file=$(echo "$jira_key" | tr '[:upper:]' '[:lower:]').md

{
echo "# $jira_key: $jira_summary"
echo ""
echo "**Status:** $jira_status  "
echo "**Assignee:** $jira_assignee  "
echo "**Created:** $jira_created  "
echo "**Updated:** $jira_updated"
echo ""
echo "## Description"
echo ""
echo "$jira_description"
echo ""
echo "## Comments"
echo ""
echo "$jira_comments"
} > "$output_file"

echo "Saved Jira issue $jira_key to $output_file"
