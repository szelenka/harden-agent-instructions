# Expected Audit Results: go-service

A small Go service repo with no instruction files, a root `Makefile`, and multiple command packages.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** `go.mod` plus root `Makefile`
- **Verification commands:** `make lint`, `make build`, `make test`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Build/test commands in fenced code blocks (`make lint`, `make build`, `make test`)
- Key entry points with roles (`cmd/api/main.go` — HTTP entry point, `internal/server/server.go` — request handling, `internal/config/config.go` — config loading)
- Architecture description limited to a small Go service with a `cmd/` plus `internal/` layout

## Key Signals

- The skill must prefer `make` and `go test` over invented npm, Python, or Poetry commands
- The audit should call out the `cmd/` versus `internal/` split rather than pretending the repo is a single binary
- The done checklist should use the Makefile targets as the canonical verification commands
