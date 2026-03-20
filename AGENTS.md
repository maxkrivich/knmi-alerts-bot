# AGENTS.md - Essential Agent Rules for KNMIAlerts

## 1) Non-Negotiable Guardrail
Agents MUST NOT modify files unless the user explicitly requests `/implement`.

Allowed before `/implement`:
- Read/search code
- Analyze behavior
- Produce research or plans

Forbidden before `/implement`:
- Any source/config/test edits
- Any mutating command (except research/plan artifacts)

## 2) Required Workflow: Advanced Context Engineering
Use this sequence for any significant changes:
1. `/research` -> understand current behavior (see `ACE_WORKFLOW.md`)
2. `/plan` -> design phased implementation (see `ACE_WORKFLOW.md`)
3. `/implement` -> execute approved plan (see `ACE_WORKFLOW.md`)

**Key Rule**: No implementation during `/research` or `/plan`

For detailed instructions on each phase, see `ACE_WORKFLOW.md`.

## 3) Opencode-Native First
Prefer opencode native features:
1. TodoWrite for task tracking
2. Task tool with explore agent for research
3. Edit tool for plan updates
4. Native command execution for verification

## 4) Project Context
- Python `>=3.12,<4`
- Main components: `knmi_bot/`, `report_checker/`, `notifier/`
- Tooling: `uv`, Ruff, ty, Docker Compose

## 5) Essential Commands
```bash
uv install
make lint
make format
make check-format
make check-ty
make git-hooks
make up
```

## 6) Verification Policy
1. Static checks: `make lint`, `make check-format`, `make check-ty`
2. Runtime verification: `make up`
3. Always pause for manual testing between implementation phases

## 7) Code Standards
- Ruff rules: `E4`, `E7`, `E9`, `F`, `I`
- Line length: `127`; quote style: double quotes
- Import grouping: stdlib → third-party → local
- Typed signatures; concise docstrings
- Prefer `loguru` logger over `print`

## 8) Safety Boundaries
Ask first for: dependency changes, large refactors, CI/CD changes, destructive operations

Never: commit secrets, bypass quality checks, revert unrelated changes

## 9) Reference Docs
- `README.md` - setup/run instructions
- `ARCHITECTURE.md` - system design
- `PRODUCT.md` - product requirements
- `ACE_WORKFLOW.md` - detailed workflow instructions
- `ACE_WORKFLOW_QUICK_REFERENCE.md` - quick start examples

## 10) Source of Truth
If commands/tooling/workflow change, update this file and `ACE_WORKFLOW.md` in the same PR.
