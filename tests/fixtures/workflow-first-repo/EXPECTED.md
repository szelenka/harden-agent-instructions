# Expected Audit Results: workflow-first-repo

A small repo where `.github/workflows/ci.yml` is the strongest operational truth and no stronger local task runner exists.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** workflow-first
- **Verification commands:** `python -m pytest`, `ruff check .`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks derived from the CI workflow
- Key paths with roles (`.github/workflows/ci.yml` — enforced verification contract, `app/main.py` — runtime entry point, `tests/test_main.py` — deterministic verification)
- A note that CI is the source of truth even though the repo has minimal local tooling files

## Key Signals

- The skill must prioritize the workflow file over weaker or absent local manifests
- The audit should treat CI commands as canonical verification
- The done checklist should explicitly reflect the workflow-backed checks
