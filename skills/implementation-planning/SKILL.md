---
name: implementation-planning
description: Propose and design implementation plans with workspace analysis, user interview, tradeoffs analysis, and approval gates before any code changes
license: MIT
---

# Implementation Planning

Design implementation plans following the investigate-first principle: NEVER edit without approval. Analyze, plan, ask permission.

## Non-Negotiable Rules (STOP if violated)

|Rule | Violation = STOP |
|------|------------------|
| investigate-first | Block if implementation starts before analysis complete |
| tradeoffs-required | Block if proposal lacks pros/cons/alternatives |
| approval-gate | Block if execution begins without explicit "yes" |
| consistency-check | Block if new code violates existing patterns |
| spec-clarity | Block if requirements are ambiguous or incomplete |

## When to Use This Skill vs Others

| Skill | Use When |
|-------|----------|
| `implementation-planning` | ANY implementation request (small or large). Quick planning, user interview, tradeoffs, approval. |
| `workflow-development` | FORMAL feature development requiring full documentation (PRD → Design → Specs → Implementation). Use for complex, documented features. |
| `tdd-enforcement` | DURING implementation to enforce test-first practices. |

**Flow:** `implementation-planning` → (if formal process needed) → `workflow-development` → (during coding) → `tdd-enforcement`

## Invocation Contract

Use this skill when:

- User says: "implement", "build feature", "create endpoint", "add feature"
- User says: "/plan" or "create a plan" or "design a solution"
- User describes a feature to build
- Agent needs to propose implementation approach

## Workflow

### Phase 1: Workspace Analysis

**Goal:** Understand the existing codebase before proposing changes.

#### Step1.1: Scan Project Context

Gather essential context before any planning:

```bash
# Check for tech-context.md (single source of truth)
ls docs/tech-context.md

# Check project configuration
ls pyproject.toml package.json requirements.txt Cargo.toml go.mod

# Find entry points
find . -name "main.py" -o -name "index.ts" -o -name "app.py" -o -name "main.go" | head -5

# Identify project structure
ls -la src/ lib/ app/ cmd/ 2>/dev/null || ls -la
```

#### Step1.2: Read Key Files

Priority order for context gathering:

| Priority | File | Purpose |
|----------|------|---------|
| 1 | `docs/tech-context.md` | Single source of truth for architecture |
| 2 | `pyproject.toml` / `package.json` | Dependencies, scripts, config |
| 3 | Entry point (main/main.py) | Application bootstrap |
| 4 | Related modules | Existing patterns to follow |
| 5 | Tests for related modules | Testing conventions |

**CRITICAL**: Always check if `docs/tech-context.md` exists. If yes, READ IT FIRST.

#### Step1.3: Identify Existing Patterns

Look for:

- **Code style**: How are functions/classes structured?
- **Error handling**: How are errors raised and caught?
- **Testing patterns**: Test structure, fixtures, mocking approach
- **Naming conventions**: Files, functions, classes
- **Module organization**: Where do similar features live?

**Pattern Violation Check:**

| If you see... | Then... |
|---------------|---------|
| `services/` directory | New features go in `services/` |
| `def func(x: int) -> str:` | Use type hints consistently |
| `pytest` tests in `tests/` | Write pytest tests, not unittest |
| `raise SpecificError()` | Never use bare `except:` |
| Pydantic models for APIs | Never use raw dicts |

### Phase 2: User Interview

**Goal:** Achieve 100% specification clarity before planning.

#### Step2.1: Clarify Requirements

Ask questions **one topic at a time** (conversational, not interrogative):

| Category | Questions to Ask |
|----------|-----------------|
| **What** | What exactly should this do? What's the expected output? |
| **Why** | What's the business goal? What problem does this solve? |
| **Who** | Who will use this? What's their skill level? |
| **When** | When should this run? Real-time? Batch? On-demand? |
| **Where** | Where does this fit in the existing architecture? |
| **How** | Any constraints on implementation approach? |

#### Step 2.2: Identify Edge Cases

Ask about:

- Empty inputs
- Maximum values
- Invalid inputs
- Error scenarios
- Concurrent access (if applicable)
- Performance requirements

#### Step 2.3: Confirm Scope

Before proceeding, confirm:

```
"Let me confirm my understanding:
- [requirement 1]
- [requirement 2]
- [requirement 3]

Is this correct? Anything to add or modify?"
```

**Gate:** Do NOT proceed to Phase 3 until user confirms understanding.

### Phase 3: Tradeoffs Analysis

**Goal:** Every suggestion MUST include pros, cons, and alternatives.

#### Step3.1: Design Options

Propose at least 2-3 approaches:

| Approach | Description | Pros | Cons |
|----------|-------------|------|------|
| Option A | [brief description] | [pro1, pro2] | [con1, con2] |
| Option B | [brief description] | [pro1, pro2] | [con1, con2] |
| Option C | [brief description] | [pro1, pro2] | [con1, con2] |

#### Step 3.2: Recommendation

After presenting options, recommend one:

```
"Recommended: Option X because [reason].

Alternatives considered:
- Option Y: [why not chosen]
- Option Z: [why not chosen]"
```

#### Step 3.3: Quantify When Possible

Include metrics where applicable:

| Metric | Option A | Option B |
|--------|----------|----------|
| Estimated complexity | Low | Medium |
| Time to implement | 2 days | 4 days |
| Performance impact | Negligible | +50ms latency |
| Breaking changes | None | Requires migration |
| Risk level | Low | Medium |

### Phase 4: Action Plan

**Goal:** Step-by-step todos with testable checkpoints.

#### Step 4.1: Create Phased Todo List

Use `TodoWrite` for tasks with 3+ steps:

```python
todowrite([
    {"content": "Analyze workspace and gather context", "status": "completed", "priority": "high"},
    {"content": "Interview user for requirements clarity", "status": "completed", "priority": "high"},
    {"content": "Design options and analyze tradeoffs", "status": "in_progress", "priority": "high"},
    {"content": "Get user approval on chosen approach", "status": "pending", "priority": "high"},
    {"content": "Create phased implementation plan", "status": "pending", "priority": "high"},
])
```

#### Step 4.2: Define Testable Gates

Each phase must have clear pass/fail criteria:

```markdown
## Phase 1: Data Model
**Estimation**: X days

### Tasks
1. Create migration
2. Define models

### Gate Criteria
- [ ] Migration runs successfully
- [ ] Model unit tests pass
- [ ] Coverage >= 80%

### Verification Commands
pytest tests/test_models.py -v --cov=src/models --cov-fail-under=80
```

#### Step 4.3: Write Plan Document

Create `docs/plan-[feature-name].md` with:

```markdown
# Implementation Plan: [Feature Name]

## Summary
[1-2 sentences of what and why]

## Requirements
- [requirement 1]
- [requirement 2]
- [requirement 3]

## Design Options

### Option A: [Name]
**Description**: [brief description]
**Pros**: [list pros]
**Cons**: [list cons]
**Estimation**: X days
**Risk**: Low/Medium/High

### Option B: [Name]
[same structure]

### Chosen Approach
**Option X** because [reason].

## Implementation Phases

### Phase 1: [Name]
**Estimation**: X days

#### Tasks
1. [task 1]
2. [task 2]

#### Tests to Write (BEFORE implementation)
```python
# test_file.py
def test_x():
    [test code]
```

#### Gate Criteria
- [ ] [criterion 1]
- [ ] [criterion 2]

#### Verification Commands
[commands to verify phase completion]

### Phase N: Integration
[final phase with end-to-end verification]

## Success Criteria
- [ ] All gate criteria met
- [ ] Tests pass
- [ ] Coverage >= 80%
- [ ] Lint passes
- [ ] Documentation updated

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [risk 1] | Low/Medium/High | Low/Medium/High | [mitigation] |
```

### Phase 5: Approval Gate

**Goal:** Wait for explicit "yes" before execution.

#### Step5.1: Present Plan

Show the complete plan to the user:

```
"Here's my implementation plan:

[Summary of plan]

Do you approve this plan? Please respond with:
- 'yes' to proceed with implementation
- 'no' and I'll revise the approach
- Questions if anything is unclear"
```

#### Step 5.2: Wait for Approval

**CRITICAL**: 
- Do NOT start implementation until user says "yes" (or equivalent approval)
- If user has questions, answer them and re-present the approval gate
- If user says "no", return to Phase 2 or Phase 3 as appropriate

#### Step 5.3: Approval Confirmation

After approval, confirm:

```
"Plan approved. I'll now implement according to the phases.

Starting with Phase 1: [Phase Name]

[Begin implementation]"
```

### Phase 6: Implementation Execution

**Goal:** Execute plan with phase-by-phase verification.

#### Step 6.1: Execute Phase by Phase

For each phase:

1. **Pre-implementation check**: Verify gate criteria areclear
2. **Write tests FIRST** (TDD): Create failing tests
3. **Implement**: Write minimal code to pass tests
4. **Verify**: Run tests, check coverage
5. **Commit**: Use `/commit` command after gate passes
6. **Ask approval**: "Phase X complete. Proceed to Phase X+1?"

#### Step 6.2: Gate Enforcement

**MANDATORY**: Do NOT proceed to next phase until:

- [ ] All phase tests pass
- [ ] Coverage meets threshold (>=80%)
- [ ] Lint passes
- [ ] Gate criteria verified
- [ ] Commit created

#### Step 6.3: Handle Deviations

If implementation reveals issues:

1. **STOP**
2. **Document the issue**
3. **Ask user for guidance**
4. **Update plan if needed**
5. **Get renewed approval**

## Plan Document Location

All implementation plans go in `docs/plan-[feature-name].md`.

### Naming Convention

| Feature | Plan File |
|---------|-----------|
| User authentication | `docs/plan-user-auth.md` |
| Password reset | `docs/plan-password-reset.md` |
| API endpoint /users | `docs/plan-users-endpoint.md` |
| Database migration | `docs/plan-db-migration.md` |

### After Approval

Once approved, the plan document becomes the single source of truth:

- Refer back to it during implementation
- Update it if requirements change
- Mark phases as completed

## Example Session

```
User: I need to implement user authentication

Agent: [Phase 1: Workspace Analysis]
Let me analyze the existing codebase first...

[Reads docs/tech-context.md, pyproject.toml, existing auth patterns]

I see this project uses:
- FastAPI for async endpoints
- SQLAlchemy for database
- Tests in tests/ directory with pytest
- Existing user model in src/models/user.py

[Phase 2: User Interview]
I have a few questions to clarify requirements:

1. What authentication method should I use?
   - Email/password
   - OAuth (Google, GitHub, etc.)
   - Both?

User: Email/password for now, OAuth later

Agent: Got it. Email/password with bcrypt hashing.

2. Should sessions be stateless (JWT) or stateful (database sessions)?

   | Approach | Pros | Cons |
   |----------|------|------|
   | JWT | Stateless, scalable | Harder to revoke |
   | Sessions | Easy revocation | Requires DB storage |

User: JWT tokens

Agent: JWT tokens with refresh token rotation. Any constraints on:
- Token expiration time?
- Password requirements?

User: 15min access tokens, 7-day refresh tokens. Min8 chars password.

Agent: [Phase 3: Tradeoffs Analysis]
Let me confirm my understanding:
- Email/password authentication with bcrypt
- JWT tokens (15min access, 7day refresh)
- Refresh token rotation for security
- Min8 char passwords

Is this correct? Anything to add or modify?

User: Yes, that's correct

Agent: [Phase4: Action Plan]
Here's my implementation plan:

## Design Options

| Approach | Description | Pros | Cons |
|----------|-------------|------|------|
| Option A: JWT with refresh rotation | Access + refresh tokens | Scalable, secure | Token management complexity |
| Option B: Session-based | Database sessions | Simple revocation | Doesn't scale horizontally |
| Option C: OAuth only | External auth | No password management | Dependency on external service |

**Recommended: Option A** (JWT with refresh rotation) because it matches your scalability requirements and keeps implementation simple.

## Implementation Plan

### Phase 1: Data Model (0.5 days)
- Create users table migration
- Define SQLAlchemy User model
- Add password hashing with bcrypt

**Gate Criteria:**
- [ ] Migration runs successfully
- [ ] User model tests pass
- [ ] Hashing tests pass
- [ ] Coverage >= 80%

### Phase 2: Auth Service (1 day)
- Implement AuthService class
- Add register() method
- Add login() method
- Add token validation

[Test scaffolds for each]

### Phase 3: API Layer (1 day)
- Create FastAPI endpoints
- Add request/response validation
- Add error handling

### Phase4: Integration (0.5 days)
- End-to-end testing
- Performance verification
- Security audit

Do you approve this plan?
- 'yes' to proceed with implementation
- 'no' and I'll revise the approach
- Questions if anything is unclear

User: yes

Agent: Plan approved. Starting Phase 1: Data Model...
[Implementation begins]
```

## Integration with Other Skills

| Skill | When to Use |
|-------|-------------|
| `python-best-practices` | After plan approval, during implementation |
| `code-review-expert` | After implementation complete |
| `doc-maintenance` | After implementation complete |
| `workflow-development` | For complex features needing TDD workflow |

## Completion Checklist

- [ ] Workspace analyzed (tech-context.md, config, entry points)
- [ ] Existing patterns identified and followed
- [ ] User interviewed until spec 100% clear
- [ ] Multiple design options presented (min2)
- [ ] Tradeoffs documented for each option
- [ ] Recommendation made with justification
- [ ] Action plan created with phased todos
- [ ] Testable gates defined for each phase
- [ ] Plan document created in `docs/plan-*.md`
- [ ] Explicit approval obtained ("yes")
- [ ] Each phase executed with TDD (tests first)
- [ ] Gates verified before proceeding to next phase
- [ ] Commits created after each phase
- [ ] Documentation updated after completion