# Advanced Context Engineering Integration - Summary

## What Was Added

Your `AGENTS.md` file has been enhanced with a comprehensive **Advanced Context Engineering (ACE)** workflow based on industry best practices from HumanLayer and research by Dex Horthy.

### Files Modified/Created

1. **AGENTS.md** (enhanced)
   - Added 243 lines covering 3 detailed workflow sections
   - Maintained all existing project configuration
   - Integrated OpenCode native features

2. **ACE_WORKFLOW_QUICK_REFERENCE.md** (new)
   - Quick start guide for the team
   - Common examples and patterns
   - Mistakes to avoid

## Key Concepts

### Frequent Intentional Compaction

The workflow is based on deliberately structuring how context is fed to agents throughout development:

```
Research Phase
    ↓ (output: structured document with file references)
Plan Phase
    ↓ (output: phased implementation plan with success criteria)
Implement Phase
    ↓ (output: working code with verified phases)
```

Each transition allows context reset while preserving critical information in compact artifacts.

### The Three Phases

#### `/research` - Understanding
- **Goal**: Map what currently exists, no changes
- **Output**: Structured research document
- **Duration**: Typically 30 mins - 2 hours
- **Guardrail**: Read-only operations only

#### `/plan` - Designing
- **Goal**: Create specific, phased approach to implementation
- **Output**: Detailed plan with automated + manual verification steps
- **Duration**: Typically 30 mins - 2 hours
- **Guardrail**: No code changes, interactive feedback

#### `/implement` - Executing
- **Goal**: Follow plan while adapting to reality
- **Output**: Working code with verified phases
- **Duration**: Varies by plan complexity
- **Guardrail**: Follow plan, pause for human verification

## Why This Matters

### The Problem This Solves

From the Stanford study on AI developer productivity:
- AI tools often produce "slop" that requires rework
- Agents struggle with large, complex codebases
- Without structure, productivity gains disappear

### The Solution

By separating concerns across three focused phases:

1. **Research** prevents wrong assumptions
   - Concrete file references prevent hallucination
   - Structured output is easily verified
   - Team alignment before planning

2. **Planning** prevents scope creep and false starts
   - Phased approach enables course correction
   - Success criteria are explicit and measurable
   - Separation of automated vs manual checks

3. **Implementation** prevents surprises
   - Plan is reference, not gospel
   - Conflicts are resolved before proceeding
   - Human verification gates quality

### Results From Real Use

From testing on 300k LOC Rust codebases (BAML project):
- ✅ Bug fixes shipped in <2 hours
- ✅ Complex features shipped in one day
- ✅ Code quality passed expert review
- ✅ No "slop" - all PRs merged directly

## OpenCode-Native Design

The workflow uses OpenCode's built-in features:

### TodoWrite
- Track research decomposition
- Track plan phases
- Track implementation progress
- Full visibility into what's happening

### Task Tool with Explore Agent
- Parallel research across codebase
- Efficient discovery patterns
- Clean context management

### Edit Tool
- Mark plan checkboxes as complete
- Atomic changes to plans
- Prevents lost progress

### Native Verification
- `make lint`, `make check-format`, `make check-ty` integration
- Runtime testing via `make up`
- Clear pass/fail gates

## How It Fits Your Project

### Your Existing Setup
- Python 3.12+ with `uv` package manager
- Ruff for linting/formatting
- ty for type checking
- Docker Compose for runtime testing
- Three main components: knmi_bot, report_checker, notifier

### The Workflow Leverages
- Static verification: `make lint`, `make check-format`, `make check-ty`
- Runtime verification: `make up`
- Clear architecture documented in ARCHITECTURE.md
- Product requirements documented in PRODUCT.md

## Guardrails Included

### The Core Rule
**Agents MUST NOT modify files unless explicitly requested via `/implement`**

### Before `/implement`:
✅ Read and analyze code
✅ Search for patterns
✅ Create research documents
✅ Create plans
✅ Ask clarifying questions

### After `/implement` Only:
✅ Modify source files
✅ Run test suites
✅ Update configuration
✅ Make commits

## Getting Started

### For the Next Task

Instead of:
```
"Add rate limiting to the alert notifications"
```

Try:
```
"Please research how alerts are currently sent from the notification
service. Use /research to map:
- Current notification flow
- Any existing rate limiting
- Configuration patterns used
- Files involved with line numbers"
```

Then:
```
"Based on the research, create a /plan for adding rate limiting that:
- Keeps configuration pattern consistent
- Includes unit and integration tests
- Shows both automated and manual verification steps"
```

Finally:
```
"Please /implement the plan phase-by-phase, pausing for manual
verification between phases."
```

### Team Communication

The workflow helps teams by:
- Making research explicit (can be reviewed)
- Making plans explicit (can be debated)
- Making implementation explicit (can be verified phase-by-phase)
- Preventing "black box" AI work

## Documentation References

Your project now has:

1. **AGENTS.md**
   - Core guardrails and rules
   - Detailed workflow documentation
   - Success criteria guidelines
   - Implementation philosophy

2. **ACE_WORKFLOW_QUICK_REFERENCE.md**
   - Quick start guide
   - Common patterns
   - Example conversations
   - Mistakes to avoid

3. **ARCHITECTURE.md** (existing)
   - System design overview
   - Component relationships

4. **PRODUCT.md** (existing)
   - Product requirements
   - Feature specifications

5. **README.md** (existing)
   - Setup and running instructions

## Technical Foundations

This implementation is based on:

- **ACE (Advanced Context Engineering)**: https://github.com/humanlayer/advanced-context-engineering-for-coding-agents
- **HumanLayer Workflow**: Real-world patterns from HumanLayer team
- **Context Management Research**: Principles from Stanford AI productivity study
- **Frequent Intentional Compaction**: Context window optimization technique

## Questions to Consider

As you adopt this workflow:

1. **For Research**: What assumptions do you have about how the system works?
2. **For Planning**: What could go wrong if we implement this way?
3. **For Implementation**: When should we pause for manual testing?

## Next Steps

1. **Review** the full AGENTS.md workflow
2. **Share** ACE_WORKFLOW_QUICK_REFERENCE.md with your team
3. **Try** the workflow on the next task
4. **Adjust** based on what works for your team
5. **Update** AGENTS.md if needed (version control it)

---

**Key Insight**: The workflow is not about "magic prompts" - it's about thoughtful structure that keeps both humans and AI focused on the right problems at the right time.
