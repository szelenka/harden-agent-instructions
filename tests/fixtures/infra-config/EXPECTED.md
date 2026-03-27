# Expected Audit Results: infra-config

A small infra/config repo with no instruction files, a root `Makefile`, and Helm-style deployment files.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** root `Makefile` plus Helm/Helmfile config
- **Verification commands:** `make lint`, `make render`, `make diff`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Render/diff commands in fenced code blocks (`make lint`, `make render`, `make diff`)
- Key paths with roles (`helmfile.yaml` — release orchestration, `charts/ml-proxy/Chart.yaml` — chart metadata, `environments/dev/values.yaml` — environment values)
- Architecture description framed as deployment/config structure, not as an application service

## Key Signals

- The skill must NOT force unit-test guidance, `src/` assumptions, or application-layer architecture onto this repo
- The audit should treat render/diff/lint as the deterministic verification path
- The audit should describe the repo as config/infrastructure, not as a runtime codebase
