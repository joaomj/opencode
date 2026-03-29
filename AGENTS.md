# AGENTS.md

IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.

---

## CRITICAL SAFETY RULES (NO EXCEPTIONS)

### Zero-Tolerance Actions
|Trigger|Action|
|-------|-------|
|User says "review"|`@code-reviewer`|
|User says "update docs"|`@doc-maintainer`|
|User asks for CI/CD pipeline on GitHub|`/skill github-cicd-lite`|
|User says "scrape this url/article/blog"|`/skill firecrawl-web-scraper`|
|User says "implement" OR "build feature" OR "create endpoint" OR "add feature"|`/skill implementation-plan`|
|User says "/plan" OR "create a plan"|`/skill implementation-plan`|
|AFTER any code change|ASK: "Update documentation?" → if yes: `@doc-maintainer`|
|User says "commit" OR "/commit"|Run `/commit` command with semantic filtering|
|See `import X` (X not stdlib)|ASK: "Fetch up-to-date docs for X?" → if yes: `/skill context7-docs`|
|Context7 fetch fails|Ask user: "Proceed without docs?"|
|Task completed|ASK: "Update daily activity log?" → if yes: `/skill standup-prep`|
|Phase gate passed|Run `/commit` to save progress|

### Non-Negotiable Rules
|Rule ID|Domain|Rule|Enforcement|Load Skill|
|-------|------|----|-----------|----------|
|OC005|Python|Every function has type hints|Pre-commit mypy|`python-best-practices`|
|OC001|Python|No raw dicts for API schemas|Lint + Pre-commit|`python-best-practices`|
|—|Python|Use `pdm add X` for deps|Manual review|`python-best-practices`|
|OC002|Python|Never view .env content|Lint + Pre-commit|`python-best-practices`|
|—|Docker|Dockerfile has non-root USER|Hadolint DL3002|`docker-best-practices`|
|OC003|Docker|No privileged containers|Lint + Pre-commit|`docker-best-practices`|
|—|ML|Test set touched ONCE only|Manual review|`ml-best-practices`|
|—|ML|Confusion matrix generated|Manual review|`ml-best-practices`|
|OC006|Python|TDD - Test-first for new features|Manual review|`python-best-practices`|
|OC007|Python|80% coverage minimum|Optional pre-commit|`python-best-practices`|
|OC008|Python|ZERO `noqa` or skip in tests - Fix root cause|Block commit|`python-best-practices`|

**Lint Rules Reference:** See `opencode_lint/` directory. Based on Factory.ai "Linters as Law Enforcement" concept.

---

## DETERMINISTIC SKILL TRIGGERS

### User Request Triggers (EXACT MATCH)
|User Says|Action|
|---------|------|
|"review" OR "code review" OR "review my changes" OR "check my code" OR "/review" OR "PR review"|`@code-reviewer`|
|"update docs" OR "prune docs" OR "clean up docs" OR "update documentation"|`@doc-maintainer`|
|"write a cicd pipeline" OR "github actions pipeline" OR "create github workflow"|`/skill github-cicd-lite`|
|"create PR" OR "open pull request" OR "check PR status" OR "fetch PR comments"|`/skill github-pr-workflow`|
|"scrape this url/website/article"|`/skill firecrawl-web-scraper`|
|"implement" OR "build feature" OR "create endpoint" OR "add feature"|`/skill implementation-planning`|
|"/plan" OR "create a plan"|`/skill implementation-planning`|
|"fix bug" OR "fix this bug"|Block: "Write regression test that reproduces bug first"|
|"standup" OR "/standup" OR "daily activity"|Run `/standup-prep` command|
|"jira" OR "fetch jira issue"|`/skill jira-issues`|
|"simplify code" OR "simplify this"|`@simplifier`|

### File Pattern Triggers (BEFORE reading file)
|File Pattern|Action|
|-----------|----------|
|`Dockerfile` OR `Dockerfile.*` OR `docker-compose*.yml`|ASK: "Load Docker best practices?"|
|`train.py` OR `model.py` OR `pipeline.py` OR `features.py`|ASK: "Load ML best practices?"|
|`*.env.example`|STOP - see env-files rule|
|`setup.py` OR `pyproject.toml`|ASK: "Load Python best practices?"|

### Import Statement Triggers (WHILE reading file)
|Import Statement|Action|
|--------------|----------|
|`import pandas` OR `import numpy` OR `from sklearn` OR `import torch`|ASK: "Load ML best practices?"|
|`from pydantic` OR `import pytest`|ASK: "Load Python best practices?"|
|`from fastapi` OR `from flask` OR `from django`|ASK: "Load Python best practices + fetch up-to-date docs?"|

---

## SUBAGENT INDEX

|Subagent|Invoke|Description|
|----------|--------|-------------|
|code-reviewer|`@code-reviewer`|Expert code review with P0-P3 severity levels|
|simplifier|`@simplifier`|Apply project standards to simplify code|
|doc-maintainer|`@doc-maintainer`|Update and prune project documentation|

## SKILL INDEX (Reference Guides - Use `/skill name`)

|Domain|Skill|
|-------|------|
|Implementation planning|`/skill implementation-plan`|
|Python development (with TDD)|`/skill python-best-practices`|
|Docker/containerization|`/skill docker-best-practices`|
|Machine learning|`/skill ml-best-practices`|
|GitHub CI/CD|`/skill github-cicd-lite`|
|GitHub PR workflow|`/skill github-pr-workflow`|
|Jira issues|`/skill jira-issues`|
|Web scraping|`/skill firecrawl-web-scraper`|
|Documentation lookup|`/skill context7-docs`|

---

## CONTEXT7 DOCS API

Use Context7 for ANY external library (React, Vue, Next.js, FastAPI, Django, Flask, Pydantic, SQLAlchemy, pandas, etc.)

1. Detect version from `package.json` OR `requirements.txt` OR `pyproject.toml`
2. Find library ID: `curl -s "https://context7.com/api/v2/libs/search?libraryName=LIBRARY_NAME&query=USER_QUESTION"`
3. Fetch docs: `curl -s "https://context7.com/api/v2/context?libraryId=LIBRARY_ID&query=TOPIC&type=txt"`

|Scenario|Action|
|--------|------|
|User specifies version|Fetch that version|
|Project has version|Fetch matching major version|
|Cannot detect version|Fetch latest, WARN user|
|Library not found|Tell user, proceed with knowledge|

---

## PRE-COMMIT HOOKS (OPTIONAL)

Only install if user explicitly requests: "Install pre-commit hooks" or "/setup-hooks"
Installation: `curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash`

---

## COMMIT PROTOCOL

### Before First Git Operation
**CRITICAL:** Verify identities BEFORE any git commands.

1. Check git identity: `git config user.name && git config user.email`
2. Check remote URL: `git remote -v`
3. If GitHub remote: `gh auth status` (fallback: `ssh -T git@github.com`)
4. **Check SSH key alignment**:
   ```bash
   REMOTE_URL=$(git remote get-url origin 2>/dev/null)
   if [[ "$REMOTE_URL" == git@* ]]; then
       SSH_HOST=$(echo "$REMOTE_URL" | sed 's/.*@//' | sed 's/:.*//')
       EXPECTED_KEY=$(ssh -G "$SSH_HOST" 2>/dev/null | grep '^identityfile' | head -1 | awk '{print $2}' | sed "s|~|$HOME|")
       LOADED_KEYS=$(ssh-add -l 2>/dev/null | awk '{print $3}')
       if [[ -n "$EXPECTED_KEY" ]] && ! echo "$LOADED_KEYS" | grep -q "$EXPECTED_KEY"; then
           echo "SSH Key Mismatch Detected"
           echo "  Expected key: $EXPECTED_KEY"
           echo "  Currently loaded: $LOADED_KEYS"
           # Prompt user to switch
           read -p "Switch SSH agent to correct profile? (y/n) " response
           if [[ "$response" =~ ^[Yy]$ ]]; then
               ssh-add -D
               ssh-add "$EXPECTED_KEY"
           fi
       fi
   fi
   ```
5. If identity mismatch: Present both identities, ask user which to use

### When to Invoke `/commit`
- After completing a logical unit of work
- At phase gates in implementation plans
- Before switching to a different task
- When user explicitly requests to save progress

### Commit Rules
|Rule|Requirement|
|------|-----------|
|Agent generates message|User does NOT write commit messages|
|Respect .gitignore|Automatically excludes gitignored files|
|Exclude planning files|Files with PLAN/TODO/DRAFT/WIP/TEMP/BACKUP/OLD in name|
|One-line only|Maximum 72 characters, no body text|
|No scope|Format: `type: description` (no parentheses)|
|Imperative mood|"Add" not "Added", "Fix" not "Fixed"|

### Commit Type Detection
|Type|When to Use|
|------|-----------|
|`feat:`|New features, added functionality|
|`fix:`|Bug fixes, corrections|
|`docs:`|Documentation changes|
|`style:`|Formatting (no logic change)|
|`refactor:`|Code restructuring without behavior change|
|`test:`|Test files, testing infrastructure|
|`chore:`|Dependencies, build process, configuration|

---

## CORE PRINCIPLES

|Principle|Description|
|---------|-----------|
|investigate-first|NEVER edit without approval. Analyze, plan, ask permission.|
|tradeoffs-required|Every suggestion MUST include: pros, cons, alternatives.|
|consistency|Follow existing patterns. Scan codebase before writing new code.|
|simplicity|Prefer fewest moving parts. Ask "is this overkill?" before abstractions.|
|no-emojis|Never use emojis in code, docs, or communication.|
|security|No secrets in code. Use .env + pydantic-settings. Validate all inputs.|
|tdd-first|Test-first is MANDATORY. RED-GREEN-REFACTOR is non-negotiable. NO exceptions for business logic. Bug fixes REQUIRE regression tests first.|
|no-test-skipping|NEVER use `# noqa`, `@pytest.mark.skip`, `@pytest.mark.xfail`, or any mechanism to bypass failing tests. The sole purpose of tests is to identify failures. When a test fails, fix the root cause - do NOT suppress the symptom.|
|env-files|Never view .env content. Use .env.example for schema reference.|
|python-deps|Use `pdm add`, not direct pyproject.toml edit.|
|tech-context|MANDATORY: tech-context.md is single source of truth.|
|doc-maintenance|After completing a task, ASK: "Update documentation?"|

---

## LINT RULES REFERENCE (Factory.ai Concept)

All rules are enforced via `opencode-lint` package. Run with: `python -m opencode_lint.cli`

|Rule ID|Category|Description|Severity|Auto-fix|
|-------|--------|-------------|--------|--------|
|OC001|Type Safety|No raw dicts for API schemas - Use Pydantic models|Error|No|
|OC002|Security|Never view .env content - Use os.getenv() or pydantic-settings|Error|No|
|OC003|Security|No privileged containers in docker-compose|Error|No|
|OC004|Grep-ability|Absolute imports preferred over relative|Warning|No|
|OC005|Type Safety|Strict type hints required for all functions|Warning|No|
|OC008|Test Integrity|ZERO tolerance for `# noqa` or `@pytest.mark.skip` in tests. Tests exist to catch failures. Fix the code or fix the test.|Error|No|

### How It Works (Factory.ai Pattern)

1. **Agent generates code**
2. **Lint check runs** (`python -m opencode_lint.cli`)
3. **Violations displayed with Rule ID**
4. **Agent warns user**: "Fix OC001 violation? (y/n)"
5. **Pre-commit blocks** if violations remain

This implements the Factory.ai concept: "Linters are the executable spec that ties human intent to agent output."

### Special Handling for Test Failures

**When encountering a failing test:**
- Ask: "Fix the implementation or fix the test?"
- Investigate root cause
- Make minimal fix
- Verify test passes
- **NEVER suggest**: `noqa`, `skip`, `xfail`, or any suppression mechanism

**When seeing `# noqa` in test files:**
- Immediately remove it
- Fix the underlying issue
- Explain: "Tests exist to identify failures, not hide them"

**When user says "just make the tests pass":**
- Clarify: "All tests must pass without suppression"
- Proceed only with proper fixes

---

## AVAILABLE SKILLS (For Subagent Use)

Skills provide specialized instructions for subagents and main agents.

<available_skills>
  <skill>
    <name>implementation-plan</name>
    <description>Propose and design implementation plans with workspace analysis, user interview, tradeoffs analysis, and approval gates</description>
    <location>file:///Users/admin/.config/opencode/skills/implementation-plan/SKILL.md</location>
  </skill>
  <skill>
    <name>python-best-practices</name>
    <description>Complete Python development guide covering code quality, testing, security, dependency management, and TDD</description>
    <location>file:///Users/admin/.config/opencode/skills/python-best-practices/SKILL.md</location>
  </skill>
  <skill>
    <name>docker-best-practices</name>
    <description>Complete containerization guide covering Dockerfile patterns, Docker Compose, security, and networking</description>
    <location>file:///Users/admin/.config/opencode/skills/docker-best-practices/SKILL.md</location>
  </skill>
  <skill>
    <name>ml-best-practices</name>
    <description>Complete ML development guide covering CRISP-DM, data quality, evaluation, and MLflow</description>
    <location>file:///Users/admin/.config/opencode/skills/ml-best-practices/SKILL.md</location>
  </skill>
  <skill>
    <name>github-cicd-lite</name>
    <description>Lean GitHub-only CI pipelines for small Python projects, optimized for speed and security</description>
    <location>file:///Users/admin/.config/opencode/skills/github-cicd-lite/SKILL.md</location>
  </skill>
  <skill>
    <name>github-pr-workflow</name>
    <description>Guide PR lifecycle management with automated context detection, PR description generation from templates, troubleshooting, and best practices for GitHub CLI operations</description>
    <location>file:///Users/admin/.config/opencode/skills/github-pr-workflow/SKILL.md</location>
  </skill>
  <skill>
    <name>context7-docs</name>
    <description>Retrieve up-to-date documentation for software libraries and frameworks via Context7 API</description>
    <location>file:///Users/admin/.config/opencode/skills/context7-docs/SKILL.md</location>
  </skill>
</available_skills>