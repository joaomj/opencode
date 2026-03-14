# AGENTS.md

IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.

---

## CRITICAL SAFETY RULES (NO EXCEPTIONS)

### Zero-Tolerance Actions
|Trigger|Action|
|-------|-------|
|User says "review"|`/skill code-review-expert`|
|User says "update docs"|`/skill doc-maintenance`|
|User asks for CI/CD pipeline on GitHub|`/skill github-cicd-lite`|
|User says "scrape this url/article/blog"|`/skill firecrawl-web-scraper`|
|AFTER any code change|ASK: "Update documentation?" → if yes: `/skill doc-maintenance`|
|User says "commit" OR "/commit"|Run `/commit` command with semantic filtering and conventional commits|
|See `import X` (X not stdlib)|ASK: "Fetch up-to-date docs for X?" → if yes: Fetch Context7 docs|
|Context7 fetch fails|Ask user: "Proceed without docs?"|
|Task completed|ASK: "Update daily activity log?" → if yes: `/skill standup-prep`|
|Phase gate passed|Run `/commit` to save progress|

### Python Non-Negotiables
|Rule|Violation=STOP|
|------|-----------|
|Every function has type hints|Block if missing|
|No raw dicts for API schemas|Block if detected|
|No secrets in code|Block if detected|
|Never view .env content (Read tool, cat, scripts printing envs)|Block if attempted|
|Use `pdm add X` for deps|Block if direct pyproject.toml edit|

### Docker Non-Negotiables
|Rule|Violation=STOP|
|------|-----------|
|Dockerfile has non-root USER|Block if missing|
|docker-compose has read_only|Block if missing|
|No privileged: true|Block if detected|
|No secrets in ENV|Block if detected|

### ML Non-Negotiables
|Rule|Violation=STOP|
|------|-----------|
|Test set touched ONCE only|Block if multiple accesses|
|Preprocessing in Pipeline|Block if done manually|
|Confusion matrix generated|Block if missing|
|Baseline comparison done|Block if missing|

### TDD Non-Negotiables
|Rule|Violation=STOP|
|------|-----------|
|Test-first for new features|WARN + require justification if skipped|
|80% coverage threshold|Block commit if below threshold|
|Critical path coverage|Business logic MUST have tests|
|Behavior assertions required|Tests must verify outcomes, not internals|
|No orphan test files|Tests must correspond to production code|
|Bug fixes need regression tests|Block fix until test reproduces bug|

---

## DETERMINISTIC SKILL TRIGGERS

### User Request Triggers (EXACT MATCH)
|User Says|Load Skill|
|---------|----------|
|"review" OR "code review" OR "review my changes" OR "check my code" OR "/review" OR "PR review" OR "pull request review"|`/skill code-review-expert`|
|"update docs" OR "prune docs" OR "clean up docs" OR "update documentation" OR "/update-docs"|`/skill doc-maintenance`|
|"write a cicd pipeline" OR "write a ci/cd pipeline" OR "write a ci pipeline" OR "github actions pipeline" OR "set up github actions" OR "create github workflow" OR "/cicd"|`/skill github-cicd-lite`|
|"scrape this url/website/article" OR "save this blog post/newsletter" OR "add to my reading queue"|`/skill firecrawl-web-scraper`|
|"use [library]" OR "implement with [library]" OR "using [library]" OR "with [library]" OR "add [library]"ASK: "Fetch up-to-date docs for [library]?"|
|"implement" OR "write X function" OR "build feature" OR "create endpoint" OR "add feature"|ASK: "Create test scaffold first?"|
|"fix bug" OR "fix this bug" OR "bug fix"|Block: "Write regression test that reproduces bug first"|

### File Pattern Triggers (BEFORE reading file)
|File Pattern|Action|
|-----------|----------|
|`Dockerfile` OR `Dockerfile.*` OR `docker-compose*.yml`|ASK: "Load Docker best practices?"|
|`train.py` OR `model.py` OR `pipeline.py` OR `features.py` OR `preprocessing.py`|ASK: "Load ML best practices?"|
|`*.env.example`|STOP - see env-files rule|
|`setup.py` OR `pyproject.toml`|ASK: "Load Python best practices?"|

### Import Statement Triggers (WHILE reading file)
|Import Statement|Action|
|--------------|----------|
|`import pandas` OR `import numpy` OR `from sklearn` OR `import torch` OR `import tensorflow`|ASK: "Load ML best practices?"|
|`from pydantic` OR `import pydantic` OR `import pytest`|ASK: "Load Python best practices?"|
|`from fastapi` OR `from flask` OR `from django`|ASK: "Load Python best practices + fetch up-to-date docs?"|
|`import react` OR `from react`|ASK: "Fetch up-to-date React docs?"|

### Code Pattern Triggers (WHILE reading file)
|Code Pattern|Issue Detected|Action|
|-----------|--------------|----------|
|`def func(...):` without `->` or `: Type` OR `def func(x, y):` without `: Type` on args|Missing type hints|ASK: "Load Python best practices?"|
|`X_train, X_test, y_train, y_test`|Data split detected|ASK: "Load ML best practices?"|
|`fit_transform(X)` on full dataset|Leakage risk|ASK: "Load ML best practices?"|
|`logging.info(f"...")` with secrets OR `password=`/`api_key=`/`token=` in code|Secret exposure|ASK: "Load Python best practices?"|
|`patch(` OR `patch.object(` OR `MagicMock(` OR `jest.mock(` OR `vi.mock(`|Potential mock abuse|ASK: "Load Python best practices?"|

### Conversation Triggers
|User Shows/Says|Task Type|Action|
|---------------|----------|----------|
|Stack trace/traceback OR test failure OR "This doesn't work" OR "It's throwing an error" OR error log|Debugging|ASK: "Load Python best practices?"|
|"Add tests for this"|Test creation|ASK: "Load Python best practices for testing guidance?"|
|"Can you refactor this?"|Refactoring|Check refactoring triggers|
|Shows diff/code snippet|Code review or fix|Ask: "Review or fix?"|
|No `.github/workflows/*.yml` found in GitHub repo|CI gap|Ask: "Add GitHub CI?" if yes: `/skill github-cicd-lite`|

---

## SKILL INDEX (LOAD ON DEMAND)

|Domain|Skill|
|-------|------|
|Python development|`/skill python-best-practices`|
|Docker/containerization|`/skill docker-best-practices`|
|Machine learning|`/skill ml-best-practices`|
|Workflow/TDD development|`/skill workflow-development`|
|TDD enforcement|`/skill tdd-enforcement`|
|Code review|`/skill code-review-expert`|
|Documentation maintenance|`/skill doc-maintenance`|
|GitHub CI/CD|`/skill github-cicd-lite`|
|Web scraping|`/skill firecrawl-web-scraper`|
|Code simplification|`/skill code-simplifier`|


---

## CONTEXT7 DOCS API

### When to Use
Use Context7 for ANY external library (React, Vue, Next.js, FastAPI, Django, Flask, Pydantic, SQLAlchemy, pandas, etc.)

### Fetch Flow
1. Detect version from `package.json` OR `requirements.txt` OR `pyproject.toml` OR `pip show`
2. Find library ID: `curl -s "https://context7.com/api/v2/libs/search?libraryName=LIBRARY_NAME&query=USER_QUESTION"`
3. Fetch docs: `curl -s "https://context7.com/api/v2/context?libraryId=LIBRARY_ID&query=TOPIC&type=txt"`

### Version Matching
|Scenario|Action|
|--------|------|
|User specifies version|Fetch that version|
|Project has version in package.json/requirements.txt|Fetch matching major version|
|Cannot detect version|Fetch latest, WARN user|
|Library not found in Context7|Tell user, proceed with knowledge|

---

## PRE-COMMIT HOOKS (OPTIONAL)

### Installation Rule
Do NOT install pre-commit hooks by default.

Only install if user explicitly requests: "Install pre-commit hooks" or "/setup-hooks"
Installation command: `curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh -o setup-hooks.sh && chmod +x setup-hooks.sh && ./setup-hooks.sh`

### Before Committing
1. If hooks installed: `pre-commit run --all-files`

---

## COMMIT PROTOCOL

### Before First Git Operation

**CRITICAL: Verify identities BEFORE any git commands**

1. **Check git identity:**
   ```bash
   git config user.name && git config user.email
   ```

2. **Check remote URL:**
   ```bash
   git remote -v
   ```

3. **If remote is GitHub (contains github.com):**

   a. Try GitHub CLI auth check:
   ```bash
   gh auth status
   ```

   b. If GitHub CLI unavailable or failed, test SSH authentication:
   ```bash
   # Extract host from remote URL (e.g., github.com or github.com-alias)
   ssh -T git@<host>
   ```

4. **If remote uses SSH:**
   ```bash
   ssh-add -l
   ```
   - If no keys loaded: warn user to run `ssh-add` before proceeding
   - Note: Agent does NOT automatically add keys

5. **Check for identity mismatch:**
   - Compare git config user with GitHub/SSH authenticated user
   - If mismatch detected (e.g., git config says `alice` but auth shows `bob`):
     - Present both identities
     - Ask user which to use

6. **Present findings to user:**
   ```
   Detected identities:
   - Git config: user.name=[name], user.email=[email]
   - GitHub auth: [username] (if available)
   - SSH key: [key fingerprint] (if applicable)

   Identity match: [YES/NO - user@github matches git config email]

   Use this identity for git operations? [Y/n]

   If mismatch or multiple accounts:
   Which account should I use?
   1. [identity 1 - git config]
   2. [identity 2 - GitHub auth]
   ```

7. **Only proceed after user confirmation**

|Rule|Requirement|
|------|-----------|
|Always verify first|NEVER run git commands without confirming identity|
|GitHub CLI optional|Fallback to SSH auth test if gh unavailable|
|SSH key check|Warn if no keys loaded; do NOT auto-add|
|Identity mismatch|Present all detected identities, let user choose|
|User selects|Agent does NOT choose - user must confirm|

### When to Invoke `/commit`
- After completing a logical unit of work
- At phase gates in implementation plans
- Before switching to a different task
- When user explicitly requests to save progress
- After user says "commit" or types "/commit"

### Commit Rules
|Rule|Requirement|
|------|-----------|
|Agent generates message|User does NOT write commit messages|
|Respect .gitignore|Automatically excludes gitignored files|
|Exclude planning files|Files with PLAN/TODO/DRAFT/WIP/TEMP/BACKUP/OLD in name|
|Auto-detect type|feat/fix/docs/style/refactor/test/chore based on changes|
|One-line only|ALWAYS use one-line commit messages. Maximum 72 characters, no body text, no multi-line|
|No scope|Format: `type: description` (no parentheses)|
|Imperative mood|"Add" not "Added", "Fix" not "Fixed"|
|Hooks|Ask before installing; run if already installed|
|User interruption|Only when uncertain about file classification|

### Commit Type Detection
|Type|When to Use|
|------|-----------|
|`feat:`|New features, added functionality, new endpoints, new components|
|`fix:`|Bug fixes, corrections, patches|
|`docs:`|Documentation changes (README, docs/, comments)|
|`style:`|Formatting, whitespace, semicolons, quotes (no logic change)|
|`refactor:`|Code restructuring without behavior change|
|`test:`|Test files, testing infrastructure, test utilities|
|`chore:`|Dependencies, build process, configuration, misc tasks|

### Examples
- `feat: add user authentication endpoints`
- `fix: resolve null pointer in login flow`
- `docs: update API reference for v2`
- `test: add unit tests for auth service`
- `refactor: simplify error handling logic`

---

## CORE PRINCIPLES

|investigate-first|NEVER edit without approval. Analyze, plan, ask permission.|
|tradeoffs-required|Every suggestion MUST include: pros, cons, alternatives. Quantify when possible.|
|consistency|Follow existing patterns. Scan codebase before writing new code.|
|simplicity|Prefer fewest moving parts. Ask "is this overkill?" before abstractions.|
|no-emojis|Never use emojis in code, docs, or communication.|
|security|No secrets in code. Use .env + pydantic-settings. Validate all inputs.|
|tdd-first|Test-first where it fits. Business logic needs tests. Bug fixes need regression tests. Config/spike work exempt.|
|testing-policy|Prefer behavior/state assertions and real integrations; mock only external boundaries by default.|
|env-files|Never view .env content. Read tool, cat, scripts printing envs are FORBIDDEN. Scripts can LOAD .env internally. Use .env.example for schema reference.|
|python-deps|When changing/adding Python dependencies, you MUST use `pdm add`, not direct pyproject.toml edit.|
|tech-context|MANDATORY: docs/tech-context.md is single source of truth for current project architecture, technical decisions.|
|ml-reporting|MANDATORY: ML projects must include CRISP-DM Build Report in docs/tech-context.md. Each phase documented with STAR.|
|doc-maintenance|After completing a task, ASK: "Update documentation?" → if yes: `/skill doc-maintenance`.|

---

## REFACTORING TRIGGERS

|Triggers|Action|
|--------|-------|
|Hard to explain|Consider refactor|
|DRY violation|Consider refactor|
|Security issue|MUST refactor|
|Pattern appears 3+ times|Consider refactor|
|YAGNI principle|Don't refactor prematurely. Don't build for hypothetical futures.|

---

## DEVELOPMENT PHILOSOPHY

|incremental|Build in testable increments. Each phase needs objective verification.|
|checkpoint-driven|Define testable success criteria before starting each major step.|
|verify-first|Prove the current increment works before building on top of it.|
