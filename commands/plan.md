---
description: Create phased implementation plan with testable gates, SDD, logging, config, and commit checkpoints
---

# Implementation Planning (SDD - Spec-Driven Design)

Create a structured implementation plan following the investigate-first principle. NEVER edit without approval. Analyze, design, discuss tradeoffs, then plan with strict phase-gate structure.

## Non-Negotiable Rules (STOP if violated)

|Rule | Violation = STOP |
|------|------------------|
| investigate-first | Block if implementation starts before analysis complete |
| design-before-tradeoffs | Block if tradeoffs discussed before architecture defined |
| tradeoffs-before-plan | Block if plan created before options compared |
| approval-gate | Block if execution begins without explicit "yes" |
| consistency-check | Block if new code violates existing patterns |
| spec-clarity | Block if requirements are ambiguous or incomplete |
| sdd-first | Block if tests or implementation begin before specs are defined |
| no-hardcoding | Block if hardcoded values found (URLs, timeouts, thresholds, file paths, magic numbers, retry counts) |

## Conditional Skill Loading

DETECT project type and LOAD relevant skills BEFORE Phase 5 (Action Plan). Apply their rules to every phase.

| Detected Signal | Action |
|-----------------|--------|
| `pyproject.toml` OR `setup.py` OR `requirements.txt` | Load `/skill python-best-practices` |
| `Dockerfile` OR `Dockerfile.*` OR `docker-compose*.yml` | Load `/skill docker-best-practices` |
| `import sklearn` OR `import torch` OR `import pandas` OR `import numpy` | Load `/skill ml-best-practices` |
| None of the above | Skip skill loading, use general rules |

If skill loading fails, ASK user: "Proceed without [domain] best practices?"

## Configuration Policy

Applies to ALL phases. No exceptions.

| Rule | Detail |
|------|--------|
| Config module | All configurable values in a dedicated module (e.g., `config.py` or `settings.py`). Never scattered across source files. |
| Typed config | Use `pydantic-settings` (`BaseSettings`) for typed, validated configuration. Raw dicts for config are FORBIDDEN (OC001). |
| Environment vars | Environment-specific values (DB URLs, API keys, feature flags) via env vars, never in code. `.env` for local dev, `.env.example` for schema reference. |
| Constants | Magic numbers, thresholds, timeouts, retry counts, pagination limits - ALL extracted to config. If a number is not `0`, `1`, or `-1`, it belongs in config. |
| File paths | No hardcoded paths. Use `pathlib.Path` relative to config-defined base directories. |
| Defaults | Defaults live in the config module with clear documentation of what they control and sensible fallbacks. |

## Logging Policy

Professional-grade logging is MANDATORY. Logging is how you understand what happens in production.

| Rule | Detail |
|------|--------|
| Structured logging | REQUIRED. Any library: `structlog`, `python-json-logger`, `loguru`. No plain text log lines in production. |
| Correlation IDs | Every request/operation gets a UUID. Propagated across ALL function calls and log entries. Included in every log record as `correlation_id`. |
| Log levels | `DEBUG` = dev-only diagnostic detail. `INFO` = business events (user created, order placed). `WARNING` = degraded but functional (retry succeeded, fallback used). `ERROR` = operation failed (unhandled exception, external service down). `CRITICAL` = system-level failure (out of memory, database unreachable). No logging at DEBUG in production. |
| Dual output | Console: human-readable during development. File: JSON structured for production. File naming: `logs/app-YYYY-MM-DD.log`. |
| Log rotation | `RotatingFileHandler` or `TimedRotatingFileHandler`. Max 10MB per file, keep 30 days. |
| Format | `timestamp | level | correlation_id | module | function | line | message | extra_fields` |
| Security | NEVER log secrets, tokens, passwords, PII. Use `logging.addFilter()` or structured logging `mask` to redact sensitive fields. |
| Testing | Every phase MUST include log assertion tests - verify correct log level, message content, and correlation ID presence. |
| Centralized config | Logging configuration in a dedicated module (e.g., `src/logging_config.py`). NOT scattered across files. Loaded ONCE at app startup. |
| Context binding | Bind relevant context (request_id, user_id, trace_id) to loggers at operation boundaries, not passed as function arguments. |

---

## Phase 1: Workspace Analysis

**Goal:** Understand the existing codebase before proposing changes.

### Step 1.1: Scan Project Context

Gather essential context:

```bash
ls docs/tech-context.md
ls pyproject.toml package.json requirements.txt Cargo.toml go.mod
find . -name "main.py" -o -name "index.ts" -o -name "app.py" -o -name "main.go" | head -5
ls -la src/ lib/ app/ cmd/ 2>/dev/null || ls -la
```

### Step 1.2: Read Key Files

Priority order:

| Priority | File | Purpose |
|----------|------|---------|
| 1 | `docs/tech-context.md` | Single source of truth for architecture |
| 2 | `pyproject.toml` / `package.json` | Dependencies, scripts, config |
| 3 | Entry point | Application bootstrap |
| 4 | Related modules | Existing patterns to follow |
| 5 | Tests for related modules | Testing conventions |

ALWAYS check if `docs/tech-context.md` exists. If yes, READ IT FIRST.

### Step 1.3: Identify Existing Patterns

Look for:
- **Code style**: Function/class structure
- **Error handling**: How errors are raised and caught
- **Testing patterns**: Test structure, fixtures, mocking
- **Naming conventions**: Files, functions, classes
- **Module organization**: Where similar features live
- **Logging patterns**: Existing logger setup, formatters, handlers
- **Config patterns**: Existing config module, settings management

**Pattern Violation Check:**

| If you see... | Then... |
|---------------|---------|
| `services/` directory | New features go in `services/` |
| `def func(x: int) -> str:` | Use type hints consistently |
| `pytest` tests in `tests/` | Write pytest tests |
| `raise SpecificError()` | Never use bare `except:` |
| Pydantic models for APIs | Never use raw dicts |
| `structlog.get_logger()` | Use structlog for logging |
| `config.py` with `BaseSettings` | Add new config values there |

### Step 1.4: Detect Infrastructure Gaps

Check if project already has:
- [ ] Structured logging module (`logging_config.py` or similar)
- [ ] Config module (`config.py`, `settings.py` with `BaseSettings`)
- [ ] Correlation ID middleware or utility
- [ ] Log file output configuration

If ALL are present, skip conditional Phase 0.
If ANY are missing, Phase 0 (Logging + Config Foundation) will be added to the plan.

---

## Phase 2: User Interview

**Goal:** Achieve 100% specification clarity before design.

### Step 2.1: Clarify Requirements

Ask questions ONE topic at a time:

| Category | Questions |
|----------|-----------|
| What | What exactly should this do? Expected output? |
| Why | Business goal? Problem being solved? |
| Who | Target users? Skill level? |
| When | Real-time? Batch? On-demand? |
| Where | Where in the existing architecture? |
| How | Constraints on implementation approach? |

### Step 2.2: Identify Edge Cases

Ask about:
- Empty inputs
- Maximum values
- Invalid inputs
- Error scenarios
- Concurrent access (if applicable)
- Performance requirements

### Step 2.3: Confirm Scope

Before proceeding:

```
"Let me confirm my understanding:
- [requirement 1]
- [requirement 2]
- [requirement 3]

Is this correct? Anything to add or modify?"
```

**Gate:** Do NOT proceed to Phase 3 until user confirms understanding.

---

## Phase 3: Systems Design & Architecture

**Goal:** Define the technical architecture BEFORE discussing options.

### Step 3.1: Identify System Components

Map high-level architecture:

```
System Architecture:

[Component A]
  | [interface/data flow]
[Component B]
  | [interface/data flow]
[Component C]
```

### Step 3.2: Define Data Flow

Trace data through the system:

```
Input -> [Validation] -> [Processing] -> [Storage] -> [Output]
         |                |              |
      Errors          Metrics       Side effects
```

### Step 3.3: Define Logging Architecture

```
Logging Architecture:

[Component A] --(bind correlation_id)--> [Logger] --(structured JSON)--> [RotatingFileHandler] -> logs/app-YYYY-MM-DD.log
                                           |
                                    [ConsoleHandler] -> dev output
```

Questions to answer:
- Where are loggers created? (centralized module)
- How are correlation IDs generated and propagated?
- What log level for each component?
- What fields are included in every log entry?
- How are sensitive fields masked?

### Step 3.4: Define Config Architecture

```
Config Architecture:

.env -> [pydantic BaseSettings] -> config.py -> consumed by all modules
                                       |
                                  .env.example (schema reference)
```

Questions to answer:
- What values are configurable?
- What are sensible defaults?
- What requires environment-specific override?
- Where does the config module live?

### Step 3.5: Identify Technical Constraints

| Constraint | Impact |
|------------|--------|
| Existing database schema | Must work with current tables |
| API compatibility | Must not break existing endpoints |
| Authentication system | Must use existing auth mechanism |
| Deployment environment | Must run in current infra |
| Existing logging setup | Must extend, not replace |
| Existing config setup | Must extend, not replace |

**Gate:** Architecture (including logging and config) must be defined before proposing options.

---

## Phase 4: Tradeoffs Analysis

**Goal:** Compare approaches for decision-making ONLY. Pros/cons do NOT go into the final plan document.

### Step 4.1: Design Options

Propose at least 2-3 approaches:

| Approach | Description |
|----------|-------------|
| Option A | [brief description] |
| Option B | [brief description] |
| Option C | [brief description] |

For each: pros, cons, fit with architecture from Phase 3.

### Step 4.2: Recommendation

```
"Recommended: Option X because [reason].

Alternatives considered:
- Option Y: [why not chosen]
- Option Z: [why not chosen]"
```

### Step 4.3: Get Consensus

```
"Based on the architecture and tradeoffs, I recommend Option X.

Do you agree with this approach, or would you prefer a different option?"
```

---

## Phase 5: Action Plan

**Goal:** Create structured plan with phases, specs, tests, gates, and commits.

### Step 5.1: Define Implementation Phases

Each phase MUST follow SDD flow:
1. **Define specs** (signatures, types, contracts, edge cases, errors)
2. **Write tests** validating spec compliance
3. **Implement** to fulfill spec
4. **Verify** gate criteria

**Phase Structure:**

```
### Phase N: [Phase Name]

**Objective:** [What this phase accomplishes]

#### Specs to Define (BEFORE tests or implementation)
Define these contracts first:

```python
# [module].py - Spec definitions

class [DataType](BaseModel):
    """Data contract for [purpose]."""
    field: type = ...  # [description]

def function_name(param: type) -> ReturnType:
    """Behavioral contract: [what it does].

    Edge cases:
    - [edge case 1]: raises [ErrorType]
    - [edge case 2]: returns [default]

    Errors:
    - [error condition]: raises [ErrorType]
    """
    ...
```

#### Tests to Write (validate specs)
Write these tests against the specs above:

```python
# tests/test_[module].py

def test_[feature]_spec_compliance():
    """Verify: [spec contract being tested]"""

def test_[feature]_edge_case_[scenario]():
    """Verify: [edge case from spec]"""

def test_[feature]_error_[condition]():
    """Verify: [error contract from spec]"""

def test_[feature]_logging():
    """Verify: correct log level, correlation_id present, message content"""
```

#### Gate Criteria (ALL must pass to proceed)
- [ ] All specs defined with type hints and contracts
- [ ] All new tests pass
- [ ] Tests cover all spec edge cases and error contracts
- [ ] Code coverage >= 80% for new code
- [ ] Lint/type checks pass
- [ ] No hardcoded values (all configurable values in config module)
- [ ] Logging assertions pass (correct level, correlation_id, message)
- [ ] Code follows existing patterns
- [ ] No breaking changes to existing tests

#### Verification Commands
```bash
pytest tests/test_module.py -v --cov=src/module --cov-fail-under=80
ruff check src/module
mypy src/module
```

#### Commit Trigger
After gate criteria pass: `/commit` with message: "feat: [phase objective]"
```

### Step 5.2: Create Phased Todo List

Use `todowrite` to track progress.

### Step 5.3: Write Plan Document

Create `plan-[feature-name].md` at PROJECT ROOT (not in docs/).

```markdown
# Implementation Plan: [Feature Name]

## Summary
[1-2 sentences of what and why]

## Requirements
- [requirement 1]
- [requirement 2]

## Architecture Overview
[High-level system design from Phase 3]

## Logging Architecture
[Logging design from Phase 3.3]

## Config Architecture
[Config design from Phase 3.4]

## Chosen Approach
[Option Name] - [One-line description]
[Why selected - 2-3 sentences max]

## Implementation Phases

[Phase 0: Logging + Config Foundation - CONDITIONAL]
[Only included if infrastructure gaps detected in Step 1.4]

### Phase 1: [Phase Name]
[SDD phase structure as defined above]

### Phase N: Integration & Final Verification
- Integration testing
- End-to-end verification
- Final review

## Success Criteria
- [ ] All gate criteria met for all phases
- [ ] All specs have corresponding tests
- [ ] No implementation without a spec
- [ ] Specs match actual behavior
- [ ] Coverage >= 80%
- [ ] Lint passes
- [ ] No hardcoded values
- [ ] Structured logging with correlation IDs operational
- [ ] No breaking changes
```

**IMPORTANT RULES for Plan Document:**
- NO time estimates
- NO pros/cons in final plan
- NO alternative approaches in final plan
- MUST include spec definitions for each phase
- MUST include test code examples for each phase
- MUST include logging assertions in test examples
- MUST specify exact gate criteria
- MUST specify commit trigger for each phase
- Architecture, logging, and config sections REQUIRED before phases
- Plan file at PROJECT ROOT: `plan-[feature-name].md`

---

## Phase 6: Approval Gate

**Goal:** Wait for explicit "yes" before execution.

### Step 6.1: Present Plan

```
"I've created an implementation plan.

Plan highlights:
- [Number] implementation phases
- Each phase: specs first, then tests, then implementation (SDD)
- Clear gate criteria between phases
- Commits after each successful gate
- Logging + config integrated throughout

The plan document is at: plan-[feature-name].md

Do you approve this plan? Respond with:
- 'yes' to proceed
- 'no' to revise
- Questions if anything is unclear"
```

### Step 6.2: Wait for Approval

Do NOT start implementation until user says "yes".
If user has questions, answer and re-present approval gate.
If user says "no", return to Phase 3, 4, or 5.

### Step 6.3: Approval Confirmation

```
"Plan approved. Executing with SDD methodology:
1. Define specs (signatures, types, contracts)
2. Write tests against specs
3. Implement to fulfill specs
4. Verify gate criteria
5. Commit after each phase

Starting Phase [N]: [Phase Name]"
```

---

## Phase 7: Implementation Execution

**Goal:** Execute plan with strict SDD phase-gate-commit discipline.

### Step 7.1: Execute Phase by Phase

For each phase:

1. **Define specs FIRST** (SDD): Create type hints, contracts, Pydantic models, protocols
2. **Write tests against specs**: Tests validate spec compliance
3. **Implement to fulfill specs**: Write code to satisfy contracts
4. **Verify**: Run all verification commands from plan
5. **Check gates**: Verify ALL gate criteria pass
6. **Commit**: Use `/commit` with specified trigger message
7. **Confirm**: "Phase X complete. Proceed to Phase X+1?"

### Step 7.2: Gate Enforcement

MANDATORY: Do NOT proceed to next phase until:

- [ ] All specs defined before any implementation
- [ ] All phase tests pass
- [ ] Tests cover all spec edge cases and error contracts
- [ ] Coverage >= 80%
- [ ] Lint passes
- [ ] Type checks pass (if applicable)
- [ ] No hardcoded values in new code
- [ ] Logging assertions pass
- [ ] All gate criteria from plan verified
- [ ] Commit created with specified message

### Step 7.3: Handle Deviations

If implementation reveals issues:

1. STOP - Do not proceed
2. Document the issue
3. Ask user for guidance
4. Update plan if needed
5. Get renewed approval before continuing

### Step 7.4: Completion

After final phase passes:

1. Run full test suite: `pytest tests/ -v --cov=src --cov-fail-under=80`
2. Run full lint: `ruff check src/`
3. Verify no regressions
4. Commit final state
5. ASK: "Update documentation?" -> if yes, run `/update-docs`
