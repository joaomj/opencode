---
name: simplify
description: Apply project standards to simplify code. Use ONLY when the user explicitly asks to simplify code.
license: MIT
---

# Code Simplification

Simplify code following project standards. Only applies when explicitly requested by user.

## Non-Negotiable Rules

| Rule | Violation = STOP |
|------|------------------|
| Explicit request only | Block if not explicitly requested by user |
| No behavior change | Simplification must preserve exact behavior |
| Project standards | Follow existing patterns in codebase |
| Ask before edit | Request permission before each change |

## Workflow

### Step 1: Analyze Target Code

1. Read target file(s)
2. Identify simplification opportunities:
   - Duplicate code blocks
   - Overly complex conditionals
   - Unnecessary abstractions
   - Inconsistent naming

### Step 2: Check Project Patterns

1. Search for similar patterns in codebase
2. Identify naming conventions
3. Check for existing utilities/abstractions

### Step 3: Propose Simplifications

For each proposed change, present:

- **File**: path/to/file.py
- **Line**: N
- **Current**: original code
- **Proposed**: simplified code
- **Reasoning**: why this simplification
- **Impact**: what changes — behavior must be identical

### Step 4: Get User Approval

Ask: "Apply these simplifications? (yes/no/selective)"

- If "yes": Apply all simplifications
- If "no": Do nothing
- If "selective": Apply user-selected changes only
