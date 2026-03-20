---
date: 2026-03-20
topic: Replace mypy with ty for static type checking
status: research-complete
---

# Research: Replace mypy with ty

## Summary

The project currently uses **mypy** solely as a manually invoked dev-dependency (`make check-mypy`). It is **not** wired into CI or pre-commit hooks. There is **no custom mypy configuration** — it runs with all defaults. This makes the replacement surface minimal: one dependency declaration, one Makefile target, and references in documentation/workflow files.

**ty** is a new Python type checker from Astral (the creators of uv and Ruff), written in Rust. It is claimed to be 10×–100× faster than mypy, supports `pyproject.toml` configuration under `[tool.ty]`, and is installed via `uv add --dev ty`. The CLI entry point for type checking is `ty check`.

ty is **pre-1.0** (currently at `0.0.x`). Its docs note it is still in active development.

---

## Detailed Findings

### 1. Current mypy Usage in the Project

| Aspect | Detail |
|--------|--------|
| Declared dependency | `mypy>=1.14.0,<2` in `[dependency-groups] dev` (`pyproject.toml:28`) |
| Resolved version | `mypy==1.19.1` + `mypy-extensions==1.1.0` (in `uv.lock`) |
| Configuration | **None** — no `[tool.mypy]` section, no `mypy.ini`, no `setup.cfg [mypy]` |
| Invocation | `make check-mypy` → `uv run mypy .` (`Makefile:22-23`) |
| CI | **Not in CI** — `.github/workflows/ci.yaml` only runs `make git-hooks` (pre-commit) |
| Pre-commit | **Not a hook** — `.pre-commit-config.yaml` has no mypy entry |
| Ruff exclusion | `.mypy_cache` excluded from Ruff scan (`ruff.toml:10`) |
| Gitignore | `.mypy_cache/`, `.dmypy.json`, `dmypy.json` ignored (`.gitignore:153-156`) |

### 2. Files Referencing mypy

| File | Lines | Context |
|------|-------|---------|
| `pyproject.toml` | 28 | Dependency declaration |
| `Makefile` | 22–23 | `check-mypy` target |
| `ruff.toml` | 10 | Excludes `.mypy_cache` from Ruff |
| `.gitignore` | 153–156 | Ignores mypy cache artifacts |
| `uv.lock` | 202, 219, 308–346 | Resolved mypy + mypy-extensions packages |
| `AGENTS.md` | 35, 43, 49 | Documents `make check-mypy` in verification policy |
| `ACE_WORKFLOW.md` | 171, 213, 275, 289, 371 | References `make check-mypy` |
| `ACE_WORKFLOW_QUICK_REFERENCE.md` | 41, 152 | References `make check-mypy` |
| `ACE_WORKFLOW_INTEGRATION.md` | 113, 122, 127 | References `make check-mypy` |
| `.opencode/commands/implement.md` | 35, 47 | References `make check-mypy` |
| `.opencode/commands/plan.md` | 85, 111 | References `make check-mypy` |

### 3. ty Tool — What It Is

- **Author**: Astral (same team as uv and Ruff)
- **Language**: Rust
- **Status**: Pre-1.0 (currently `0.0.x` series); docs dated 2026-03-19
- **Homepage**: https://docs.astral.sh/ty/
- **PyPI**: `ty`
- **Speed claim**: 10×–100× faster than mypy and Pyright
- **Key feature**: Also includes a language server (`ty server`)

### 4. ty Installation

The recommended method for a uv-managed project:

```bash
uv add --dev ty
```

Then invoke via:

```bash
uv run ty check
```

Or without installation (for quick trials):

```bash
uvx ty check
```

### 5. ty CLI Interface

The primary command for type checking:

```
ty check [OPTIONS] [PATH]...
```

Notable options:

| Option | Description |
|--------|-------------|
| `[PATH]...` | Files or directories to check (defaults to project root) |
| `--python` / `--venv` | Path to Python environment or interpreter |
| `--python-version` | Target Python version (e.g., `3.12`) |
| `--python-platform` | Target platform (`linux`, `darwin`, `win32`, `all`) |
| `--ignore <rule>` | Disable a rule |
| `--warn <rule>` | Treat rule as warning severity |
| `--error <rule>` | Treat rule as error severity |
| `--output-format` | `full` (default), `concise`, `github`, `gitlab`, `junit` |
| `--watch` / `-W` | Watch mode |
| `--config` / `-c` | Inline TOML config override |
| `--config-file` | Path to a `ty.toml` file |
| `--exit-zero` | Always exit 0 even with errors |
| `--error-on-warning` | Exit 1 if any warnings |

### 6. ty Configuration Format

Configuration lives in `pyproject.toml` under `[tool.ty]` or in a separate `ty.toml`.

**Configuration sections** (from reference docs):

```toml
# pyproject.toml

[tool.ty.rules]
# Set severity: "ignore" | "warn" | "error"
possibly-unresolved-reference = "warn"
division-by-zero = "ignore"

[tool.ty.environment]
python-version = "3.12"
python-platform = "linux"  # or "darwin", "win32", "all"
# extra-paths = ["./stubs"]
# python = ".venv"

[tool.ty.src]
exclude = ["generated/**"]
# include = ["src", "tests"]
# respect-ignore-files = true  (default)

[tool.ty.terminal]
output-format = "concise"
# error-on-warning = false  (default)

[[tool.ty.overrides]]
include = ["tests/**"]
[tool.ty.overrides.rules]
possibly-unresolved-reference = "warn"
```

**Key behavioral note**: ty automatically reads `project.requires-python` from `pyproject.toml` to infer the Python version. Since this project declares `requires-python = ">=3.12,<4"`, ty would default to targeting Python 3.12 with no additional config needed.

**Suppression comments**: ty respects both `# type: ignore` (mypy-compatible, enabled by default via `respect-type-ignore-comments = true`) and its own `# ty: ignore` syntax.

### 7. ty Default Exclusions

ty automatically excludes `.mypy_cache/` from scanning (it is listed in ty's built-in default exclusion set as `**/.mypy_cache/`). ty uses its own cache directory `.ty_cache/`.

---

## Code References

- `pyproject.toml:28` — mypy dependency declaration
- `pyproject.toml:6` — `requires-python = ">=3.12,<4"` (ty will auto-detect this for Python version)
- `Makefile:22-23` — `check-mypy` target (`uv run mypy .`)
- `ruff.toml:10` — `.mypy_cache` exclusion
- `.gitignore:153-156` — mypy cache artifact patterns
- `.github/workflows/ci.yaml:27-28` — CI runs `make git-hooks` only (no mypy)
- `.pre-commit-config.yaml:1-33` — no mypy hook present

---

## Architectural Patterns

- **uv-managed project**: All dev tooling is invoked via `uv run <tool>`. ty follows this same pattern (`uv run ty check`).
- **Makefile as task runner**: All quality gates are surfaced as `make` targets. The mypy gate is `make check-mypy`.
- **No mypy custom configuration**: mypy runs with zero configuration, scanning `.` with defaults. No config migration is required.
- **Pre-commit does not include type checking**: Type checking is only a manual/local quality check, not enforced at commit time or in CI.
- **Documentation references `make check-mypy`** in multiple workflow documents (AGENTS.md, ACE_WORKFLOW.md, etc.).

---

## Historical Context

- No evidence of a previous type checker before mypy in the repository.
- There is no `mypy.ini` or `[tool.mypy]` block, suggesting mypy was added without customization for basic type checking coverage.
- The Astral ecosystem (uv, Ruff) is already adopted in this project; ty is also from Astral.

---

## Scope of Change Required

To replace mypy with ty, the following artifacts would need to change:

| Artifact | Change Type | Details |
|----------|------------|---------|
| `pyproject.toml` | Dependency swap | Replace `mypy>=1.14.0,<2` with `ty` in `[dependency-groups] dev` |
| `uv.lock` | Auto-regenerated | `uv sync` after pyproject.toml change |
| `Makefile` | Command swap | Replace `uv run mypy .` with `uv run ty check` in `check-mypy` target |
| `ruff.toml` | Cache dir update | Swap `.mypy_cache` exclusion for `.ty_cache` |
| `.gitignore` | Cache dir update | Remove mypy cache entries; add `.ty_cache/` |
| `AGENTS.md` | Doc update | Update `make check-mypy` references if target is renamed |
| `ACE_WORKFLOW.md` | Doc update | Same |
| `ACE_WORKFLOW_QUICK_REFERENCE.md` | Doc update | Same |
| `ACE_WORKFLOW_INTEGRATION.md` | Doc update | Same |
| `.opencode/commands/implement.md` | Doc update | Same |
| `.opencode/commands/plan.md` | Doc update | Same |

The change is **low-risk and narrow** — no existing mypy configuration needs migrating (there is none), and type checking is not part of CI or pre-commit, so the blast radius of a failed first run is limited to local developer experience.
