---
description: Execute an approved plan phase-by-phase with verification
---

You are entering the /implement phase of the ACE workflow. Your goal is to execute the approved plan phase-by-phase, verifying each phase before proceeding.

## Your Task

Implement: $ARGUMENTS

## Process

### 1. Understand the plan
- Read the complete plan document from `docs/plans/`
- Check for any existing progress (✓ marks or checked boxes)
- Read all files mentioned in the plan
- Create a TodoWrite list for the phases

### 2. Execute Phase N
- Implement all changes specified in the phase
- Update plan checkboxes as you complete sections using the Edit tool
- Follow code standards from AGENTS.md:
  - Ruff rules: `E4`, `E7`, `E9`, `F`, `I`
  - Line length: 127, double quotes
  - Import grouping: stdlib → third-party → local
  - Typed signatures; concise docstrings
  - Prefer `loguru` logger over `print`
- Track progress in TodoWrite

### 3. Run automated verification
After each phase, run all checks:
```bash
make lint
make check-format
make check-ty
```
Fix any failures and re-run. Do not proceed to manual verification until all checks pass.

### 4. Pause for human manual verification
After automated checks pass, present:
```
Phase [N] Complete — Ready for Manual Verification

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
Do NOT check off manual verification items until confirmed by the user.

### 5. Handle plan conflicts
If the actual codebase differs from the plan, stop and report:
```
Issue in Phase [N]:
Expected: [what the plan says]
Found: [actual situation]
Why this matters: [explanation]

How should I proceed?
```
Wait for human guidance before deviating from the plan.

### 6. Repeat until complete
- Update todos as each phase completes
- Run all verification steps for every phase
- Pause for manual verification between phases (unless told to execute consecutively)

## Guardrails

You MUST follow these rules:
- Only implement what the approved plan specifies
- Never skip verification steps
- Never ignore plan conflicts without asking
- Never bypass quality gates (`--no-verify`, etc.)
- Never make changes outside the approved plan scope
- Do not proceed past a phase until manual verification is confirmed
