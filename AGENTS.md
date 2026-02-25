# Development Guidelines|v3.0|deterministic-triggers

IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning.

---

## CRITICAL RULES (No Exceptions)

### Zero-Tolerance Actions
| Trigger | Action | Verification |
|---------|--------|--------------|
| User says "review" | `/skill code-review-expert` | Check skill invoked |
| User says "update docs" | `/skill doc-maintenance` | Check skill invoked |
| User asks for CI/CD pipeline on GitHub | `/skill github-cicd-lite` | Check skill invoked |
| AFTER any code change | Run `/skill doc-maintenance` | Check skill invoked |
| BEFORE commit | Ensure hook setup exists (`setup-hooks.sh`), install if missing, then run `pre-commit run --all-files` | Check all verification pass |
| See `import X` (X not stdlib) | Fetch Context7 docs for X | Check docs loaded |
| Context7 fetch fails | Ask user: "Should I proceed without docs?" | User confirmation |

### Python Non-Negotiables
| Rule | Violation = STOP |
|------|-----------------|
| Every function has type hints | Block if missing |
| No raw dicts for API schemas | Block if detected |
| No secrets in code | Block if detected |
| No .env file reading | Block if attempted |
| Use `pdm add X` for deps | Block if direct pyproject.toml edit |

### Docker Non-Negotiables
| Rule | Violation = STOP |
|------|-----------------|
| Dockerfile has non-root USER | Block if missing |
| docker-compose has read_only | Block if missing |
| No privileged: true | Block if detected |
| No secrets in ENV | Block if detected |

### ML Non-Negotiables
| Rule | Violation = STOP |
|------|-----------------|
| Test set touched ONCE only | Block if multiple accesses |
| Preprocessing in Pipeline | Block if done manually |
| Confusion matrix generated | Block if missing |
| Baseline comparison done | Block if missing |

---

## PRE-FLIGHT CHECKLIST (MANDATORY)

BEFORE writing ANY code, you MUST complete ALL steps:

### Step 1: Context Scan
- [ ] Read `docs/tech-context.md` if exists (project architecture)
- [ ] Read `pyproject.toml` or `package.json` (dependencies, versions)
- [ ] Find existing tests (test patterns, coverage)
- [ ] Find entry points (main.py, app.py, index.js, etc.)
- [ ] Check for existing CI workflows in `.github/workflows/*.yml` or `.yaml`
- [ ] If `setup-hooks.sh` is missing in the current codebase, install it: `curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh -o setup-hooks.sh && chmod +x setup-hooks.sh`

### Step 2: Task Classification
Answer: What type of task is this?
- [ ] New feature → Identify domain, load relevant instruction
- [ ] Bug fix → Load `@instructions/python/error-handling.md`
- [ ] Test fix/add → Load `@instructions/python/testing.md`
- [ ] Refactoring → Check triggers section
- [ ] Documentation → Load `doc-maintenance` skill
- [ ] Debugging → Load `@instructions/python/error-handling.md`

### Step 3: External Dependencies Check
- [ ] Check if task involves external library
- [ ] If YES: Detect version from package.json/requirements.txt
- [ ] If YES: Fetch Context7 docs BEFORE coding
- [ ] If Context7 fails: Ask user before proceeding

### Step 4: Load Instructions
Based on task classification, load appropriate instruction:
- [ ] Python task → Load from `@instructions/python/`
- [ ] Docker task → Load from `@instructions/docker/`
- [ ] ML task → Load from `@instructions/ml/`
- [ ] Workflow task → Load from `@instructions/workflow/`

**DO NOT PROCEED to Step 5 until ALL 4 steps complete.**

### Step 5: Post-Code Verification
AFTER writing code, verify:
- [ ] Type hints added (Python)
- [ ] Error handling added
- [ ] Tests written/updated
- [ ] Lint passes (`ruff check .`)
- [ ] Tests pass (`pytest`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] `/skill doc-maintenance` ran

---

## USER REQUEST -> ACTION (Exact Match)

### Code Review Triggers
User says ANY of these phrases:
- "review"
- "code review"
- "review my changes"
- "check my code"
- "/review"
- "PR review"
- "pull request review"

**ACTION:** RUN `/skill code-review-expert` IMMEDIATELY. No analysis needed.

### Documentation Triggers
User says ANY of these phrases:
- "update docs"
- "prune docs"
- "clean up docs"
- "update documentation"
- "/update-docs"

**ACTION:** RUN `/skill doc-maintenance` IMMEDIATELY. No analysis needed.

### CI/CD Triggers (GitHub)
User says ANY of these phrases:
- "write a cicd pipeline"
- "write a ci/cd pipeline"
- "write a ci pipeline"
- "github actions pipeline"
- "set up github actions"
- "create github workflow"
- "/cicd"

**ACTION:** RUN `/skill github-cicd-lite` IMMEDIATELY. No analysis needed.

### Library-Specific Triggers
User says ANY of these patterns:
- "use [library]"
- "implement with [library]"
- "using [library]"
- "with [library]"
- "add [library]"

**ACTION:** 
1. Detect version from project files
2. Fetch Context7 docs for [library] with matching version
3. If version not found, fetch latest and warn user

---

## AUTOMATIC TASK DETECTION

You MUST classify your task before starting. Apply these detection rules:

### File-Based Detection (Check BEFORE reading file)
| File Pattern | Auto-Load Instruction | Reason |
|-------------|----------------------|--------|
| `test_*.py`, `*_test.py`, `tests/*.py` | `@instructions/python/testing.md` | Test file detected |
| `conftest.py` | `@instructions/python/testing.md` | Pytest config detected |
| `Dockerfile`, `Dockerfile.*` | `@instructions/docker/dockerfile.md` | Docker build detected |
| `docker-compose*.yml` | `@instructions/docker/compose-template.md` | Compose config detected |
| `train.py`, `model.py`, `pipeline.py` | `@instructions/ml/crisp-dm.md` | ML training detected |
| `features.py`, `preprocessing.py` | `@instructions/ml/leakage-prevention.md` | Feature engineering detected |
| `*.env.example` | STOP - see `env-files` rule | Never read .env files |
| `setup.py`, `pyproject.toml` | `@instructions/python/ruff-rules.md` | Config reference |

### Import-Based Detection (Check WHILE reading file)
| Import Statement | Auto-Load Instruction | Reason |
|-----------------|----------------------|--------|
| `import pandas`, `import numpy` | `@instructions/ml/data-splitting.md` | Data manipulation |
| `from sklearn`, `import torch`, `import tensorflow` | `@instructions/ml/evaluation.md` + `@instructions/ml/leakage-prevention.md` | ML framework |
| `import logging` | `@instructions/python/logging.md` | Logging detected |
| `from pydantic`, `import pydantic` | `@instructions/python/pydantic.md` | Pydantic usage |
| `import pytest`, `import unittest` | `@instructions/python/testing.md` | Test framework |
| `from fastapi`, `from flask`, `from django` | `@instructions/python/pydantic.md` + Context7 fetch | API framework |
| `import react`, `from react` | Context7 fetch React docs | Frontend framework |

### Pattern-Based Detection (Check WHILE reading file)
| Code Pattern | Issue Detected | Auto-Load | Fix |
|-------------|----------------|-----------|-----|
| `def func(...):` without `->` or `: Type` | Missing type hints | `@instructions/python/type-hints.md` | Add return type |
| `def func(x, y):` without `: Type` on args | Missing arg types | `@instructions/python/type-hints.md` | Add arg types |
| `class X(BaseModel):` | Pydantic model | `@instructions/python/pydantic.md` | Apply patterns |
| `try:/except:` without logging or raise | Swallowed exception | `@instructions/python/error-handling.md` | Add proper handling |
| `try:/except Exception:` | Bare except | `@instructions/python/error-handling.md` | Specify exception type |
| `X_train, X_test, y_train, y_test` | Data split detected | `@instructions/ml/data-splitting.md` | Validate split method |
| `fit_transform(X)` on full dataset | Leakage risk | `@instructions/ml/leakage-prevention.md` | Use Pipeline |
| `logging.info(f"...")` with secrets | Security risk | `@instructions/python/logging.md` | Remove secrets |
| `password=`, `api_key=`, `token=` in code | Hardcoded secret | Security rule | Move to env vars |

### Conversation-Based Detection
| User Shows / Says | Task Type | Auto-Load |
|------------------|-----------|-----------|
| Stack trace / traceback | Debugging | `@instructions/python/error-handling.md` |
| Test failure output | Test fix | `@instructions/python/testing.md` |
| "This is slow" / performance issue | Optimization | Check domain (python/docker/ml) |
| "This doesn't work" | Debugging | `@instructions/python/error-handling.md` |
| "Add tests for this" | Test creation | `@instructions/python/testing.md` |
| "It's throwing an error" | Exception handling | `@instructions/python/error-handling.md` |
| "Can you refactor this?" | Refactoring | Check refactoring triggers |
| Shows diff / code snippet | Code review or fix | Ask: "Should I review or fix this?" |
| Shares error log | Debugging | `@instructions/python/error-handling.md` |
| No `.github/workflows/*.yml` found in a GitHub repo | CI gap detection | Ask: "I don't see a GitHub CI workflow here. Want me to add a lean, secure CI pipeline for this repo?"; if yes run `/skill github-cicd-lite` |

### Domain Detection Decision Tree
```
IF file contains `def ` or `class `:
  IF file contains `BaseModel` or `pydantic`:
    -> Python + Pydantic task
  ELIF file contains `sklearn` or `torch`:
    -> Python + ML task
  ELSE:
    -> Python task
    
IF file is Dockerfile:
  -> Docker task
  
IF file is docker-compose*.yml:
  -> Docker Compose task
  
IF file contains `import react` or `from react`:
  -> Frontend task (fetch Context7 React docs)
  
IF file contains `from fastapi` or `from flask`:
  -> Backend API task (fetch Context7 docs)
```

---

## CONTEXT7 API WITH VERSION DETECTION

### When to Use Context7
Use Context7 for ANY external library:
- JavaScript: React, Vue, Svelte, Angular, Next.js, Express, etc.
- Python: FastAPI, Django, Flask, Pydantic, SQLAlchemy, pandas, etc.
- Any npm package or PyPI package not in stdlib

### Step 1: Detect Library Version
```bash
# For npm packages
cat package.json | grep '"react":'          # e.g., "react": "^19.0.0"

# For Python packages
cat requirements.txt | grep pandas          # e.g., pandas==2.1.0
cat pyproject.toml | grep -A2 pandas
pip show pandas | grep Version              # e.g., Version: 2.1.0
```

### Step 2: Fetch Version-Matched Docs
```bash
# Step 2a: Find library ID
curl -s "https://context7.com/api/v2/libs/search?libraryName=LIBRARY_NAME&query=USER_QUESTION"

# Step 2b: Fetch documentation
curl -s "https://context7.com/api/v2/context?libraryId=LIBRARY_ID&query=TOPIC&type=txt"
```

### Version Matching Rules
| Scenario | Action |
|----------|--------|
| User specifies version: "use React 19" | Fetch React 19 docs |
| Project has version in package.json | Fetch matching major version docs |
| Project has version in requirements.txt | Fetch matching major version docs |
| Cannot detect version | Fetch latest docs, WARN user |
| Library not found in Context7 | Tell user, proceed with available knowledge |

### Example: React with Version Detection
```bash
# User says: "use React for this component"
# Step 1: Detect version
cat package.json | grep '"react":'  # Returns: "react": "^18.2.0"

# Step 2: Search for React 18
curl -s "https://context7.com/api/v2/libs/search?libraryName=react&query=18"

# Step 3: Fetch React 18 docs for hooks
curl -s "https://context7.com/api/v2/context?libraryId=/websites/react_dev_reference&query=useState+hooks&type=txt"
```

### Step 3: Verification
After fetching Context7 docs:
- Confirm doc version matches expected version
- If major version mismatch: WARN user "Fetched React 18 docs, project uses React 19. Proceed?"
- If docs don't load: ASK user "Context7 unavailable. Proceed without docs?"

---

## Core Principles
|investigate-first|NEVER edit without approval. Analyze, plan, ask permission.
|tradeoffs-required|Every suggestion MUST include: pros, cons, alternatives. Quantify when possible.
|consistency|Follow existing patterns. Scan codebase before writing new code.
|simplicity|Prefer fewest moving parts. Ask "is this overkill?" before abstractions.
|no-emojis|Never use emojis in code, docs, or communication.
|security|No secrets in code. Use .env + pydantic-settings. Validate all inputs.
|env-files|NEVER read .env files - only .env.example for schema reference
|python-deps|When changing/adding Python dependencies, you MUST use `pdm` commands (e.g., `pdm add`), not directly edit `pyproject.toml`.
|tech-context|MANDATORY: docs/tech-context.md is the single source of truth for current project architecture, technical decisions.
|ml-reporting|MANDATORY: ML projects must include a CRISP-DM Build Report in docs/tech-context.md. Each phase documented with STAR.
|doc-maintenance|The final step of your task MUST be: running the "doc-maintenance" skill.

---

## Workflow
|1|Workspace Analysis - scan docs/tech-context.md, pyproject.toml, entry points
|2|User Interview - ask questions until spec is 100% clear
|3|Action Plan - step-by-step todos with testable checkpoints between phases
|4|Approval Gate - wait for explicit "yes" before executing the plan
|5|Execute - after approval, write phased todo plan in docs/; only advance after gate pass; commit after each gate (no pushes)

---

## Task Management
|atomic-units|Break tasks into smallest testable pieces
|todo-tracking|Use TodoWrite for 3+ steps. Mark complete immediately.
|phase-plan-file|After plan approval, write plan as phased todo list in docs/
|phase-gates|Define explicit pass/fail gate criteria between phases
|gate-commits|After each gate passes, create a commit (never push unless requested)
|stop-when|Tests pass, feature works, code documented

---

## Documentation
|source-of-truth|docs/tech-context.md - Single-File Memory Bank. Mandatory for all projects.
|document-why|Explain decisions and tradeoffs, not just mechanics
|data-flow|How data moves through components, entry to exit
|depth-over-brevity|docs/tech-context.md must be a DEEP technical report. For every metric: calculation method, why chosen, observed values.
|no-proactive-docs|Never create README/docs unless explicitly requested

---

## Instruction Index (Load on Detection)
|python|@instructions/python/{type-hints.md,pydantic.md,error-handling.md,ruff-rules.md,logging.md,testing.md}
|docker|@instructions/docker/{dockerfile.md,runtime-security.md,compose-template.md,network-isolation.md}
|ml|@instructions/ml/{crisp-dm.md,data-splitting.md,leakage-prevention.md,evaluation.md,feature-importance.md,mlflow.md}
|workflow|@instructions/workflow/{planning.md,task-management.md,pr-description.md}
|tools|@instructions/tools/up-to-date-docs.md

---

## Quality Checks|pre-commit-hooks
|check|tool|purpose|
|secrets|gitleaks|detects hardcoded secrets|
|file-length|python script|max 300 lines per Python file|
|formatting|ruff|code formatting and linting|
|dockerfile|hadolint|Dockerfile best practices|
|no-main|pre-commit|prevents commits to main/master|

Setup: if `setup-hooks.sh` is missing in the current codebase, install it with `curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh -o setup-hooks.sh && chmod +x setup-hooks.sh`, then run `./setup-hooks.sh`.

---

## Ruff Rules|@instructions/pyproject.toml
|line-length=100|target-version=py311
|select|E,W,F,I,B,C4,UP,ARG,SIM,PTH,ERA,PL,RUF,S,NPY
|max-complexity=15|max-args=7|max-statements=50

---

## Refactoring Triggers
|triggers|Hard to explain, DRY violation, security issue, pattern appears 3+ times
|yagni|Don't refactor prematurely. Don't build for hypothetical futures.

---

## Development Philosophy
|incremental|Build in testable increments. Each phase needs objective verification.
|checkpoint-driven|Define testable success criteria before starting each major step.
|verify-first|Prove the current increment works before building on top of it.
