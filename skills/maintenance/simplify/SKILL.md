---
name: simplify
description: Apply project standards and Fowler refactoring smells to simplify code. Use ONLY when the user explicitly asks to simplify code.
---

# Code Simplification

Simplify code following project standards and recognized refactoring patterns. Only applies when explicitly requested by user.

## Non-Negotiable Rules

| Rule | Violation = STOP |
|------|------------------|
| Explicit request only | Block if not explicitly requested by user |
| No behavior change | Simplification must preserve exact behavior |
| Project standards | Follow existing patterns in codebase |
| Ask before edit | Request permission before each change |

## Refactoring Vocabulary

Use established Fowler terminology when it clarifies the finding. Prefer
evidence from the current code over a checklist of named smells. Common targets
include duplication, speculative generality, divergent change, long message
chains, feature envy, primitive obsession, and middle-man delegation.

## Workflow

### Step 1: Analyze Target Code

1. Read target file(s)
2. Identify simplification opportunities:
   - Duplicate code blocks
   - Overly complex conditionals
   - Unnecessary abstractions
   - Inconsistent naming
   - Fowler refactoring smells (see above)

### Step 2: Check Project Patterns

1. Search for similar patterns in codebase
2. Identify naming conventions
3. Check for existing utilities/abstractions

### Step 3: Propose Simplifications

For each proposed change, present:
- **File**: path/to/file.py
- **Line**: N
- **Smell**: which smell or issue identified
- **Current**: original code
- **Proposed**: simplified code
- **Reasoning**: why this simplification

### Step 4: Get User Approval

Ask: "Apply these simplifications? (yes/no/selective)"

- If "yes": Apply all simplifications
- If "no": Do nothing
- If "selective": Apply user-selected changes only
