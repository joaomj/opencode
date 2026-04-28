#!/usr/bin/env bash
set -euo pipefail

# OpenCode Skills Installer
# Usage: curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/install.sh | bash
#        bash install.sh --update

REPO_RAW_URL="${OPENCODE_REPO_URL:-https://raw.githubusercontent.com/joaomj/skills/main}"
TARGET_DIR="${OPENCODE_DIR:-$HOME/.config/opencode}"
MANIFEST_FILE="$TARGET_DIR/.opencode-manifest"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Component catalog: name|description|files...
SKILLS=(
  "architecture-diagram|Generate dark-themed system architecture diagrams|skills/architecture-diagram/SKILL.md"
  "c4-diagram|Generate C4 model diagrams (System Context, Container, Component)|skills/c4-diagram/SKILL.md"
  "context7-docs|Fetch up-to-date library docs via Context7 API|skills/context7-docs/SKILL.md"
  "create-pull-request|End-to-end PR creation with GitHub CLI|skills/create-pull-request/SKILL.md"
  "docker-best-practices|Dockerfile patterns, security, networking|skills/docker-best-practices/SKILL.md"
  "firecrawl-web-scraper|Scrape URLs to markdown/JSON with browser actions|skills/firecrawl-web-scraper/SKILL.md"
  "github-cicd-lite|Lean GitHub Actions CI for Python projects|skills/github-cicd-lite/SKILL.md"
  "google-drive-reader|Read Google Drive files via OAuth (multi-file)|skills/google-drive-reader/SKILL.md:skills/google-drive-reader/drive_reader.py:skills/google-drive-reader/.env.example:skills/google-drive-reader/.gitignore"
  "jira-issues|Fetch, create, and search Jira issues|skills/jira-issues/SKILL.md"
  "ml-best-practices|ML dev guide: CRISP-DM, evaluation, MLflow|skills/ml-best-practices/SKILL.md"
  "notion-reader|Search and fetch Notion content via CLI (multi-file)|skills/notion-reader/SKILL.md:skills/notion-reader/.env.example"
  "python-best-practices|Python dev guide: type hints, pydantic, testing|skills/python-best-practices/SKILL.md"
)

COMMANDS=(
  "commit|Stage and commit changes with atomic principles|commands/commit.md"
  "deslop|Remove AI-generated code slop from current branch|commands/deslop.md"
  "review|Task-scoped code review with P0-P3 severity|commands/review.md"
  "standup-prep|Generate daily standup from git activity|commands/standup-prep.md"
  "update-docs|Identify and remove obsolete documentation|commands/update-docs.md"
  "update-opencode|Sync skills/commands/agents from remote|commands/update-opencode.md"
)

AGENTS=(
  "code-reviewer|Expert code review with P0-P3 severity|agents/code-reviewer.md"
  "doc-maintainer|Update and prune project documentation|agents/doc-maintainer.md"
  "plan|Primary planner using Goal-Driven Development|agents/plan.md"
  "simplifier|Apply project standards to simplify code|agents/simplifier.md"
)

HOOKS_FILES=(
  "hooks/check_file_length.py"
  "hooks/check_test_mock_abuse.py"
  ".pre-commit-config.yaml"
  ".test-mock-external-allowlist.example"
)

LINTER_FILES=(
  "opencode_lint/README.md"
  "opencode_lint/__init__.py"
  "opencode_lint/cli.py"
  "opencode_lint/pyproject.toml"
  "opencode_lint/rule.py"
  "opencode_lint/runner.py"
  "opencode_lint/violation.py"
  "opencode_lint/rules/__init__.py"
  "opencode_lint/rules/absolute_imports.py"
  "opencode_lint/rules/no_env_file_access.py"
  "opencode_lint/rules/no_privileged_containers.py"
  "opencode_lint/rules/no_raw_dict_api.py"
  "opencode_lint/rules/strict_type_hints.py"
)

print_banner() {
  echo ""
  echo -e "${BLUE}========================================${NC}"
  echo -e "${BLUE}  OpenCode Skills Installer v2.0${NC}"
  echo -e "${BLUE}========================================${NC}"
  echo ""
}

check_prerequisites() {
  if ! command -v curl &>/dev/null; then
    echo -e "${RED}Error: curl is required but not installed.${NC}"
    exit 1
  fi
  if ! command -v bash &>/dev/null; then
    echo -e "${RED}Error: bash is required.${NC}"
    exit 1
  fi
}

detect_existing() {
  if [[ -d "$TARGET_DIR" ]]; then
    echo -e "${YELLOW}Warning: $TARGET_DIR already exists.${NC}"
    read -rp "Do you want to backup existing files? [Y/n] " backup
    if [[ ! "$backup" =~ ^[Nn]$ ]]; then
      backup_dir="$TARGET_DIR.backup.$(date +%Y%m%d_%H%M%S)"
      echo "Backing up to $backup_dir..."
      cp -r "$TARGET_DIR" "$backup_dir"
      echo -e "${GREEN}Backup created: $backup_dir${NC}"
    fi
  fi
}

show_menu() {
  local title="$1"
  shift
  local items=("$@")

  echo ""
  echo -e "${BLUE}--- $title ---${NC}"
  local i=1
  for item in "${items[@]}"; do
    local name="${item%%|*}"
    local desc="${item#*|}"
    desc="${desc%%|*}"
    printf "  %2d. %-25s %s\n" "$i" "$name" "$desc"
    ((i++))
  done
  echo "   0. None"
  echo "   a. All"
  echo ""
  read -rp "Select (space-separated numbers, 0, or a): " selection
  echo "$selection"
}

parse_selection() {
  local selection="$1"
  local -n arr="$2"

  if [[ "$selection" == "0" ]]; then
    echo ""
    return
  fi
  if [[ "$selection" == "a" || "$selection" == "A" ]]; then
    local result=""
    for item in "${arr[@]}"; do
      local name="${item%%|*}"
      result="$result $name"
    done
    echo "$result"
    return
  fi

  local result=""
  for num in $selection; do
    if [[ "$num" =~ ^[0-9]+$ && "$num" -gt 0 && "$num" -le ${#arr[@]} ]]; then
      local item="${arr[$((num-1))]}"
      local name="${item%%|*}"
      result="$result $name"
    fi
  done
  echo "$result"
}

get_files_for_component() {
  local name="$1"
  local -n catalog="$2"

  for item in "${catalog[@]}"; do
    local item_name="${item%%|*}"
    local rest="${item#*|}"
    local files="${rest#*|}"
    if [[ "$item_name" == "$name" ]]; then
      echo "$files"
      return
    fi
  done
  echo ""
}

download_file() {
  local file="$1"
  local dest="$TARGET_DIR/$file"
  local dir
  dir="$(dirname "$dest")"

  mkdir -p "$dir"
  local url="$REPO_RAW_URL/$file"

  echo "  Downloading: $file"
  if ! curl -fsSL "$url" -o "$dest" 2>/dev/null; then
    echo -e "${RED}    Failed to download: $file${NC}"
    return 1
  fi
  return 0
}

install_component() {
  local name="$1"
  local files="$2"

  echo "Installing: $name"
  local IFS=':'
  read -ra file_list <<< "$files"
  local success=0
  local failed=0
  for file in "${file_list[@]}"; do
    if download_file "$file"; then
      ((success++))
    else
      ((failed++))
    fi
  done

  if [[ $failed -gt 0 ]]; then
    echo -e "${YELLOW}  $success downloaded, $failed failed${NC}"
  else
    echo -e "${GREEN}  $success file(s) installed${NC}"
  fi
}

install_hooks() {
  echo ""
  echo -e "${BLUE}Installing Python pre-commit hooks...${NC}"
  local success=0
  local failed=0
  for file in "${HOOKS_FILES[@]}"; do
    if download_file "$file"; then
      ((success++))
    else
      ((failed++))
    fi
  done
  echo -e "${GREEN}Hooks: $success installed, $failed failed${NC}"

  # Run setup-hooks.sh if it was downloaded
  if [[ -f "$TARGET_DIR/setup-hooks.sh" ]]; then
    echo "Running setup-hooks.sh..."
    bash "$TARGET_DIR/setup-hooks.sh"
  fi
}

install_linter() {
  echo ""
  echo -e "${BLUE}Installing opencode linter...${NC}"
  local success=0
  local failed=0
  for file in "${LINTER_FILES[@]}"; do
    if download_file "$file"; then
      ((success++))
    else
      ((failed++))
    fi
  done
  echo -e "${GREEN}Linter: $success installed, $failed failed${NC}"
}

copy_template() {
  local source="$1"
  local dest="$2"

  if [[ -f "$TARGET_DIR/$dest" ]]; then
    echo -e "${YELLOW}$dest already exists. Skipping (use the example file as reference).${NC}"
    return
  fi

  echo "Copying template: $source -> $dest"
  if curl -fsSL "$REPO_RAW_URL/$source" -o "$TARGET_DIR/$dest" 2>/dev/null; then
    echo -e "${GREEN}Template copied: $dest${NC}"
  else
    echo -e "${RED}Failed to copy template: $source${NC}"
  fi
}

save_manifest() {
  echo ""
  echo -e "${BLUE}Saving manifest...${NC}"

  local skills_str=""
  for s in $SELECTED_SKILLS; do
    skills_str="${skills_str:+,}$s"
  done

  local commands_str=""
  for c in $SELECTED_COMMANDS; do
    commands_str="${commands_str:+,}$c"
  done

  local agents_str=""
  for a in $SELECTED_AGENTS; do
    agents_str="${agents_str:+,}$a"
  done

  cat > "$MANIFEST_FILE" <<EOF
# OpenCode Skills Manifest
# Use: curl -sSL $REPO_RAW_URL/install.sh | bash -s -- --update
REPO_URL=$REPO_RAW_URL
DATE=$(date +%Y-%m-%d)
SKILLS=${skills_str:-none}
COMMANDS=${commands_str:-none}
AGENTS=${agents_str:-none}
HOOKS=$INSTALL_HOOKS
LINTER=$INSTALL_LINTER
EOF

  echo -e "${GREEN}Manifest saved: $MANIFEST_FILE${NC}"
}

update_from_manifest() {
  if [[ ! -f "$MANIFEST_FILE" ]]; then
    echo -e "${RED}No manifest found at $MANIFEST_FILE${NC}"
    echo "Run the installer normally first to create a manifest."
    exit 1
  fi

  echo ""
  echo -e "${BLUE}Updating from manifest...${NC}"

  # Parse manifest
  local repo_url
  repo_url=$(grep "^REPO_URL=" "$MANIFEST_FILE" | cut -d= -f2-)
  local skills_str
  skills_str=$(grep "^SKILLS=" "$MANIFEST_FILE" | cut -d= -f2-)
  local commands_str
  commands_str=$(grep "^COMMANDS=" "$MANIFEST_FILE" | cut -d= -f2-)
  local agents_str
  agents_str=$(grep "^AGENTS=" "$MANIFEST_FILE" | cut -d= -f2-)
  local hooks
  hooks=$(grep "^HOOKS=" "$MANIFEST_FILE" | cut -d= -f2-)
  local linter
  linter=$(grep "^LINTER=" "$MANIFEST_FILE" | cut -d= -f2-)

  # Re-download components
  if [[ "$skills_str" != "none" && -n "$skills_str" ]]; then
    local IFS=','
    read -ra skills_arr <<< "$skills_str"
    for skill in "${skills_arr[@]}"; do
      local files
      files=$(get_files_for_component "$skill" SKILLS)
      if [[ -n "$files" ]]; then
        install_component "$skill" "$files"
      fi
    done
  fi

  if [[ "$commands_str" != "none" && -n "$commands_str" ]]; then
    local IFS=','
    read -ra commands_arr <<< "$commands_str"
    for command in "${commands_arr[@]}"; do
      local files
      files=$(get_files_for_component "$command" COMMANDS)
      if [[ -n "$files" ]]; then
        install_component "$command" "$files"
      fi
    done
  fi

  if [[ "$agents_str" != "none" && -n "$agents_str" ]]; then
    local IFS=','
    read -ra agents_arr <<< "$agents_str"
    for agent in "${agents_arr[@]}"; do
      local files
      files=$(get_files_for_component "$agent" AGENTS)
      if [[ -n "$files" ]]; then
        install_component "$agent" "$files"
      fi
    done
  fi

  if [[ "$hooks" == "true" ]]; then
    install_hooks
  fi

  if [[ "$linter" == "true" ]]; then
    install_linter
  fi

  # Update manifest date
  sed -i.bak "s/^DATE=.*/DATE=$(date +%Y-%m-%d)/" "$MANIFEST_FILE"
  rm -f "$MANIFEST_FILE.bak"

  echo ""
  echo -e "${GREEN}Update complete!${NC}"
}

print_summary() {
  echo ""
  echo -e "${GREEN}========================================${NC}"
  echo -e "${GREEN}  Installation Complete!${NC}"
  echo -e "${GREEN}========================================${NC}"
  echo ""
  echo "Installed to: $TARGET_DIR"
  echo ""

  if [[ -n "$SELECTED_SKILLS" ]]; then
    echo "Skills installed:"
    for s in $SELECTED_SKILLS; do echo "  - $s"; done
    echo ""
  fi

  if [[ -n "$SELECTED_COMMANDS" ]]; then
    echo "Commands installed:"
    for c in $SELECTED_COMMANDS; do echo "  - $c"; done
    echo ""
  fi

  if [[ -n "$SELECTED_AGENTS" ]]; then
    echo "Agents installed:"
    for a in $SELECTED_AGENTS; do echo "  - $a"; done
    echo ""
  fi

  if [[ "$INSTALL_HOOKS" == "true" ]]; then
    echo "Pre-commit hooks: installed"
    echo ""
  fi

  if [[ "$INSTALL_LINTER" == "true" ]]; then
    echo "OpenCode linter: installed"
    echo ""
  fi

  if [[ -f "$TARGET_DIR/AGENTS.md" ]]; then
    echo -e "${YELLOW}Note: AGENTS.md was created from template.${NC}"
    echo "Edit it to customize rules for your project."
    echo ""
  fi

  if [[ -f "$TARGET_DIR/opencode.json" ]]; then
    echo -e "${YELLOW}Note: opencode.json was created from template.${NC}"
    echo "Replace placeholders with your actual model and provider settings."
    echo ""
  fi

  echo "Next steps:"
  echo "  1. Edit $TARGET_DIR/AGENTS.md for your project"
  echo "  2. Edit $TARGET_DIR/opencode.json with your model and API keys"
  echo "  3. Run 'opencode' to start"
  echo ""
  echo "Update later with:"
  echo "  curl -sSL $REPO_RAW_URL/install.sh | bash -s -- --update"
  echo ""
}

# Main

if [[ "${1:-}" == "--update" ]]; then
  update_from_manifest
  exit 0
fi

print_banner
check_prerequisites
detect_existing

SELECTION=$(show_menu "Skills" "${SKILLS[@]}")
SELECTED_SKILLS=$(parse_selection "$SELECTION" SKILLS)

SELECTION=$(show_menu "Commands" "${COMMANDS[@]}")
SELECTED_COMMANDS=$(parse_selection "$SELECTION" COMMANDS)

SELECTION=$(show_menu "Agents" "${AGENTS[@]}")
SELECTED_AGENTS=$(parse_selection "$SELECTION" AGENTS)

# Create target directory
mkdir -p "$TARGET_DIR"

# Install selected components
echo ""
echo -e "${BLUE}Installing selected components...${NC}"

for skill in $SELECTED_SKILLS; do
  local files
  files=$(get_files_for_component "$skill" SKILLS)
  if [[ -n "$files" ]]; then
    install_component "$skill" "$files"
  fi
done

for command in $SELECTED_COMMANDS; do
  local files
  files=$(get_files_for_component "$command" COMMANDS)
  if [[ -n "$files" ]]; then
    install_component "$command" "$files"
  fi
done

for agent in $SELECTED_AGENTS; do
  local files
  files=$(get_files_for_component "$agent" AGENTS)
  if [[ -n "$files" ]]; then
    install_component "$agent" "$files"
  fi
done

# Optional tooling
echo ""
read -rp "Install Python pre-commit hooks? [y/N] " hooks_input
INSTALL_HOOKS="false"
if [[ "$hooks_input" =~ ^[Yy]$ ]]; then
  INSTALL_HOOKS="true"
  install_hooks
fi

read -rp "Install opencode linter (Python)? [y/N] " linter_input
INSTALL_LINTER="false"
if [[ "$linter_input" =~ ^[Yy]$ ]]; then
  INSTALL_LINTER="true"
  install_linter
fi

# Templates
echo ""
read -rp "Copy AGENTS.md.example as template? [Y/n] " agents_template
if [[ ! "$agents_template" =~ ^[Nn]$ ]]; then
  copy_template "AGENTS.md.example" "AGENTS.md"
fi

read -rp "Copy opencode.json.example as template? [Y/n] " opencode_template
if [[ ! "$opencode_template" =~ ^[Nn]$ ]]; then
  copy_template "opencode.json.example" "opencode.json"
fi

# Save manifest
save_manifest

# Print summary
print_summary
