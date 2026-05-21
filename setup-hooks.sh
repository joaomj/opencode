#!/usr/bin/env bash
set -euo pipefail

# Downloads and installs OpenCode Skills pre-commit hooks in the current project
# Usage: curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/setup-hooks.sh | bash

RAW_URL="https://raw.githubusercontent.com/joaomj/skills/main"

echo "Downloading pre-commit config..."
curl -sSL "$RAW_URL/.pre-commit-config.yaml" -o .pre-commit-config.yaml

echo "Downloading mock allowlist template..."
curl -sSL "$RAW_URL/.test-mock-external-allowlist.example" -o .test-mock-external-allowlist.example

echo "Installing pre-commit..."
pip install -q pre-commit

echo "Installing hooks..."
pre-commit install

echo ""
echo "Done! Pre-commit hooks are now active."
echo "Quality checks will run automatically on every 'git commit'."
