---
date: 2026-03-20
feature: Replace mypy with ty
status: approved
---

# Replace mypy with ty — Implementation Plan

## Overview

Replace the project's static type checker from **mypy** to **ty** (Astral's Rust-based type checker). This involves swapping the dev dependency, updating the Makefile target name, updating cache directory references, and updating all documentation/workflow files that reference the old command.

## Current State Analysis

- **Dependency**: `mypy>=1.14.0,<2` declared in `pyproject.toml:28`; resolved to `mypy==1.19.1` + `mypy-extensions==1.1.0` in `uv.lock`
- **No mypy configuration**: Zero `[tool.mypy]` settings anywhere — nothing to migrate
- **Invocation**: `make check-mypy` → `uv run mypy .` (`Makefile:22-23`)
- **Not in CI**: `.github/workflows/ci.yaml` only runs `make git-hooks` (pre-commit); mypy is a manual-only check
- **Not in pre-commit**: `.pre-commit-config.yaml` has no mypy hook
- **Cache dir**: `.mypy_cache` excluded in `ruff.toml:10`; `.mypy_cache/`, `.dmypy.json`, `dmypy.json` in `.gitignore:153-156`
- **Documentation references**: 6 files reference `make check-mypy` by name

## Desired End State

- `uv run ty check` is the type-checking command, invoked via `make check-ty`
- `mypy` and `mypy-extensions` no longer appear in `pyproject.toml` or `uv.lock`
- `ty` appears as a dev dependency in `pyproject.toml`
- Cache references updated: `.ty_cache/` in `.gitignore`, `.mypy_cache` entry in `ruff.toml` replaced with `.ty_cache`
- All documentation and workflow files reference `make check-ty` instead of `make check-mypy`
- `make check-ty` runs clean (exit 0) against the current codebase

## What We're NOT Doing

- Adding any `[tool.ty]` configuration to `pyproject.toml` — ty's defaults are sufficient (it auto-detects `requires-python = ">=3.12,<4"` for Python version)
- Adding type checking to CI or pre-commit — that is unchanged and out of scope
- Fixing any pre-existing type errors surfaced by ty — if ty reports errors not caught by mypy, those are handled in a follow-up task
- Pinning ty to a specific version — `ty` (unpinned) is sufficient; it is a dev tool

## Implementation Approach

Two sequential phases:

1. **Core tool swap** — swap the dependency, regenerate the lock file, update the Makefile and cache-dir references, verify `make check-ty` passes
2. **Documentation updates** — update all 6 files that reference `make check-mypy` to `make check-ty`

Phase 2 is deferred until Phase 1 is manually verified to be working, since the documentation should only reflect a working tool.

---

## Phase 1: Core Tool Swap

### Overview

Replace mypy with ty at the tooling level: dependency declaration, lock file, Makefile target, and cache directory references in `ruff.toml` and `.gitignore`.

### Changes Required

#### 1. Dependency declaration
**File**: `pyproject.toml`
**Change**: In `[dependency-groups] dev`, replace `"mypy>=1.14.0,<2"` with `"ty"`.

```toml
[dependency-groups]
dev = [
    "icecream>=2.1.3,<3",
    "ipython>=8.31.0,<9",
    "ty",
]
```

#### 2. Lock file regeneration
**File**: `uv.lock` (auto-generated)
**Command**: `uv sync`

This removes `mypy` and `mypy-extensions` from the lock file and resolves/adds `ty`.

#### 3. Makefile target
**File**: `Makefile`
**Change**: Rename target from `check-mypy` to `check-ty`; replace `uv run mypy .` with `uv run ty check`.

```makefile
check-ty: ## Check ty
	uv run ty check
```

#### 4. Ruff exclusion list
**File**: `ruff.toml`
**Change**: Replace `".mypy_cache"` with `".ty_cache"` in the `exclude` list (`ruff.toml:10`).

#### 5. Gitignore
**File**: `.gitignore`
**Change**: Replace the mypy cache block (lines 153–156) with a ty cache block:

```
# ty
.ty_cache/
```

The `.dmypy.json` and `dmypy.json` entries (mypy daemon artifacts) are also removed.

### Success Criteria

#### Automated Verification
- [ ] `make lint` passes
- [ ] `make check-format` passes
- [ ] `make check-ty` passes (exit 0)

#### Manual Verification
- [ ] `uv run ty check` completes without unexpected errors in the terminal
- [ ] `mypy` and `mypy-extensions` no longer appear in `uv.lock`
- [ ] `ty` appears in `uv.lock`
- [ ] `make check-ty` is visible in `make help` output

**Note**: After completing this phase and all automated verification passes, pause for manual confirmation from the human before proceeding to Phase 2.

---

## Phase 2: Documentation Updates

### Overview

Update all 6 documentation and workflow files that reference `make check-mypy` to use `make check-ty`. Also update prose references to mypy as the project's type checker tool.

### Changes Required

#### 1. AGENTS.md
**File**: `AGENTS.md`
**Lines to update**:
- Line 35: Change `mypy` in tooling list to `ty`
- Line 43: Change `make check-mypy` to `make check-ty`
- Line 49: Change `make check-mypy` to `make check-ty`

Specific changes:
```
## 4) Project Context
- Tooling: `uv`, Ruff, ty, Docker Compose   ← was: mypy

## 5) Essential Commands
make check-ty                                ← was: make check-mypy

## 6) Verification Policy
1. Static checks: `make lint`, `make check-format`, `make check-ty`   ← was: check-mypy
```

#### 2. ACE_WORKFLOW.md
**File**: `ACE_WORKFLOW.md`
**Lines to update**: 171, 213, 275, 289, 371
All occurrences of `make check-mypy` → `make check-ty`.

#### 3. ACE_WORKFLOW_QUICK_REFERENCE.md
**File**: `ACE_WORKFLOW_QUICK_REFERENCE.md`
**Lines to update**: 41, 152
All occurrences of `make check-mypy` → `make check-ty`.

#### 4. ACE_WORKFLOW_INTEGRATION.md
**File**: `ACE_WORKFLOW_INTEGRATION.md`
**Lines to update**: 113, 122, 127
- Line 113: `make check-mypy` → `make check-ty`
- Line 122: `mypy for type checking` → `ty for type checking`
- Line 127: `make check-mypy` → `make check-ty`

#### 5. .opencode/commands/implement.md
**File**: `.opencode/commands/implement.md`
**Lines to update**: 35, 47
All occurrences of `make check-mypy` → `make check-ty`.

#### 6. .opencode/commands/plan.md
**File**: `.opencode/commands/plan.md`
**Lines to update**: 85, 111
All occurrences of `make check-mypy` → `make check-ty`.

### Success Criteria

#### Automated Verification
- [ ] `make lint` passes
- [ ] `make check-format` passes
- [ ] `make check-ty` passes

#### Manual Verification
- [ ] `grep -r "check-mypy" .` returns no results (outside of the plan/research artifacts in `docs/`)
- [ ] `grep -r "mypy" . --include="*.md" --include="*.toml" --include="Makefile"` returns only cache-dir related results in `.gitignore` (none) and this plan document

**Note**: After completing this phase, the migration is complete.

---

## Testing Strategy

### Automated
- `make lint` — Ruff linting passes on all Python source
- `make check-format` — Ruff format check passes
- `make check-ty` — ty type checking passes (exit 0)

### Manual Testing Steps
1. Run `make check-ty` in the terminal and confirm it exits cleanly
2. Confirm `make help` displays `check-ty` with its description
3. Run `grep -r "check-mypy" . --include="*.md" --include="*.toml" --include="Makefile"` and confirm zero results (excluding docs/research and docs/plans artifacts)
4. Confirm `uv.lock` no longer contains `mypy` or `mypy-extensions`

---

## References

- Related research: `docs/research/2026-03-20-replace-mypy-with-ty.md`
- ty documentation: https://docs.astral.sh/ty/
- `pyproject.toml:28` — dependency to replace
- `Makefile:22-23` — target to update
- `ruff.toml:10` — cache exclusion to update
- `.gitignore:153-156` — cache entries to replace
