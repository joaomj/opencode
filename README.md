# OpenCode Skills Installer

One-line installer for [OpenCode](https://opencode.ai) skills, commands, and agents.

## Quick Start

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/install.sh | bash
```

This interactive script asks which components you want, then downloads them to `~/.config/opencode/`.

## What You Get

### 11 Skills

| Skill | Description |
|-------|-------------|
| `architecture-diagram` | Generate dark-themed system architecture diagrams as standalone HTML/SVG |
| `context7-docs` | Fetch up-to-date library documentation via the Context7 API |
| `create-pull-request` | End-to-end PR creation with branch selection and GitHub CLI |
| `docker-best-practices` | Dockerfile patterns, Docker Compose security, network isolation |
| `firecrawl-web-scraper` | Scrape URLs to markdown/JSON with browser actions and structured extraction |
| `github-cicd-lite` | Lean GitHub Actions CI for Python projects, auto-detects package manager |
| `google-drive-reader` | Read Google Drive files via OAuth (Docs, Sheets, Slides, generic downloads) |
| `jira-issues` | Fetch, create, and search Jira issues using Atlassian CLI |
| `ml-best-practices` | ML development guide: CRISP-DM, evaluation metrics, MLflow tracking |
| `notion-reader` | Search and fetch Notion content using notion-cli |
| `python-best-practices` | Python development: type hints, pydantic, Ruff, testing, SDD |

### 6 Commands

| Command | Description |
|---------|-------------|
| `/commit` | Stage and commit with atomic principles and conventional commit messages |
| `/deslop` | Remove AI-generated code slop (extra comments, defensive checks, casts) |
| `/review` | Task-scoped code review with P0-P3 severity levels |
| `/standup-prep` | Generate daily standup summaries from git activity |
| `/update-docs` | Identify and remove obsolete documentation |
| `/update-opencode` | Sync skills/commands/agents from the remote repository |

### 4 Agents

| Agent | Description |
|-------|-------------|
| `@code-reviewer` | Expert code review with P0-P3 severity (SOLID, security, performance) |
| `@doc-maintainer` | Update and prune documentation for accuracy |
| `@plan` | Primary implementation planner using Spec-Driven Design (SDD) |
| `@simplifier` | Apply project standards to simplify code |

## Customization

After installation, edit `~/.config/opencode/AGENTS.md` to customize rules for your project. The template includes:

- Core principles (pick the ones that matter for your stack)
- Intent-driven agent routing (enable agents you want)
- Context-aware skill loading (enable skills for your tech stack)
- Workflow triggers (define your team's conventions)
- Non-negotiable rules (set your quality bar)
- Subagent index (register custom agents)

Edit `~/.config/opencode/opencode.json` to add your model providers and API keys.

## Updating

Re-run the installer with the `--update` flag to re-download previously selected components:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/install.sh | bash -s -- --update
```

The installer reads the manifest at `~/.config/opencode/.opencode-manifest` and re-downloads everything.

## Manual Installation

If you prefer, clone the repo and copy files manually:

```bash
git clone https://github.com/joaomj/skills.git /tmp/opencode-skills
cp -r /tmp/opencode-skills/skills/* ~/.config/opencode/skills/
cp -r /tmp/opencode-skills/commands/* ~/.config/opencode/commands/
cp -r /tmp/opencode-skills/agents/* ~/.config/opencode/agents/
```

## Pre-Commit Hooks (Optional)

Install quality checks in any Python project:

```bash
curl -sSL https://raw.githubusercontent.com/joaomj/skills/main/setup-hooks.sh | bash
```

Enforces: secrets detection (gitleaks), file length limits, Ruff formatting, Dockerfile linting, mock abuse checks.

## Architecture

The configuration follows a hierarchical model:

1. **Remote AGENTS.md** (`joaomj/skills/main/AGENTS.md`) contains the primary guidelines
2. **Local AGENTS.md** (`~/.config/opencode/AGENTS.md`) overrides remote rules
3. **opencode.json** (`~/.config/opencode/opencode.json`) configures models and permissions

This means you get automatic guideline updates from the remote, while your local rules take precedence.

## Contributing

To add a new skill, command, or agent:

1. Create a new `.md` file in the appropriate directory (`skills/`, `commands/`, `agents/`)
2. Follow the existing format (front matter with name/description, then markdown content)
3. Update the component catalog in `install.sh`
4. Submit a PR

## License

MIT - see [LICENSE](LICENSE) for details.
