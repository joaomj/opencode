---
name: workflow-development
description: TDD-driven development workflow with chronological document ordering and testable gates
license: MIT
---

# Workflow Development

TDD-driven development process with strict document ordering, approval gates, and verification checkpoints.

## Non-Negotiable Rules (STOP if violated)

| Rule | Violation = STOP |
|------|-----------------|
| Test Driven Development (TDD) | Block if tests written AFTER implementation |
| Chronological document order | Block if order violated |
| Approval gates required | Block if skipped |
| AGENT must never read .env files | Block if attempted |

## Chronological Document Order for New Features

When building a new feature, you MUST follow this exact order:

### 1. Product Requirements Document (PRD)
**File:** `docs/prd-[feature-name].md`

**Purpose:** Define WHAT we're building and WHY

**Sections:**
- **Problem Statement**: What business problem are we solving?
- **Goals**: What does success look like?
- **User Stories**: Who are the users and what do they need?
- **Acceptance Criteria**: How do we know when we're done?
- **Constraints**: What are the technical, time, or resource constraints?
- **Success Metrics**: How will we measure success?

**Example:**
```markdown
# PRD: User Authentication

## Problem Statement
Users cannot securely access the application.

## Goals
- Enable users to register and login securely
- Support password reset functionality
- Ensure session security

## User Stories
- As a user, I want to register with email and password
- As a user, I want to login with my credentials
- As a user, I want to reset my forgotten password

## Acceptance Criteria
- User can register with valid email and password
- User receives confirmation email
- User can login with correct credentials
- User cannot login with incorrect credentials
- User can reset password via email

## Constraints
- Use OAuth 2.0 for authentication
- Passwords must be hashed using bcrypt
- Session tokens expire after 24 hours

## Success Metrics
- Registration completion rate: >80%
- Login success rate: >95%
- Time to register: <2 minutes
```

### 2. System Design Options
**File:** `docs/design-[feature-name].md`

**Purpose:** Define HOW we'll build it with tradeoffs

**Sections:**
- **Architecture Overview**: High-level system design
- **Design Options**: At least 2-3 approaches with pros/cons
- **Chosen Approach**: Which option selected and WHY
- **Component Diagrams**: Visual representation of components
- **Data Model**: Database schema changes (if any)
- **API Endpoints**: REST/gRPC endpoints (if any)
- **Security Considerations**: Security implications

**Example:**
```markdown
# System Design: User Authentication

## Architecture Overview
Authentication service using JWT tokens with session management.

## Design Options

### Option 1: Session-Based Authentication
**Pros:**
- Server-controlled sessions
- Easy to revoke sessions
- No JWT complexity

**Cons:**
- Requires session storage
- Doesn't scale well horizontally
- Requires sticky sessions

**Estimation**: 3 days
**Risk**: Low

### Option 2: JWT Tokens
**Pros:**
- Stateless - scales horizontally
- No session storage needed
- Easy to distribute

**Cons:**
- Harder to revoke tokens
- Token management complexity
- Refresh token rotation needed

**Estimation**: 2 days
**Risk**: Medium

### Option 3: OAuth 2.0 with External Provider
**Pros:**
- Delegated authentication
- No password management
- Social login support

**Cons:**
- Dependency on external service
- User data privacy concerns
- Implementation complexity

**Estimation**: 4 days
**Risk**: High

## Chosen Approach
**Option 2: JWT Tokens** - chosen for scalability and simplicity. Security concerns addressed with short-lived access tokens + refresh token rotation.

## Component Diagrams
[Component diagram showing: Auth Service, Token Store, User DB, API Gateway]

## Data Model
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP
);
```

## API Endpoints
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- POST /api/auth/logout

## Security Considerations
- Passwords hashed with bcrypt (cost factor 12)
- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days
- Refresh token rotation on every use
```

### 3. Technical Specifications
**File:** `docs/specs-[feature-name].md`

**Purpose:** Define the implementation details

**Sections:**
- **Detailed Component Specs**: Each component's responsibilities
- **Data Structures**: Detailed data models
- **Interface Contracts**: Function/method signatures
- **Error Handling**: Error codes and messages
- **Testing Strategy**: What tests will be written
- **Dependencies**: External services/libraries needed

**Example:**
```markdown
# Technical Specifications: User Authentication

## Component: AuthService

### Responsibilities
- User registration
- User authentication
- Token generation
- Token validation

### Interface
```python
class AuthService:
    def register(self, email: str, password: str) -> User:
        """Register a new user.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            Created user object

        Raises:
            DuplicateEmailError: If email already exists
            ValidationError: If email/password invalid
        """
        pass

    def login(self, email: str, password: str) -> AuthTokens:
        """Authenticate user and return tokens.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            AuthTokens with access_token and refresh_token

        Raises:
            InvalidCredentialsError: If credentials invalid
        """
        pass

    def validate_token(self, token: str) -> User:
        """Validate access token and return user.

        Args:
            token: JWT access token

        Returns:
            User object

        Raises:
            InvalidTokenError: If token invalid or expired
        """
        pass
```

## Data Structures
```python
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    email: str
    created_at: datetime

class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int  # seconds

class RegisterRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

## Error Codes
| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| AUTH_001 | Duplicate email | 409 Conflict |
| AUTH_002 | Invalid credentials | 401 Unauthorized |
| AUTH_003 | Invalid token | 401 Unauthorized |
| AUTH_004 | Token expired | 401 Unauthorized |

## Testing Strategy
- Unit tests for AuthService methods
- Integration tests for API endpoints
- Security tests for token validation
- Performance tests for authentication flow

## Dependencies
- bcrypt for password hashing
- pyjwt for JWT tokens
- pydantic for validation
```

### 4. Implementation Plan with Testable Gates
**File:** `docs/implementation-[feature-name].md`

**Purpose:** Define step-by-step implementation with verification

**Sections:**
- **Phase 1: Data Model**
  - Tasks
  - Tests to write (BEFORE implementation)
  - **Gate Criteria**: Tests pass, migration successful
- **Phase 2: Core Service**
  - Tasks
  - Tests to write (BEFORE implementation)
  - **Gate Criteria**: All unit tests pass
- **Phase 3: API Layer**
  - Tasks
  - Tests to write (BEFORE implementation)
  - **Gate Criteria**: Integration tests pass
- **Phase 4: Integration**
  - Tasks
  - Tests to write (BEFORE implementation)
  - **Gate Criteria**: End-to-end tests pass

**Example:**
```markdown
# Implementation Plan: User Authentication

## Phase 1: Data Model
**Estimation**: 0.5 days

### Tasks
1. Create users table migration
2. Create refresh_tokens table migration
3. Define SQLAlchemy models
4. Add indexes for email lookup

### Tests to Write (BEFORE implementation)
```python
# test_models.py
def test_user_creation():
    user = User(email="test@example.com", password_hash="hash")
    assert user.email == "test@example.com"

def test_user_email_unique():
    # Test duplicate email constraint
    pass

def test_refresh_token_expires():
    # Test token expiration
    pass
```

### Gate Criteria
- [ ] All database migrations created
- [ ] All model unit tests pass
- [ ] Email uniqueness constraint enforced
- [ ] Indexes created and verified

## Phase 2: Core Service
**Estimation**: 1 day

### Tasks
1. Implement password hashing with bcrypt
2. Implement AuthService.register()
3. Implement AuthService.login()
4. Implement AuthService.validate_token()
5. Add JWT token generation
6. Add refresh token rotation

### Tests to Write (BEFORE implementation)
```python
# test_auth_service.py
def test_register_success():
    service = AuthService(db)
    user = service.register("test@example.com", "password123")
    assert user.email == "test@example.com"

def test_register_duplicate_email():
    service = AuthService(db)
    service.register("test@example.com", "password123")
    with pytest.raises(DuplicateEmailError):
        service.register("test@example.com", "different123")

def test_login_success():
    service = AuthService(db)
    service.register("test@example.com", "password123")
    tokens = service.login("test@example.com", "password123")
    assert tokens.access_token
    assert tokens.refresh_token

def test_login_invalid_credentials():
    service = AuthService(db)
    with pytest.raises(InvalidCredentialsError):
        service.login("test@example.com", "wrongpassword")

def test_validate_token_success():
    service = AuthService(db)
    tokens = service.login("test@example.com", "password123")
    user = service.validate_token(tokens.access_token)
    assert user.email == "test@example.com"

def test_validate_token_expired():
    # Test expired token rejection
    pass
```

### Gate Criteria
- [ ] All unit tests pass (pytest)
- [ ] Code coverage > 80%
- [ ] No security warnings (bandit)
- [ ] Lint passes (ruff check)

## Phase 3: API Layer
**Estimation**: 1 day

### Tasks
1. Create FastAPI endpoints
2. Add request/response validation
3. Add error handling
4. Add rate limiting
5. Add CORS configuration

### Tests to Write (BEFORE implementation)
```python
# test_api.py
def test_register_endpoint():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()

def test_login_endpoint():
    # Test login endpoint
    pass

def test_invalid_email_format():
    response = client.post("/api/auth/register", json={
        "email": "invalid-email",
        "password": "password123"
    })
    assert response.status_code == 422

def test_short_password():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "short"
    })
    assert response.status_code == 422
```

### Gate Criteria
- [ ] All API integration tests pass
- [ ] OpenAPI spec validates
- [ ] Rate limiting works
- [ ] CORS configured correctly

## Phase 4: Integration
**Estimation**: 0.5 days

### Tasks
1. End-to-end testing
2. Performance testing
3. Security audit
4. Documentation updates

### Tests to Write (BEFORE implementation)
```python
# test_e2e.py
def test_full_auth_flow():
    # Register
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    tokens = response.json()

    # Login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200

    # Access protected endpoint
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_token_refresh():
    # Test refresh token rotation
    pass
```

### Gate Criteria
- [ ] All end-to-end tests pass
- [ ] Performance meets requirements (<100ms for login)
- [ ] Security audit passes (no critical issues)
- [ ] API documentation updated
- [ ] tech-context.md updated with CRISP-DM documentation

## Completion Criteria
- [ ] All gate criteria met
- [ ] Documentation updated in docs/tech-context.md
- [ ] Pre-commit hooks pass
- [ ] Code reviewed and approved
```

## Test Driven Development (TDD)

### TDD Cycle
1. **RED**: Write a failing test
2. **GREEN**: Write minimal code to pass the test
3. **REFACTOR**: Improve the code while keeping tests green

### Rules
- **Prefer test-first** for business logic, domain rules, and bug fixes
- **Test-after is acceptable** for spikes, config-only work, and refactors with existing coverage
- **For bug fixes**, add a regression test that reproduces the bug before finalizing
- **Verify-first always**: prove behavior with automated checks before building further

### Example
```python
# Step 1: Write failing test (RED)
def test_register_duplicate_email():
    service = AuthService(db)
    service.register("test@example.com", "password123")
    with pytest.raises(DuplicateEmailError):
        service.register("test@example.com", "different123")

# Step 2: Run test - it FAILS (RED)
# pytest test_auth_service.py::test_register_duplicate_email
# FAILED

# Step 3: Write minimal code to pass test (GREEN)
def register(self, email: str, password: str) -> User:
    # Check if user exists
    existing_user = self.db.query(User).filter_by(email=email).first()
    if existing_user:
        raise DuplicateEmailError(f"Email {email} already exists")

    # Create user
    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )
    user = User(email=email, password_hash=hashed_password)
    self.db.add(user)
    self.db.commit()
    return user

# Step 4: Run test - it PASSES (GREEN)
# pytest test_auth_service.py::test_register_duplicate_email
# PASSED

# Step 5: Refactor if needed (REFACTOR)
# Improve code structure, extract methods, etc.
# Keep tests green
```

## Approval Gates

### Before Each Phase
1. **Write phase tests** (BEFORE any implementation)
2. **Review plan** with user
3. **Get explicit approval**: "Shall I proceed with Phase X?"

### After Each Phase
1. **Run all tests**: `pytest`
2. **Verify gate criteria** are met
3. **Commit changes**: `git commit -m "Phase X: <description>"`
4. **Ask for approval**: "Phase X complete. Proceed to Phase X+1?"

## Todo Tracking

### Using TodoWrite
For tasks with 3+ steps, use TodoWrite to track progress:

```python
# Example usage
todowrite([
    {"content": "Write PRD for authentication", "status": "completed", "priority": "high"},
    {"content": "Write system design options", "status": "completed", "priority": "high"},
    {"content": "Write technical specifications", "status": "in_progress", "priority": "high"},
    {"content": "Create implementation plan with gates", "status": "pending", "priority": "high"},
    {"content": "Get user approval for implementation", "status": "pending", "priority": "high"},
])
```

### Rules
- Mark tasks as `completed` immediately after finishing
- Only have ONE task as `in_progress` at a time
- Complete current tasks before starting new ones

## Post-Code Verification

### After Implementation
1. **Type hints added**: All functions have proper type hints
2. **Error handling**: Specific exceptions, no bare except
3. **Tests written**: All functionality covered by tests
4. **Lint passes**: `ruff check .`
5. **Tests pass**: `pytest`
6. **Pre-commit hooks**: `pre-commit run --all-files` (if installed)
7. **Documentation updated**: `/skill doc-maintenance`

### Pre-Commit Hooks (OPTIONAL)
If `setup-hooks.sh` is missing, ask user before installing:

```
"Pre-commit hooks are not configured. Would you like me to install them?
This will add quality checks (linting, secrets detection, file length) to your git workflow."
```

Only run `curl -sSL https://raw.githubusercontent.com/joaomj/opencode/main/setup-hooks.sh | bash` if user confirms "yes".

## AGENT Restrictions

### Never Read .env Files
- AGENT must never use Read tool on `.env` files
- Application code can load `.env` files
- Use environment variables for configuration
- Keep secrets secure

## Workflow Summary

### For New Features:
1. Write PRD
2. Write System Design Options (with tradeoffs)
3. Write Technical Specifications
4. Write Implementation Plan (with testable gates)
5. Get user approval
6. Implement Phase 1 (TDD: write tests FIRST)
7. Verify Phase 1 gate criteria
8. Commit Phase 1
9. Get approval for Phase 2
10. Repeat 6-9 for all phases
11. Run post-code verification
12. Run `/skill doc-maintenance`

### For Bug Fixes:
1. Reproduce bug (write test that fails)
2. Write test that exposes bug (TDD)
3. Fix bug (minimal code)
4. Verify test passes
5. Add regression tests
6. Run verification checklist

## Completion Checklist

- [ ] Chronological document order followed (PRD → Design → Specs → Implementation)
- [ ] Tests written BEFORE implementation (TDD)
- [ ] All gate criteria met
- [ ] Approval obtained before each phase
- [ ] All tests pass (pytest)
- [ ] Lint passes (ruff check)
- [ ] Type hints added
- [ ] Error handling proper
- [ ] Documentation updated
- [ ] Pre-commit hooks installed only with user consent
- [ ] AGENT never read `.env` files
