# Expected Audit Results: weak-instructions

A Go user service with Chi and PostgreSQL. Has an AGENTS.md but it's vague and missing critical content.

## Expected Phase 2 Assessment

- **Cold-start ready:** no
  - Build commands NOT in code blocks (just prose references)
  - Fewer than 3 concrete file paths (zero actual paths referenced)
  - No project structure section with paths
- **Repo tier:** small
- **Stale paths:** none (no paths referenced at all)
- **Verification gaps:** `make build`, `make test`, `make lint`, `make fmt`, `make migrate` exist but aren't in code blocks
- **Orphaned commands:** `fmt`, `run`, `migrate` not mentioned in instructions

## Expected Rubric Ratings

| Criterion | Expected Rating | Reason |
|-----------|----------------|--------|
| Instruction Salience | Missing | No rules marked as critical, no emphasis |
| Action-Outcome Coupling | Missing | "run tests" without naming the command |
| Grounding Density | Missing | Zero file paths, zero code examples |
| First-Time Correctness | Missing | No entry points, no commands, agent can't start |
| Structural Orientation | Missing | "layered architecture" mentioned but no file paths or data flow |
| Context Efficiency | Pass | File is short, at least not bloated |
| Codebase Drift Prevention | Missing | "follow best practices" is not a convention |

## Deliberate Stale Reference

`internal/routes/auth.go` references `internal/middleware/auth.go` in a TODO comment, but no `internal/middleware/` directory exists. This is intentional — the skill should detect this as a stale/broken path reference in the source code and note it in the assessment. It also tests whether the skill distinguishes between stale paths in instruction files (its primary job) and broken references in source code (which it should flag but not fix).

## Anti-patterns Present (skill should flag these)

- "Make sure code is clean and well-tested" — abstract, no command
- "Follow best practices" — meaningless without specifics
- "just retry" — not actionable guidance
- "run the linter" — which command? Not in a code block
- No file paths anywhere in the document
