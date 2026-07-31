# AGENTS.md

## Core Principles

- **no-assumptions**: read code first. Investigate when uncertain.
- **branch-sync-before-pr**: before creating a PR, compare the current branch with the destination branch. Do not rebase or merge automatically.
- **infra-code-separation**: separate infrastructure and application changes into separate commits and PRs unless they are deeply intertwined.
- **no-silent-failures**: every failure must surface through an error, log, recovery classification, or user-visible result.
- **gh-cli-only**: use `gh` for GitHub operations. Do not use curl, wget, or WebFetch against github.com.
- **signed-commits**: sign every commit with the SSH key configured in `~/.gitconfig`. Use `git commit -S`.
- **no-api-commits**: do not use the GitHub Contents API or `gh api --method PUT`.
- **never-read-env**: never read or inspect `.env` values. Use `os.getenv()` for environment variables.
- **no-privileged-containers**: never run privileged containers.

## Evidence

- Rank evidence by signal and noise: deployed or remote behavior, local code, updated documentation, then Jira tickets.
- Treat Jira tickets as context and intent, not as law. Report conflicts between evidence sources.
- Preserve code, identifiers, logs, and error messages verbatim when quoting them.

## Communication

- Use ASD-STE100 technical English.
- Explain the strategy in plain terms before a plan.
- Do not mention time estimates unless asked.
- Do not use emojis or em dashes.
- Keep commit messages within 50 characters.
- Code reviews report only P0 and P1 findings, grouped by file, without line numbers or imperatives. Each finding explains the behavior, impact, and recommendation.

## Planning

- Substantial features and architecture work need a user-approved spec before implementation.
- For a plan, create a new branch from `origin/<default-branch>` using the repository naming convention.
- Write only `PLAN-<ticket-id>.md` at the repository root.
- Back every plan step with current files, symbols, and behavior.
- Mark unknown areas as discovery work.
- Include acceptance criteria, risks, dependencies, open decisions, and out-of-scope work.
- Verify every step before starting the next one. Stop when verification fails.
- Recommend one established coding pattern for each task, with its rationale, trade-offs, and an alternative.
- Prefer composition. Avoid premature abstraction. Separate responsibilities by reason to change.

## Testing

- Test at the highest seam that gives a strong regression signal at an acceptable cost.
- Prefer user-flow tests, then e2e tests, integration tests, and unit or property tests.
- Test user-facing behavior as close to the user experience as possible, including a shell frontend when appropriate.
- Use unit or property tests for complex pure logic only. Do not test every function, ordinary wiring, or private methods without a strong regression signal.
- For each confirmed bug, write one failing black-box regression test at the highest useful seam, fix the bug, and keep the test permanently.
- Do not build large test infrastructure without approval. If the environment blocks verification, record the gap and use the cheapest reliable check.
- Prune low-signal tests. Do not add tests only to increase coverage.
- Do not use internal mocks for user-visible behavior.

## Python And Tooling

- Use `uv` as the only Python package manager and execution wrapper.
- Run Python commands through `uv run` or `uvx`.
- Do not run direct `python`, `pip`, `pytest`, `ruff`, `mypy`, or similar Python tooling commands.
- Prefer Python for non-trivial automation and bash for one-liners.
- Use `rg` instead of `grep` for text searches.
- Treat OC014 hardcoding checks as enforceable errors. Move runtime configuration values to centralized configuration. Keep fixed protocol constants as named constants only when they are not runtime configuration.
- Keep OC014 regression tests for detected hardcoding and valid fixed constants. A clean verification reports zero OC014 warnings.

## Jira

- The agent writes Jira tickets directly.
- Keep tickets focused on the problem, desired user-visible state, acceptance criteria, constraints, and out-of-scope items.
- Keep file paths, symbols, algorithms, and implementation plans out of tickets.
- Use Markdown for Jira descriptions when the MCP field defaults to Markdown.
- Use ADF only when the tool explicitly requests or accepts ADF.

## Opencode Map

- **Config**: `opencode.json`
- **Commands**: `commands/*.md`
- **Skills**: `skills/**/SKILL.md`
- **Linter**: `opencode_lint/`
- **Linter rules**: `opencode_lint/rules/`
- **Teams messaging**: use `skills/tooling/teams-brave-cli/SKILL.md` with the local Python CLI. Never use Playwright MCP or personal browser profiles.

## Routing

| Need | Use | Scope |
|------|-----|-------|
| Create an implementation plan | `/implementation-plan` | User asks for a plan or ticket implementation strategy |
| Create or update a Jira ticket | `/jira` | User asks to write, update, or inspect Jira work |
| Review code | `/code-review` | User explicitly asks for a code review |
| Implement an approved plan | `implement` skill | A spec or approved plan is available |
| Diagnose a hard bug | `diagnosing-bugs` skill | User asks to diagnose or debug a failure |
| Maintain project documentation | `doc-maintenance` skill | User asks to update project documentation |

## Writing Style

- Use a professional tone.
- Be concise.
- Do not use AI filler such as "Certainly", "Of course", or "Happy to help".
