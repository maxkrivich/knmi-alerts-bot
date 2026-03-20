---
description: Research current behavior before planning changes
---

You are entering the /research phase of the ACE workflow. Your goal is to understand current behavior and document what exists — without suggesting improvements or making any changes.

## Your Task

Research the topic: $ARGUMENTS

## Process

### 1. Decompose using TodoWrite
Break the research question into composable areas:
- Identify specific components, patterns, or concepts to investigate
- Consider which directories and files are relevant
- Plan which aspects require parallel investigation

### 2. Parallel exploration
Use the Task tool with the `explore` agent to run multiple independent investigations simultaneously:
- Search for related implementations, configurations, and patterns
- Identify dependencies and integration points
- Keep context usage low by running searches in parallel

### 3. Synthesize findings
Structure your findings into:
- **Summary** — high-level overview answering the research question
- **Detailed Findings** — component-by-component breakdown
- **Code References** — specific file paths with line numbers (`file:line`)
- **Architectural Patterns** — conventions and design decisions found
- **Historical Context** — past decisions or design notes (if available)

### 4. Save research artifact
Save findings to: `docs/research/YYYY-MM-DD-<topic>.md`
- Use clear frontmatter with date, topic, and status
- Self-contained documentation suitable for reference
- Include all necessary context without requiring external files

## Guardrails

You MUST follow these rules:
- Read/analyze/document only — no file modifications
- No mutating commands
- No suggestions or improvements
- No critique of existing implementation
- Describe current state only

When complete, present a summary and the path to the saved artifact.
