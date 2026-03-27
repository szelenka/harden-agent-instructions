# Expected Audit Results: hook-first-go-template-seed

A small repo where a generic Go-template `AGENTS.md` exists, but `.pre-commit-config.yaml` is the strongest operational truth and there is no stronger build manifest.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (instruction file exists, but it is still template-shaped and not repo-grounded)
- **Repo tier:** small
- **Instruction files found:** `AGENTS.md`
- **Build system:** hook-first
- **Verification commands:** `go test ./...`, `go vet ./...`

## Expected Phase 3 Actions

The skill should rewrite the existing `AGENTS.md` so it:
- Removes generic template residue and placeholder-style guidance
- Treats `.pre-commit-config.yaml` as the canonical verification contract
- Uses fenced command blocks with `go test ./...` and `go vet ./...`
- Names key paths with roles (`.pre-commit-config.yaml` — enforced local verification contract, `service/handler.go` — runtime logic, `service/handler_test.go` — deterministic verification)
- Drops generic workflow content that is not grounded in the fixture, such as branch-policy boilerplate and guessed install or lint commands

## Key Signals

- The skill must override the generic Go template when hook-backed evidence is stronger
- The audit should convert the file from language-template guidance to repo-grounded operational guidance
- The done checklist should reflect the hook-backed commands directly
