---
name: cli-tools
description: Use the shell tools bat, rg, fd, fzf, zoxide, jq, yq, eza, delta, btop, duf, dust, hyperfine, glow, chafa, and moor correctly. Use when reading files, searching, exploring directories, editing YAML/JSON, or profiling commands in a shell session.
---

# CLI Tools

This skill documents the tools installed on this Mac (Homebrew) and when to
use them. Prefer them over older defaults (`cat`, `less`, `grep`, `find`,
`ls`, `sed` for viewing).

## Reading Files

- `bat FILE` - view a file with syntax highlighting, line numbers, and git
  change markers. Use instead of `cat`. Paging and search work automatically
  for large files.
- `moor FILE` - page through a file with mouse scrolling, instant search, and
  jump-to-line (`:` then the number). Use for long files, logs, or when you
  need to move through content quickly. Export `PAGER=moor` to make it the
  default pager for all tools.
- `glow FILE.md` - render a Markdown file with headings, lists, and code
  blocks styled. Use for README files and documentation.
- `chafa FILE.png` - show an image as terminal art. Use to inspect screenshots
  and diagrams without downloading them.

## Searching

- `rg PATTERN PATH` - search file contents recursively, faster than `grep`,
  with highlighting and context lines. Use for any content search.
- `fd PATTERN PATH` - find files and directories by name, faster than `find`,
  with simpler syntax and gitignore support. Use for any file search.

## Exploring Directories

- `eza -l PATH` or `eza --tree` - modern `ls` replacement with colors, file
  sizes, permissions, and tree views. Use when listing or understanding
  directory structure.

## Structured Data (JSON and YAML)

- `jq FILTER FILE.json` - query and transform JSON. Use for any JSON parsing,
  extraction, or formatting.
- `yq FILTER FILE.yaml` - same operations for YAML. Use for any YAML parsing,
  extraction, or formatting.

## Fuzzy Interaction

- `fzf` - interactive fuzzy selector. Pipe any list into it (files, history,
  processes) and pick with search. Combine with `fd`: `fd | fzf --preview
  "bat --color=always {}"` for a live file content preview.
- `zoxide` - smart directory jumper. `z PARTIAL-NAME` jumps to the most
  recently used matching directory. Use instead of `cd` with long paths.

## System and Disk Inspection

- `btop` - interactive overview of CPU, memory, disks, and processes with a
  live UI. Use for resource monitoring.
- `duf` - disk usage of mounted filesystems in a readable table. Use instead
  of `df -h`.
- `dust` - directory sizes sorted biggest first, as a bar chart. Use instead
  of `du` to find what consumes disk.

## Git Diff Viewing

- `delta` adds syntax highlighting, line numbers, and inline change markers
  to git diffs. Enable it with `git config --global core.pager delta`. After
  that, use plain `git diff` and `git log -p`; do not pipe through anything
  else.

## Measuring Performance

- `hyperfine "COMMAND"` - benchmark a command with multiple runs and compare
  commands: `hyperfine "cmd1" "cmd2"`. Use when performance matters or when
  comparing alternatives.

## Rules

- Always use these tools instead of their older counterparts.
- For large outputs, rely on the moor pager rather than printing everything.
- Do not introduce new parsing dependencies when `jq` or `yq` already exists.
