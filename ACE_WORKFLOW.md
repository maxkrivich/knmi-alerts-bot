# ACE_WORKFLOW.md - Advanced Context Engineering Workflow Details

This document contains the detailed instructions for the three phases of the Advanced Context Engineering workflow referenced in `AGENTS.md`.

## Table of Contents
1. [Workflow Philosophy](#workflow-philosophy)
2. [/research Phase](#research-phase)
3. [/plan Phase](#plan-phase)
4. [/implement Phase](#implement-phase)

---

## Workflow Philosophy

This follows **Frequent Intentional Compaction** principles:
- **Research** distills codebase understanding into structured artifacts (file references, patterns, dependencies)
- **Planning** turns understanding into concrete, phased steps with measurable success criteria
- **Implementation** executes phases sequentially with human verification between phases
- **Context windows** stay at 40-60% utilization through deliberate compaction at each phase boundary

Key insight: The workflow is not about "magic prompts" - it's about thoughtful structure that keeps both humans and AI focused on the right problems at the right time.

---

## /research Phase

### Purpose
Understand current behavior and document what exists without suggesting improvements.

### Key Principles
- **Document only** - describe the current state, not what should be
- **Be concrete** - include specific file paths and line numbers
- **Be thorough** - use parallel exploration for efficiency
- **Preserve context** - include temporal information and architectural patterns

### Research Process

#### 1. Break down the research question into composable areas
Using TodoWrite, decompose the question:
- Identify specific components, patterns, or concepts to investigate
- Consider which directories and files are relevant
- Plan which aspects require parallel investigation

#### 2. Use parallel exploration
Launch multiple independent investigations:
- Use the Task tool with `explore` agent for codebase pattern discovery
- Search for related implementations, configurations, and patterns
- Identify dependencies and integration points
- Run searches in parallel to keep context usage low

#### 3. Synthesize findings into a research document
Structure your findings:
- **Summary** - High-level overview answering the research question
- **Detailed Findings** - Component-by-component breakdown
- **Code References** - Specific file paths with line numbers
- **Architectural Patterns** - Conventions and design decisions found
- **Historical Context** - Past decisions or design notes (if available)

#### 4. Create research artifact
Save at: `docs/research/YYYY-MM-DD-<topic>.md`
- Use clear frontmatter with date, topic, and status
- Self-contained documentation suitable for reference
- Include all necessary context without requiring external files
- Can be reviewed and discussed before planning

### Research Guardrails
✅ Reading code, analyzing patterns, searching files
✅ Documenting current behavior with file references
✅ Creating structured research artifacts
✅ Using TodoWrite to track decomposition
✅ Running parallel Task explorations

❌ Modifying any source, test, or config files
❌ Running mutating commands
❌ Suggesting improvements or changes
❌ Critiquing the implementation

---

## /plan Phase

### Purpose
Design a precise, phased approach with clear success criteria - no code changes.

### Key Principles
- **Be specific** - every phase must have concrete, measurable success criteria
- **Be incremental** - break work into small, testable phases
- **Be interactive** - get user feedback at major decision points
- **Be complete** - no open questions in the final plan

### Planning Process

#### 1. Gather context before creating the plan
- Read all mentioned files completely (no limit/offset)
- Use parallel exploration to understand relevant code patterns
- Document current implementation and identify constraints
- Understand existing conventions and patterns

#### 2. Present understanding and ask clarifying questions
```
Based on my research, I understand we need to [accurate summary].

I've found that:
- [Current implementation detail with file:line reference]
- [Relevant pattern or constraint discovered]
- [Potential complexity or edge case identified]

Questions for you:
- [Specific technical question that requires human judgment]
- [Business logic clarification needed]
- [Design preference that affects implementation]
```
Only ask questions you cannot answer through code investigation.

#### 3. Create plan structure with user feedback
Propose the phasing:
```
Here's my proposed plan structure:

## Phase 1: [Name] - [What it accomplishes]
## Phase 2: [Name] - [What it accomplishes]
## Phase 3: [Name] - [What it accomplishes]

Does this phasing make sense? Should I adjust the order or granularity?
```

Get feedback before writing detailed plan.

#### 4. Write detailed plan
Save at: `docs/plans/YYYY-MM-DD-<feature>.md`

Structure:
```markdown
# [Feature Name] Implementation Plan

## Overview
[Brief description of what we're implementing and why]

## Current State Analysis
[What exists now, what's missing, key constraints discovered]

## Desired End State
[A Specification of the desired end state and how to verify it]

## What We're NOT Doing
[Explicitly list out-of-scope items to prevent scope creep]

## Implementation Approach
[High-level strategy and reasoning]

## Phase 1: [Descriptive Name]

### Overview
[What this phase accomplishes]

### Changes Required

#### 1. [Component/File Group]
**File**: `path/to/file.ext`
**Changes**: [Summary of changes]

```[language]
// Specific code to add/modify
```

### Success Criteria

#### Automated Verification
- [ ] `make lint` passes
- [ ] `make check-format` passes
- [ ] `make check-ty` passes
- [ ] [Any other automated checks from AGENTS.md]

#### Manual Verification
- [ ] [Feature works as expected when tested via UI/CLI]
- [ ] [Performance is acceptable under expected load]
- [ ] [Edge case handling verified manually]
- [ ] [No regressions in related features]

**Note**: After completing this phase and all automated verification passes,
pause here for manual confirmation from the human before proceeding to Phase 2.

---

## Phase 2: [Descriptive Name]
[Similar structure with both automated and manual success criteria...]

---

## Testing Strategy

### Unit Tests
- [What to test]
- [Key edge cases]

### Integration Tests
- [End-to-end scenarios]

### Manual Testing Steps
1. [Specific step to verify feature]
2. [Another verification step]
3. [Edge case to test manually]

## References
- Original ticket/issue: [Link or reference]
- Related research: `docs/research/[relevant].md`
- Similar implementation: `[file:line]`
```

#### 5. Separate success criteria into two categories

**Automated Verification** (can be run immediately):
- Static checks: `make lint`, `make check-format`, `make check-ty`
- Runtime verification: `make up` (if applicable)
- These must pass before manual testing

**Manual Verification** (requires human testing):
- Functionality tests described in PRODUCT.md
- Performance testing if applicable
- Edge case validation
- Integration verification

**Important**: Always separate these clearly. Automated checks should use `make` commands whenever possible.

#### 6. Iterate based on feedback
- Add missing phases
- Adjust technical approach
- Clarify success criteria
- Add/remove scope items
- Refine based on user input

### Planning Guardrails
✅ Reading code and documentation
✅ Using Task tool for parallel exploration
✅ Creating detailed, phased plans
✅ Getting user feedback at decision points
✅ Separating automated vs manual verification

❌ Modifying any files
❌ Running commands that change code
❌ Finalizing plan with unresolved questions
❌ Making assumptions without asking

---

## /implement Phase

### Purpose
Execute the approved plan phase-by-phase while adapting to reality when necessary.

### Key Principles
- **Follow the plan intent** - understand the goals while adapting to what you find
- **Implement completely** - finish each phase fully before moving to the next
- **Verify thoroughly** - run all success criteria before moving forward
- **Communicate clearly** - pause when reality conflicts with the plan

### Implementation Process

#### 1. Understand the plan
- Read the complete plan document
- Check for any existing progress (✓ marks)
- Read all files mentioned in the plan
- Create a TodoWrite list for the phases

#### 2. Execute Phase N
- Implement all changes specified in the phase
- Update plan checkboxes as you complete sections using Edit tool
- Follow the code standards in AGENTS.md section 7
- Track progress in TodoWrite

#### 3. Run automated verification
```bash
make lint
make check-format
make check-ty
# And any other checks specified in the plan
```
- If checks fail, fix issues and re-run
- Do not proceed to manual verification until all checks pass

#### 4. Pause for human manual verification
After all automated checks pass, present status:
```
Phase [N] Complete - Ready for Manual Verification

Automated verification passed:
- ✅ make lint
- ✅ make check-format
- ✅ make check-ty

Please perform the manual verification steps from the plan:
- [ ] [Step 1 from plan]
- [ ] [Step 2 from plan]
- [ ] [Step 3 from plan]

Reply when manual testing is complete so I can proceed to Phase [N+1].
```

**Key**: Do not check off manual verification items until confirmed by the user.

#### 5. Handle plan conflicts
If the actual codebase differs from the plan:
```
Issue in Phase [N]:
Expected: [what the plan says]
Found: [actual situation]
Why this matters: [explanation]

How should I proceed?
```
Wait for human guidance before deviating from the plan.

#### 6. Repeat phases until complete
- Update todos as you complete each phase
- Run all verification steps
- Pause for manual verification between phases (unless told to execute consecutively)

### Implementation Guardrails
✅ Implementing changes according to the plan
✅ Running static checks and verification
✅ Pausing for human manual verification
✅ Using Edit tool to update plan checkboxes
✅ Asking for guidance when conflicts arise

❌ Skipping verification steps
❌ Ignoring plan conflicts without asking
❌ Making changes outside the approved plan scope
❌ Forcing checks to pass by bypassing quality gates

---

## Context Window Management

Target utilization: 40-60% per phase

- **Research Phase**: 20-40% typical utilization
  - Produce compact research document
  - Can reset context before planning

- **Planning Phase**: 30-50% typical utilization
  - Produce compact implementation plan
  - Can reset context before implementation

- **Implementation Phase**: 40-60% typical utilization
  - Execute verified plan
  - Mark completions atomically
  - Can reset between phases if needed

---

## Integration with OpenCode Features

### TodoWrite
- Track research decomposition into subtasks
- Mark planning steps as you create structure
- Track implementation phases
- Full visibility into progress

### Task Tool with Explore Agent
- Run parallel research across codebase
- Efficient file discovery and pattern identification
- Clean context management with focused returns
- Reusable searches across team

### Edit Tool
- Atomic updates to plan checkboxes
- Mark success criteria as they pass
- Preserve progress across context resets

### Native Verification
- `make lint`, `make check-format`, `make check-ty`
- `make up` for runtime testing
- Clear pass/fail gates

---

## Real-World Results

Based on testing with 300k LOC Rust codebases (BAML project):
- Bug fixes shipped in <2 hours
- Complex features shipped in one day
- Code quality passed expert review
- No "slop" or rework needed

The workflow prevents:
- Wrong assumptions (research grounds understanding)
- Scope creep (planning defines boundaries)
- Surprises (conflicts surface early)
- Lost work (artifacts preserve progress)

---

## Sources & References

- **Advanced Context Engineering**: https://github.com/humanlayer/advanced-context-engineering-for-coding-agents
- **HumanLayer Workflow**: Real-world patterns from production use
- **Frequent Intentional Compaction**: Context management technique
- **Stanford AI Productivity Study**: Identified patterns preventing slop
