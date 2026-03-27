# Expected Audit Results: makefile-only-mixed

A small repo with a root `Makefile` but no language-specific manifest.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** root `Makefile`
- **Verification commands:** `make lint`, `make render`, `make smoke-test`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks (`make lint`, `make render`, `make smoke-test`)
- Key paths with roles (`scripts/lint.sh` — static checks, `scripts/render.sh` — artifact renderer, `templates/service.conf.tmpl` — rendered template source)
- A done checklist that treats the Makefile targets as canonical

## Key Signals

- The skill must not guess the repo language from the Makefile alone
- The audit should treat the Makefile as the primary workflow surface
- The audit should avoid inventing `package.json`, `pyproject.toml`, or `go.mod` guidance
