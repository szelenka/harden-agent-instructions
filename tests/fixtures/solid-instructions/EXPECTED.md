# Expected Audit Results: solid-instructions

A TypeScript/Express invoice processor with Prisma and Zod. Has a well-structured AGENTS.md.

## Expected Phase 2 Assessment

- **Cold-start ready:** yes
  - Build commands in code blocks: yes (`npm run check`, `npm run build`, etc.)
  - Concrete file paths (>=3): yes (10+ paths referenced)
  - Key entry points with roles: yes (directories annotated with purpose in Architecture section)
- **Repo tier:** small
- **Stale paths:** none (all referenced paths exist in the fixture)
- **Verification gaps:** none — `npm run check` covers lint + format + test

## Expected Rubric Ratings

| Criterion | Expected Rating | Reason |
|-----------|----------------|--------|
| Instruction Salience | Pass | Hard rules first, bold emphasis, severity-ordered |
| Decision Boundary Precision | Pass | IF conditions for validation, imports |
| Action-Outcome Coupling | Pass | Every rule linked to a verification command |
| Context Efficiency | Pass | ~60 lines, dense signal |
| Grounding Density | Pass | Specific paths, right/wrong examples |
| First-Time Correctness | Pass | Quick start, entry points with roles, runnable commands |
| Structural Orientation | Pass | Architecture overview, data flow, file-role mappings |
| Done-When Checklists | Pass | Numbered checklist with exact commands |
| Testing Conventions | Pass | Location, framework, naming, what to mock |
| Codebase Drift Prevention | Pass | Dependency management, validation placement |

## Expected Remaining Issues (minor)

- No git workflow section (acceptable for small/single-contributor repo)
- No self-improving feedback loop instruction (not required for small tier)
- No verification ordering (only one check command, so ordering is moot)
- Could add scope boundaries (what's off-limits to modify)
