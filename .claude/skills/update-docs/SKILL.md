---
name: update-docs
description: Update project documentation to reflect the current state of the code. Use when new features have been added, bugs fixed, or the architecture has changed and the docs are out of date.
argument-hint: [all | claude | architecture | diagrams | summary | readme]
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Update Project Documentation

Synchronise documentation with the current codebase state.

## Argument

`$ARGUMENTS` specifies which doc(s) to update:

| Value | File(s) updated |
| ----- | --------------- |
| `all` | All docs below |
| `claude` | `CLAUDE.md` |
| `architecture` | `docs/ARCHITECTURE.md` |
| `diagrams` | `docs/DIAGRAMS.md` |
| `summary` | `docs/PROJECT_SUMMARY.md` |
| `readme` | `README.md` and `ui/README.md` |
| *(empty)* | Ask the user which doc needs updating |

## Before updating any doc

1. Read the current file in full
2. Read the files it references (`api_server.py`, `src/agent/core.py`, `src/tools/`, `ui/src/`) to understand the actual current state
3. Note specifically what has changed since the doc was last written

## What to check in each doc

### `CLAUDE.md`

- Tool integrations table — correct tools, correct APIs, correct API keys
- Known Issues & Fixes Applied — any new bugs fixed should be added
- File structure under Frontend Setup — matches actual `ui/src/` tree
- Quick start commands — still accurate
- Version number and Last Updated date at the bottom

### `docs/ARCHITECTURE.md`

- System Overview diagram — all tools present, no removed tools
- Core Components sections — `client.ts`, hooks, `api_server.py`, `core.py`, all tools
- Location Resolution end-to-end trace — still accurate
- Data Flow Examples — Restaurant, Events, Uber, Save flows still correct
- Configuration section — env vars and config.yaml keys still accurate

### `docs/DIAGRAMS.md`

- High-Level Architecture diagram — tools match what's in `src/tools/`
- External Services section — no obsolete services
- Class diagram — `classDiagram` reflects actual tool class signatures
- Sequence diagrams — step-by-step flows match current code

### `docs/PROJECT_SUMMARY.md`

- Requirements Implementation table — all pillars present
- Tech Stack tables — no obsolete packages, new packages added
- Project Structure tree — matches actual directory layout
- Known Issues & Fixes Applied table — complete
- Success Criteria table — all met criteria are ticked

### `README.md`

- Tech Stack tables — accurate
- Project Structure tree — matches current layout
- Environment Variables table — complete
- Quick Start commands — still work
- Documentation Index links — all files exist

### `ui/README.md`

- File Structure tree — matches actual `ui/src/` tree
- Key Modules section — hook signatures match current code
- Scripts table — matches `ui/package.json` scripts

## Linting rules to follow

- All table separator rows must use `| --- |` style (spaces next to pipes)
- No duplicate H1/H2 headings within a file
- Fenced code blocks must have a language specifier (` ```python `, ` ```bash `, ` ```typescript `, ` ```text `)
- Blank line before and after every fenced code block
- Ordered lists that are interrupted by code blocks must restart numbering at `1.`
- Blank line between a heading and its list items

## After updating

Tell the user exactly what was changed and why — specific sections updated and what the old vs new content was.
