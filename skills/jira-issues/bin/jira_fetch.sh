#!/bin/bash
# Fetch Jira issue and save as markdown
# Enhanced ADF to Markdown converter

set -euo pipefail

# Load environment variables
if [[ -f .env ]]; then
    set -a && source .env && set +a
else
    echo "Error: .env file not found in current directory"
    echo "Create .env with: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_KEY"
    exit 1
fi

# Validate required environment variables
: "${JIRA_BASE_URL:?Error: JIRA_BASE_URL not set in .env}"
: "${JIRA_EMAIL:?Error: JIRA_EMAIL not set in .env}"
: "${JIRA_API_KEY:?Error: JIRA_API_KEY not set in .env}"

issue_key="${1:-}"
if [[ -z "$issue_key" ]]; then
    echo "Usage: $0 <issue-key>"
    echo "Example: $0 PROJ-123"
    exit 1
fi

base_url="${JIRA_BASE_URL%/}"

echo "Fetching $issue_key..."

# Fetch issue details
issue_response=$(curl -s -w "\n%{http_code}" -u "$JIRA_EMAIL:$JIRA_API_KEY" \
    -H "Accept: application/json" \
    "$base_url/rest/api/3/issue/$issue_key?fields=summary,description,status,assignee,created,updated,priority,labels,components,issuetype")

http_code=$(echo "$issue_response" | tail -n1)
issue_json=$(echo "$issue_response" | sed '$d')

if [[ "$http_code" != "200" ]]; then
    echo "Error: Failed to fetch issue (HTTP $http_code)"
    echo "Response: $issue_json" | jq -r '.errorMessages // .error // .' 2>/dev/null || echo "$issue_json"
    exit 1
fi

# Fetch comments
comments_response=$(curl -s -w "\n%{http_code}" -u "$JIRA_EMAIL:$JIRA_API_KEY" \
    -H "Accept: application/json" \
    "$base_url/rest/api/3/issue/$issue_key/comment")

comments_http_code=$(echo "$comments_response" | tail -n1)
comments_json=$(echo "$comments_response" | sed '$d')

if [[ "$comments_http_code" != "200" ]]; then
    echo "Warning: Failed to fetch comments (HTTP $comments_http_code)"
    comments_json='{"comments":[]}'
fi

# Parse issue fields
jira_key=$(echo "$issue_json" | jq -r '.key // "unknown"')
jira_summary=$(echo "$issue_json" | jq -r '.fields.summary // "No summary"')
jira_status=$(echo "$issue_json" | jq -r '.fields.status.name // "Unknown"')
jira_assignee=$(echo "$issue_json" | jq -r '.fields.assignee.displayName // "Unassigned"')
jira_created=$(echo "$issue_json" | jq -r '.fields.created // "Unknown"')
jira_updated=$(echo "$issue_json" | jq -r '.fields.updated // "Unknown"')
jira_priority=$(echo "$issue_json" | jq -r '.fields.priority.name // "None"')
jira_issuetype=$(echo "$issue_json" | jq -r '.fields.issuetype.name // "Unknown"')
jira_labels=$(echo "$issue_json" | jq -r '.fields.labels // [] | if length > 0 then join(", ") else "None" end')
jira_components=$(echo "$issue_json" | jq -r '.fields.components // [] | map(.name) | if length > 0 then join(", ") else "None" end')

# ADF to Markdown converter
convert_adf_to_markdown() {
    local adf_json="$1"
    
    echo "$adf_json" | jq -r '
    def apply_marks($text; $marks):
        reduce ($marks // [])[] as $mark ($text;
            if $mark.type == "strong" then "**" + . + "**"
            elif $mark.type == "em" then "*" + . + "*"
            elif $mark.type == "strike" then "~~" + . + "~~"
            elif $mark.type == "code" then "`" + . + "`"
            elif $mark.type == "underline" then "<u>" + . + "</u>"
            elif $mark.type == "link" then "[" + . + "](" + ($mark.attrs.href // "") + ")"
            else . end
        );
    
    def render_inline($node):
        if $node.type == "text" then apply_marks($node.text; $node.marks)
        elif $node.type == "hardBreak" then "\n"
        elif $node.type == "emoji" then $node.attrs.shortName // ""
        elif $node.type == "mention" then ($node.attrs.text // "@" + ($node.attrs.userName // "unknown"))
        elif $node.type == "inlineCard" then "[" + ($node.attrs.url // "link") + "]"
        elif $node.type == "date" then $node.attrs.timestamp // ""
        elif $node.type == "status" then "`" + ($node.attrs.text // "") + "`"
        else "" end;
    
    def render_content($content):
        [$content[]? | render_inline(.)] | join("");
    
    def render_block($node):
        if $node.type == "paragraph" then
            render_content($node.content // [])
        elif $node.type == "heading" then
            ("#" * $node.attrs.level) + " " + render_content($node.content // [])
        elif $node.type == "bulletList" then
            ($node.content // []) | 
            map((.content // []) | map(render_block(.)) | join("")) |
            map("- " + .) |
            join("\n")
        elif $node.type == "orderedList" then
            ($node.content // []) |
            to_entries |
            map(
                .key as $idx |
                .value |
                (.content // []) | map(render_block(.)) | join("") |
                "\($idx + 1). " + .
            ) |
            join("\n")
        elif $node.type == "listItem" then
            render_content($node.content // [])
        elif $node.type == "codeBlock" then
            "```" + ($node.attrs.language // "") + "\n" + 
            render_content($node.content // []) +
            "\n```"
        elif $node.type == "blockquote" then
            ($node.content // []) | map(render_block(.)) | map("> " + .) | join("\n> ")
        elif $node.type == "rule" then
            "---"
        elif $node.type == "table" then
            ($node.content // []) as $rows |
            if ($rows | length) > 0 then
                ($rows | map(.content // [])) as $all_rows |
                ($all_rows | map(length) | max) as $col_count |
                # Extract text from cells
                ($all_rows | map(
                    map((.content // []) | map(render_block(.)) | join(""))
                )) as $table_data |
                # Calculate column widths
                ([range(0; $col_count)] | map(
                    . as $col_idx |
                    $table_data | map(.[$col_idx] // "" | length) | max
                )) as $widths |
                # Format all rows
                ($table_data | map(
                    . as $row |
                    "| " + ([range(0; $col_count)] | map(
                        ($row[.] // "") as $cell_text |
                        $cell_text + " " * ($widths[.] - ($cell_text | length))
                    ) | join(" | ")) + " |"
                )) as $formatted_rows |
                # Combine header, separator, and data
                if ($formatted_rows | length) > 0 then
                    $formatted_rows[0] + "\n| " + ([range(0; $col_count)] | map("-" * $widths[.]) | join(" | ")) + " |" +
                    if ($formatted_rows | length) > 1 then
                        "\n" + ($formatted_rows[1:] | join("\n"))
                    else "" end
                else ""
                end
            else
                ""
            end
        elif $node.type == "tableHeader" or $node.type == "tableCell" then
            ($node.content // []) | map(render_block(.)) | join("")
        elif $node.type == "panel" then
            ($node.content // []) | map(render_block(.)) | join("\n") |
            "> **" + ($node.attrs.panelType // "Info") + " Panel**\n> " + gsub("\n"; "\n> ")
        elif $node.type == "nestedExpand" then
            ($node.content // []) | map(render_block(.)) | join("\n\n") |
            "<details>\n<summary>**" + ($node.attrs.title // "Expand") + "**</summary>\n\n" + . + "\n</details>"
        else
            ""
        end;
    
    if .type == "doc" then
        [.content[]? | render_block(.)] | map(select(length > 0)) | join("\n\n")
    else
        ""
    end
    '
}

# Convert description
description_adf=$(echo "$issue_json" | jq -c '.fields.description // null')
description_markdown=$(convert_adf_to_markdown "$description_adf")

# Convert comments
comments_markdown=$(echo "$comments_json" | jq -r '
    def apply_marks($text; $marks):
        reduce ($marks // [])[] as $mark ($text;
            if $mark.type == "strong" then "**" + . + "**"
            elif $mark.type == "em" then "*" + . + "*"
            elif $mark.type == "strike" then "~~" + . + "~~"
            elif $mark.type == "code" then "`" + . + "`"
            elif $mark.type == "link" then "[" + . + "](" + ($mark.attrs.href // "") + ")"
            else . end
        );
    
    def render_inline($node):
        if $node.type == "text" then apply_marks($node.text; $node.marks)
        elif $node.type == "hardBreak" then "\n"
        elif $node.type == "emoji" then $node.attrs.shortName // ""
        elif $node.type == "mention" then ($node.attrs.text // "@" + ($node.attrs.userName // "unknown"))
        elif $node.type == "status" then "`" + ($node.attrs.text // "") + "`"
        else "" end;
    
    def render_content($content):
        [$content[]? | render_inline(.)] | join("");
    
    def render_block($node):
        if $node.type == "paragraph" then render_content($node.content // [])
        elif $node.type == "heading" then ("#" * $node.attrs.level) + " " + render_content($node.content // [])
        elif $node.type == "bulletList" then
            ($node.content // []) | 
            map((.content // []) | map(render_block(.)) | join("")) |
            map("- " + .) |
            join("\n")
        elif $node.type == "orderedList" then
            ($node.content // []) |
            to_entries |
            map(.key as $idx | .value | (.content // []) | map(render_block(.)) | join("") | "\($idx + 1). " + .) |
            join("\n")
        elif $node.type == "listItem" then render_content($node.content // [])
        elif $node.type == "codeBlock" then
            "```" + ($node.attrs.language // "") + "\n" + render_content($node.content // []) + "\n```"
        elif $node.type == "blockquote" then ($node.content // []) | map(render_block(.)) | map("> " + .) | join("\n> ")
        elif $node.type == "rule" then "---"
        elif $node.type == "table" then
            (.content // []) as $rows |
            if ($rows | length) > 0 then
                ($rows | map(.content // [])) as $all_rows |
                ($all_rows | map(length) | max) as $col_count |
                ($all_rows | map(map((.content // []) | map(render_block(.)) | join("")))) as $table_data |
                ([range(0; $col_count)] | map(. as $col_idx | $table_data | map(.[$col_idx] // "" | length) | max)) as $widths |
                ($table_data | map(. as $row | "| " + ([range(0; $col_count)] | map(($row[.] // "") as $cell_text | $cell_text + " " * ($widths[.] - ($cell_text | length))) | join(" | ")) + " |")) as $formatted_rows |
                if ($formatted_rows | length) > 0 then
                    $formatted_rows[0] + "\n| " + ([range(0; $col_count)] | map("-" * $widths[.]) | join(" | ")) + " |" +
                    if ($formatted_rows | length) > 1 then "\n" + ($formatted_rows[1:] | join("\n")) else "" end
                else "" end
            else "" end
        elif $node.type == "tableHeader" or $node.type == "tableCell" then ($node.content // []) | map(render_block(.)) | join("")
        elif $node.type == "panel" then
            ($node.content // []) | map(render_block(.)) | join("\n") |
            "> **" + ($node.attrs.panelType // "Info") + " Panel**\n> " + gsub("\n"; "\n> ")
        elif $node.type == "nestedExpand" then
            ($node.content // []) | map(render_block(.)) | join("\n\n") |
            "<details>\n<summary>**" + ($node.attrs.title // "Expand") + "**</summary>\n\n" + . + "\n</details>"
        else "" end;

    .comments // [] |
    map(
        "### " + (.author.displayName // "Unknown") + " • " + (.created[0:10] // "") + "\n\n" +
        if .body.type == "doc" then
            [.body.content[]? | render_block(.)] | map(select(length > 0)) | join("\n\n")
        else
            ""
        end
    ) | join("\n\n---\n\n")
')

# Create output file
output_file=$(echo "$jira_key" | tr '[:upper:]' '[:lower:]').md

{
echo "# $jira_key: $jira_summary"
echo ""
echo "| Field | Value |"
echo "|-------|-------|"
echo "| **Type** | $jira_issuetype |"
echo "| **Status** | $jira_status |"
echo "| **Priority** | $jira_priority |"
echo "| **Assignee** | $jira_assignee |"
echo "| **Created** | ${jira_created:0:10} |"
echo "| **Updated** | ${jira_updated:0:10} |"
echo "| **Labels** | $jira_labels |"
echo "| **Components** | $jira_components |"
echo ""
echo "---"
echo ""
echo "## Description"
echo ""
if [[ -n "$description_markdown" && "$description_markdown" != "null" ]]; then
    echo "$description_markdown"
else
    echo "_No description provided_"
fi
echo ""

# Only add comments section if there are comments
comment_count=$(echo "$comments_json" | jq -r '.comments | length // 0')
if [[ "$comment_count" -gt 0 ]]; then
    echo "---"
    echo ""
    echo "## Comments ($comment_count)"
    echo ""
    echo "$comments_markdown"
fi
} > "$output_file"

echo "Saved Jira issue $jira_key to $output_file"
