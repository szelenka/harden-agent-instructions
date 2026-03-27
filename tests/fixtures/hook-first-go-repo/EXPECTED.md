# Expected Audit Results: hook-first-go-repo

A small Go repo where `.pre-commit-config.yaml` is the strongest operational truth and there is no stronger build manifest.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** hook-first
- **Verification commands:** `go test ./...`, `go vet ./...`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks derived from the pre-commit hooks
- Key paths with roles (`.pre-commit-config.yaml` — enforced local verification contract, `service/handler.go` — runtime logic, `service/handler_test.go` — deterministic verification)
- A note that hook-backed checks are stronger than guessed local workflows

## Key Signals

- The skill must prioritize the hook config over absent CI or guessed task runners
- The audit should treat pre-commit hooks as canonical local verification
- The done checklist should reflect the hook-backed Go commands directly
