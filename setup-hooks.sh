#!/usr/bin/env bash
set -euo pipefail

# Downloads and installs OpenCode Skills pre-commit hooks in the current project
# Usage: curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash

RAW_URL="https://raw.githubusercontent.com/joaomj/opencode/main"

echo "Downloading pre-commit config..."
curl -sSL "$RAW_URL/.pre-commit-config.yaml" -o .pre-commit-config.yaml

echo "Downloading check_file_length.py..."
mkdir -p .hooks
curl -sSL "$RAW_URL/hooks/check_file_length.py" -o .hooks/check_file_length.py
chmod +x .hooks/check_file_length.py

echo "Downloading check_test_mock_abuse.py..."
curl -sSL "$RAW_URL/hooks/check_test_mock_abuse.py" -o .hooks/check_test_mock_abuse.py
chmod +x .hooks/check_test_mock_abuse.py

echo "Downloading mock allowlist template..."
curl -sSL "$RAW_URL/.test-mock-external-allowlist.example" -o .test-mock-external-allowlist.example

echo "Installing pre-commit..."
pip install -q pre-commit

echo "Installing hooks..."
pre-commit install

echo ""
echo "Done! Pre-commit hooks are now active."
echo "Quality checks will run automatically on every 'git commit'."
