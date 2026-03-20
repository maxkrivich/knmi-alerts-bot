---
description: Design a phased implementation plan with success criteria
---

You are entering the /plan phase of the ACE workflow. Your goal is to design a precise, phased implementation approach with clear success criteria — no code changes.

## Your Task

Plan the feature/change: $ARGUMENTS

## Process

### 1. Gather context
- Read all relevant files completely (no limit/offset)
- Use the Task tool for parallel exploration of related patterns
- Identify existing conventions and constraints
- Check `docs/research/` for any prior research artifacts

### 2. Present understanding and ask clarifying questions
Present what you've found:
```
Based on my research, I understand we need to [accurate summary].

I've found that:
- [Current implementation detail with file:line reference]
- [Relevant pattern or constraint]
- [Potential complexity or edge case]

Questions for you:
- [Specific technical question requiring human judgment]
- [Business logic clarification needed]
```
Only ask questions you cannot answer through code investigation.

### 3. Propose plan structure and get feedback
```
Here's my proposed plan structure:

## Phase 1: [Name] — [What it accomplishes]
## Phase 2: [Name] — [What it accomplishes]
## Phase 3: [Name] — [What it accomplishes]

Does this phasing make sense? Should I adjust the order or granularity?
```
Wait for feedback before writing the detailed plan.

### 4. Write detailed plan
Save to: `docs/plans/YYYY-MM-DD-<feature>.md`

Use this structure:
```markdown
# [Feature Name] Implementation Plan

## Overview
[What we're implementing and why]

## Current State Analysis
[What exists now, what's missing, key constraints]

## Desired End State
[Specification of desired end state and how to verify it]

## What We're NOT Doing
[Explicitly list out-of-scope items]

## Implementation Approach
[High-level strategy and reasoning]

## Phase 1: [Descriptive Name]

### Overview
[What this phase accomplishes]

### Changes Required

#### 1. [Component/File Group]
**File**: `path/to/file.ext`
**Changes**: [Summary of changes]

### Success Criteria

#### Automated Verification
- [ ] `make lint` passes
- [ ] `make check-format` passes
- [ ] `make check-ty` passes

#### Manual Verification
- [ ] [Feature works as expected]
- [ ] [Edge case handling verified]
- [ ] [No regressions in related features]

**Note**: After completing this phase and all automated verification passes,
pause for manual confirmation from the human before proceeding to Phase 2.

---

## Phase 2: [Descriptive Name]
[Similar structure...]

---

## Testing Strategy
[Unit tests, integration tests, manual testing steps]

## References
- Related research: `docs/research/[relevant].md`
- Similar implementation: `[file:line]`
```

### 5. Separate success criteria clearly
- **Automated**: `make lint`, `make check-format`, `make check-ty`, `make up` — run these first
- **Manual**: functionality, performance, edge cases — require human verification

### 6. Iterate on feedback
Adjust phasing, technical approach, scope, or success criteria based on user input.

## Guardrails

You MUST follow these rules:
- No file modifications — planning only
- No commands that change code
- Do not finalize the plan with unresolved questions
- Do not make assumptions without asking

When complete, present a summary and the path to the saved plan artifact.
