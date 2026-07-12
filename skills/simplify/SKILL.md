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

## Refactoring Smells (Fowler)

Use these code smells from Martin Fowler's *Refactoring* when analyzing code. The agent already knows these deeply from training — invoking the terminology is enough.

| Smell | What to look for | How to fix |
|-------|-----------------|------------|
| Mysterious Name | Function/variable name doesn't reveal its purpose | Rename it; if no honest name comes, the design is murky |
| Duplicated Code | Same logic shape appears in multiple places | Extract the shared shape, call it from both |
| Feature Envy | Method reaches into another object's data more than its own | Move the method onto the data it envies |
| Data Clumps | Same few fields/params travel together | Bundle them into one type |
| Primitive Obsession | Primitive/string standing in for a domain concept | Give the concept its own small type |
| Repeated Switches | Same switch/if-cascade on the same type recurs | Replace with polymorphism or a shared map |
| Divergent Change | One module edited for several unrelated reasons | Split so each module changes for one reason |
| Speculative Generality | Abstraction added for needs that don't exist | Delete it; inline back until a real need shows |
| Message Chains | Long a.b().c().d() navigation | Hide the walk behind one method on the first object |
| Middle Man | Class/function that mostly just delegates onward | Cut it, call the real target directly |

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
