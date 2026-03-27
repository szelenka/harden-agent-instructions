# Expected Audit Results: dockerfile-sparse-repo

A small repo whose strongest concrete signal is a `Dockerfile`, with no instruction file and no stronger build manifest.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** Dockerfile-led and otherwise sparse
- **Verification reality:** partial
  - image build can be described from the Dockerfile
  - no stronger test or package workflow is present

## Expected Phase 3 Actions

The skill should create a minimal AGENTS.md containing:
- Hard rules section
- Conservative command guidance centered on Docker build/run only if phrased as discovered repo behavior
- Key paths with roles (`Dockerfile` — container build contract, `scripts/entrypoint.sh` — runtime entry script, `config/default.env` — runtime config)
- A done checklist that explicitly states verification is partial

## Key Signals

- The skill must not invent npm, Python, Go, Maven, or CI workflows
- The audit should acknowledge Docker as the strongest available signal
- The audit should stay conservative because the repo lacks richer deterministic verification
