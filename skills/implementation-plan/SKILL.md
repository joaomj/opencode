---
name: implementation-planning
description: Propose and design implementation plans with workspace analysis, user interview, systems design, tradeoffs analysis, and approval gates before any code changes
license: MIT
---

# Implementation Planning

Design implementation plans following the investigate-first principle: NEVER edit without approval. Analyze, design, discuss tradeoffs, then plan with strict phase-gate structure.

## Non-Negotiable Rules (STOP if violated)

|Rule | Violation = STOP |
|------|------------------|
| investigate-first | Block if implementation starts before analysis complete |
| design-before-tradeoffs | Block if tradeoffs discussed before architecture defined |
| tradeoffs-before-plan | Block if plan created before options compared |
| approval-gate | Block if execution begins without explicit "yes" |
| consistency-check | Block if new code violates existing patterns |
| spec-clarity | Block if requirements are ambiguous or incomplete |

## When to Use This Skill vs Others

| Skill | Use When |
|-------|----------|
| `implementation-planning` | ANY implementation request (small or large). Quick planning, user interview, architecture design, tradeoffs, approval. |
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

**Goal:** Achieve 100% specification clarity before design.

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

### Phase 3: Systems Design & Architecture

**Goal:** Define the technical architecture BEFORE discussing implementation options.

#### Step3.1: Identify System Components

Map out the high-level architecture:

```
System Architecture Overview:

[Component A]
  ↓ [interface/data flow]
[Component B]
  ↓ [interface/data flow]
[Component C]
```

Questions to answer:
- What are the major components/modules?
- How do they interact?
- What are the interfaces/contracts between them?
- Where does this feature fit in the existing system?

#### Step3.2: Define Data Flow

Trace data through the system:

```
Input → [Validation] → [Processing] → [Storage] → [Output]
         ↓                ↓              ↓
      Errors          Metrics       Side effects
```

#### Step3.3: Identify Technical Constraints

List constraints that will limit implementation options:

| Constraint | Impact |
|------------|--------|
| Existing database schema | Must work with current tables |
| API compatibility | Must not break existing endpoints |
| Authentication system | Must use existing auth mechanism |
| Deployment environment | Must run in current infra |

**Gate:** Architecture must be defined and documented before proposing implementation options.

### Phase 4: Tradeoffs Analysis

**Goal:** Compare implementation approaches. This is for decision-making ONLY - do NOT include pros/cons in the final plan document.

#### Step4.1: Design Options

Propose at least 2-3 approaches based on the architecture:

| Approach | Description |
|----------|-------------|
| Option A | [brief description] |
| Option B | [brief description] |
| Option C | [brief description] |

For each option, discuss:
- **Pros:** Why this approach works
- **Cons:** Tradeoffs and risks
- **Fit with architecture:** How well it aligns with Step 3

#### Step 4.2: Recommendation

After presenting options, recommend one:

```
"Recommended: Option X because [reason].

Alternatives considered:
- Option Y: [why not chosen]
- Option Z: [why not chosen]"
```

#### Step 4.3: Get Consensus

Confirm the chosen approach before creating the plan:

```
"Based on the architecture and tradeoffs, I recommend Option X.

Do you agree with this approach, or would you prefer a different option?"
```

**IMPORTANT:** Pros, cons, and tradeoffs stay HERE in Phase 4. They do NOT go into the final plan document.

### Phase 5: Action Plan

**Goal:** Create structured implementation plan with phases, gates, tests, and commits.

#### Step 5.1: Define Implementation Phases

Break work into logical phases. Each phase must:
- Have a clear objective
- Be testable independently
- Produce working code
- Have explicit gate criteria

**Phase Structure:**

```markdown
### Phase N: [Phase Name]

**Objective:** [What this phase accomplishes]

#### Implementation Tasks
1. [Specific task]
2. [Specific task]
3. [Specific task]

#### Tests to Write (BEFORE implementation)
Write these tests first, then implement to make them pass:

```python
# test_module.py
def test_feature_basic_functionality():
    """Test: [what it verifies]"""
    # Arrange
    # Act
    # Assert
    pass

def test_feature_edge_case_empty_input():
    """Test: [what it verifies]"""
    pass

def test_feature_error_handling():
    """Test: [what it verifies]"""
    pass
```

#### Gate Criteria (ALL must pass to proceed)
- [ ] All new tests pass
- [ ] Code coverage >= 80% for new code
- [ ] Lint/type checks pass
- [ ] Code follows existing patterns
- [ ] No breaking changes to existing tests

#### Verification Commands
```bash
# Run tests
pytest tests/test_module.py -v --cov=src/module --cov-fail-under=80

# Run lint
ruff check src/module

# Run type check
mypy src/module
```

#### Commit Trigger
After gate criteria pass: `/commit` with message: "feat: [phase objective]"
```

#### Step 5.2: Create Phased Todo List

Use `TodoWrite` to track progress:

```python
todowrite([
    {"content": "Phase 1: [objective]", "status": "pending", "priority": "high"},
    {"content": "Phase 2: [objective]", "status": "pending", "priority": "high"},
    {"content": "Phase 3: [objective]", "status": "pending", "priority": "high"},
])
```

#### Step 5.3: Write Plan Document

Create `docs/plan-[feature-name].md` with STRICT format:

```markdown
# Implementation Plan: [Feature Name]

## Summary
[1-2 sentences of what and why]

## Requirements
- [requirement 1]
- [requirement 2]
- [requirement 3]

## Architecture Overview
[High-level description of system design from Phase 3]

```
[Component diagram or description]
```

## Chosen Approach
**[Option Name]** - [One-line description]

[Why this approach was selected - 2-3 sentences max]

## Implementation Phases

### Phase 1: [Phase Name]

**Objective:** [Clear statement of what this phase delivers]

#### Implementation Tasks
1. [Task 1]
2. [Task 2]
3. [Task 3]

#### Tests to Write (TDD - BEFORE implementation)
```python
# File: tests/test_[module].py

def test_[feature]_[scenario]():
    """[What this test verifies]"""
    pass

def test_[feature]_[edge_case]():
    """[What this test verifies]"""
    pass
```

#### Gate Criteria
- [ ] [Criterion 1 - specific and verifiable]
- [ ] [Criterion 2 - specific and verifiable]
- [ ] [Criterion 3 - specific and verifiable]

#### Verification Commands
```bash
[Commands to verify gate criteria]
```

#### Commit Trigger
`feat: [brief description of phase outcome]`

---

### Phase 2: [Phase Name]
[Same structure as Phase 1]

---

### Phase N: Integration & Final Verification

**Objective:** Ensure all phases work together correctly

#### Implementation Tasks
1. Integration testing
2. End-to-end verification
3. Final review

#### Tests to Write
```python
# Integration tests
```

#### Gate Criteria
- [ ] All phases integrated successfully
- [ ] Full test suite passes
- [ ] Overall coverage >= 80%
- [ ] No regressions in existing functionality

#### Verification Commands
```bash
pytest tests/ -v --cov=src --cov-fail-under=80
```

#### Commit Trigger
`feat: complete [feature name] implementation`

## Success Criteria
- [ ] All gate criteria met for all phases
- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] Lint passes
- [ ] No breaking changes
```

**IMPORTANT RULES for Plan Document:**
- NO time estimates anywhere
- NO pros/cons tables in final plan
- NO alternative approaches in final plan
- MUST include test code examples for each phase
- MUST specify exact gate criteria
- MUST specify commit trigger for each phase
- Architecture section is REQUIRED before implementation phases

### Phase 6: Approval Gate

**Goal:** Wait for explicit "yes" before execution.

#### Step6.1: Present Plan

Show the complete plan to the user:

```
"I've created an implementation plan following our architecture discussion.

Plan highlights:
- [Number] implementation phases
- Each phase has mandatory tests (TDD)
- Clear gate criteria between phases
- Commits after each successful gate

The plan document is at: docs/plan-[feature-name].md

Do you approve this plan? Please respond with:
- 'yes' to proceed with implementation
- 'no' and I'll revise the approach
- Questions if anything is unclear"
```

#### Step 6.2: Wait for Approval

**CRITICAL**: 
- Do NOT start implementation until user says "yes" (or equivalent approval)
- If user has questions, answer them and re-present the approval gate
- If user says "no", return to Phase 3, 4, or 5 as appropriate

#### Step 6.3: Approval Confirmation

After approval, confirm:

```
"Plan approved. I'll implement using strict TDD methodology:
1. Write tests FIRST
2. Implement to pass tests
3. Verify gate criteria
4. Commit after each phase

Starting Phase 1: [Phase Name]"
```

### Phase 7: Implementation Execution

**Goal:** Execute plan with strict phase-gate-commit discipline.

#### Step 7.1: Execute Phase by Phase

For each phase:

1. **Write tests FIRST** (TDD): Create failing tests based on plan
2. **Implement**: Write minimal code to pass tests
3. **Verify**: Run all verification commands from plan
4. **Check gates**: Verify ALL gate criteria pass
5. **Commit**: Use `/commit` with specified trigger message
6. **Confirm**: Ask "Phase X complete. Proceed to Phase X+1?"

**CRITICAL:** Do NOT proceed to next phase until current phase gates pass.

#### Step 7.2: Gate Enforcement

**MANDATORY**: Do NOT proceed to next phase until:

- [ ] All phase tests pass
- [ ] Coverage meets threshold (>=80%)
- [ ] Lint passes
- [ ] Type checks pass (if applicable)
- [ ] All gate criteria from plan are verified
- [ ] Commit created with specified message

#### Step 7.3: Handle Deviations

If implementation reveals issues:

1. **STOP** - Do not proceed
2. **Document** - Note the issue
3. **Ask** - Get user guidance
4. **Update plan** - Revise if needed
5. **Get renewed approval** - Confirm before continuing

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
- **Commit the plan document** after approval

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

User: JWT tokens

Agent: JWT tokens with refresh token rotation. Any constraints on:
- Token expiration time?
- Password requirements?

User: 15min access tokens, 7-day refresh tokens. Min 8 chars password.

Agent: Let me confirm my understanding:
- Email/password authentication with bcrypt
- JWT tokens (15min access, 7day refresh)
- Refresh token rotation for security
- Min 8 char passwords

Is this correct? Anything to add or modify?

User: Yes, that's correct

Agent: [Phase 3: Systems Design & Architecture]
Based on your requirements, here's the system architecture:

Components:
1. User Model (extends existing)
2. Auth Service (handles login/register/validation)
3. JWT Manager (token generation/validation)
4. API Endpoints (FastAPI routes)
5. Middleware (token verification)

Data Flow:
Login Request → Validation → Auth Service → JWT Manager → Tokens
API Request → Middleware → Token Validation → Endpoint Handler

Integration Points:
- Extends existing User model in src/models/user.py
- Adds auth routes to existing FastAPI app
- Uses existing database connection

Does this architecture look correct?

User: Yes, that makes sense

Agent: [Phase 4: Tradeoffs Analysis]
Now let's compare implementation approaches:

**Option A: JWT with refresh rotation**
- Pros: Stateless, scalable, secure token revocation via rotation
- Cons: More complex implementation, need refresh token storage
- Fits architecture: Excellent - matches your scalability needs

**Option B: Session-based auth**
- Pros: Simple implementation, easy revocation
- Cons: Requires database storage per session, harder to scale horizontally
- Fits architecture: Poor - contradicts scalability requirement

**Option C: OAuth only**
- Pros: No password management, external auth
- Cons: Dependency on external services, limited to OAuth providers
- Fits architecture: Poor - you specified email/password

**Recommendation: Option A** (JWT with refresh rotation)
- Best fit for your architecture and requirements
- Scalable as you requested
- Industry standard for this use case

Do you agree with this approach?

User: Yes, Option A sounds good

Agent: [Phase 5: Action Plan]
Great! Here's the implementation plan:

Plan document created at: docs/plan-user-auth.md

**Phase 1: User Model & Password Hashing**
- Objective: Extend user model with password support
- Tests first: User creation, password hashing, validation
- Gate: Model tests pass, coverage >= 80%
- Commit trigger: "feat: add user model with password hashing"

**Phase 2: JWT Token Manager**
- Objective: Implement token generation and validation
- Tests first: Token creation, validation, expiration
- Gate: JWT tests pass, coverage >= 80%
- Commit trigger: "feat: implement JWT token manager"

**Phase 3: Auth Service**
- Objective: Business logic for login/register/refresh
- Tests first: Login flow, registration, token refresh
- Gate: Service tests pass, coverage >= 80%
- Commit trigger: "feat: add authentication service"

**Phase 4: API Endpoints**
- Objective: FastAPI routes for auth operations
- Tests first: Endpoint tests with client
- Gate: All API tests pass, coverage >= 80%
- Commit trigger: "feat: add authentication endpoints"

**Phase 5: Integration**
- Objective: End-to-end verification
- Tests first: Full auth flow integration tests
- Gate: Integration tests pass, no regressions
- Commit trigger: "feat: complete user authentication"

Do you approve this plan? (respond with 'yes', 'no', or questions)

User: yes

Agent: [Phase 7: Implementation Execution]
Plan approved. Committing plan document and starting Phase 1.

[Commits docs/plan-user-auth.md]

Starting Phase 1: User Model & Password Hashing

**Step 1: Write tests (TDD)**
[Shows test code from plan]

**Step 2: Implement**
[Implements to pass tests]

**Step 3: Verify gate criteria**
Running: pytest tests/test_models.py -v --cov=src/models --cov-fail-under=80
Output: All tests pass, coverage 85%

Gate criteria met:
- [x] All tests pass
- [x] Coverage >= 80%
- [x] Lint passes

**Step 4: Commit**
/commit "feat: add user model with password hashing"

Phase 1 complete. Proceed to Phase 2: JWT Token Manager?
```

## Integration with Other Skills

| Skill | When to Use |
|-------|-------------|
| `python-best-practices` | After plan approval, during implementation |
| `code-review-expert` | After implementation complete |
| `doc-maintenance` | After implementation complete |
| `workflow-development` | For complex features needing additional TDD workflow |

## Completion Checklist

- [ ] Workspace analyzed (tech-context.md, config, entry points)
- [ ] Existing patterns identified and followed
- [ ] User interviewed until spec 100% clear
- [ ] System architecture defined and documented (Phase 3)
- [ ] Multiple design options compared with pros/cons (Phase 4)
- [ ] Recommendation made with justification
- [ ] Consensus reached on approach
- [ ] Action plan created with strict format (Phase 5)
- [ ] Plan includes: phases → gates → tests → commits
- [ ] NO time estimates in plan
- [ ] NO pros/cons in final plan document
- [ ] Plan document created in `docs/plan-*.md`
- [ ] Explicit approval obtained ("yes")
- [ ] Plan document committed after approval
- [ ] Each phase executed with TDD (tests first)
- [ ] Gates verified before proceeding to next phase
- [ ] Commits created after each phase with specified messages
- [ ] Documentation updated after completion
