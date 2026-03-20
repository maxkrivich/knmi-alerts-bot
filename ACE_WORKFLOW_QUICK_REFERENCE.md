# Advanced Context Engineering Workflow - Quick Reference

This document provides quick examples of how to use the ACE workflow with OpenCode.

## The Three Phases

### 1. `/research` - Understand the Current State

**When to use**: Before making any changes, understand what currently exists.

**Example**:
```
"I need to understand how the alert notification system works currently.
Use /research to:
- Map the current flow from knmi_bot to notifier
- Identify all relevant files with line numbers
- Document the messaging patterns being used
- Note any existing retry mechanisms"
```

**What you'll get**:
- A structured research document with file references
- Current patterns and conventions
- Architecture overview
- No code changes

**Time to pause**: None - research is complete when documented

---

### 2. `/plan` - Design the Implementation

**When to use**: After understanding what exists, design how you'll change it.

**Example**:
```
"Based on the research, create an implementation plan for adding
persistent message queuing. The plan should:
- Break down the work into phases
- Show which files need changes
- Include both automated (make lint, make check-ty)
  and manual verification steps (test via make up)
- Ask me for feedback before finalizing"
```

**What you'll get**:
- Phased implementation plan
- Specific files identified for changes
- Clear success criteria
- No code changes

**Time to pause**: Interactive iteration until the plan is approved

---

### 3. `/implement` - Execute the Approved Plan

**When to use**: Only after you've approved the plan.

**Example**:
```
"Please implement the plan from docs/plans/2025-03-20-message-queuing.md
Execute it phase-by-phase, pausing after each phase for manual verification."
```

**What happens**:
1. Phase 1 executed → automated checks run → pause for manual testing
2. Get confirmation from you
3. Phase 2 executed → automated checks run → pause for manual testing
4. Continue until complete

**Time to pause**: After each phase, waiting for manual verification

---

## How It Works With OpenCode Native Features

### TodoWrite for Tracking
The agent uses TodoWrite to track progress:
- Research tasks broken into items
- Plan phases tracked
- Implementation phases marked complete/in-progress

You can see exactly what's happening in real-time.

### Task Tool for Parallel Research
The agent spawns parallel research tasks:
- Multiple independent searches running concurrently
- Efficient context usage
- Faster exploration of the codebase

### Edit Tool for Plan Updates
The agent uses Edit to mark progress:
- ✓ items checked off as they complete
- Prevents losing work if context resets
- Plan stays accurate throughout

---

## What NOT to Do

### During `/research`:
❌ Don't ask for code changes
❌ Don't expect implementation
❌ Don't ask for suggestions (only documentation)

### During `/plan`:
❌ Don't ask for code changes
❌ Don't approve a plan with unanswered questions
❌ Don't skip feedback on the phases

### During `/implement`:
❌ Don't ask for changes outside the plan
❌ Don't skip verification steps
❌ Don't avoid pausing for manual testing

---

## Example Workflow Conversation

```
You: "I want to add rate limiting to the alert system.
      Start with /research."

Agent: [Researches current rate limiting patterns,
        creates research document with file references]

You: [Reviews research document]
     "Thanks, I see we use loguru. Based on this research,
      create a /plan for adding rate limiting with:
      - Phase 1: Add rate limiter utility
      - Phase 2: Integrate with notification service
      - Phase 3: Add configuration options"

Agent: [Asks clarifying questions]
       "I found we use environ for config. Should I use
        the same pattern here?"

You: "Yes, match the existing environ pattern."

Agent: [Creates detailed plan with success criteria]

You: [Reviews plan]
     "This looks good. Please /implement it."

Agent: [Implements Phase 1]
       "Phase 1 Complete - Ready for Manual Verification

        Automated checks passed:
        - ✅ make lint
        - ✅ make check-format
        - ✅ make check-ty

        Please test Phase 1 manually:
        - [ ] Verify rate limiter initializes correctly
        - [ ] Verify basic rate limiting works"

You: "Verified, rate limiter working correctly."

Agent: [Implements Phase 2]
       [Pauses for manual verification again]

[Continues until complete]
```

---

## Key Principles

### Frequent Intentional Compaction
- **Research** → structured document (distilled knowledge)
- **Plan** → phased steps (actionable plan)
- **Implement** → phase-by-phase (verified execution)

Each phase outputs a compact artifact that allows context reset.

### Keep Context Windows Healthy
- Target 40-60% utilization
- Compact between phases
- Clear phase boundaries

### Guardrails That Protect Quality
- No changes without explicit `/implement`
- Automated verification gates before manual testing
- Pause points for human judgment
- Plan conflicts must be discussed

---

## Common Mistakes to Avoid

### ❌ Vague Research Questions
"Research the system"
✅ Better: "Research how alerts flow from detection to notification"

### ❌ Skipping Plan Feedback
"Just make the plan"
✅ Better: "Create plan, then ask me for feedback before finalizing"

### ❌ Missing Success Criteria
"Phase 1: Add caching"
✅ Better: Include both automated (tests pass) and manual (performance acceptable)

### ❌ Changing Scope During Implementation
"Phase 2: Add caching AND add monitoring"
✅ Better: Add monitoring to a new phase, don't expand existing phases

### ❌ Skipping Manual Verification
"Just keep going to Phase 3"
✅ Better: "I manually tested Phase 2, proceed to Phase 3"

---

## See Also

- `AGENTS.md` - Full agent rules and detailed workflow
- `ARCHITECTURE.md` - System design overview
- `PRODUCT.md` - Product requirements
- `README.md` - Setup and running instructions

---

## Questions?

For detailed rules, see the "Advanced Context Engineering Workflow" section in AGENTS.md.
For OpenCode documentation, see: https://opencode.ai/docs
