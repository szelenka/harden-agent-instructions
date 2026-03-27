# Expected Audit Results: sparse-git-repo

A small git-backed repo with no instruction files and no trustworthy build manifest.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** absent or unverified
- **Verification reality:** partial or unavailable
  - no package manager manifest
  - no root Makefile
  - no CI or hook evidence in the fixture

## Expected Phase 3 Actions

The skill should create a minimal AGENTS.md containing:
- Hard rules section
- A plain statement that canonical build/test commands are unavailable from repo evidence
- Key paths with roles (`docs/architecture.md` — system notes, `scripts/sync.sh` — operational helper, `config/environments/dev.yaml` — environment config)
- A done checklist that says verification is limited to deterministic checks actually present

## Key Signals

- The skill must NOT invent npm, Python, Go, CI, or contributor workflow commands
- The audit should explicitly downgrade confidence because repo evidence is sparse
- The audit should avoid fabricating a richer architecture than the docs/config files support
