# AI Agent Instructions - Go Project

This file was seeded from a generic Go template and may need repository-specific tightening.

## 1. Commands (Run First)

Use the repository's Go workflow consistently.

| Task | Command |
| --- | --- |
| Install tools | `go install ./...` |
| Run tests | `go test ./...` |
| Run lint | `golangci-lint run` |
| Format | `gofmt -w .` |

## 2. Agent Persona and Scope

You are the Go engineering assistant for `hook-first-go-repo`.

Definition of done:
1. Requested behavior implemented.
2. Tests and lint pass.
3. Updated docs/config for behavior changes.

## 3. Repository Knowledge

- `service/`: production code.
- `service/handler_test.go`: tests.

## 4. Git Workflow

- Branch naming: `feature/*`, `fix/*`, `chore/*`.
- Commit format: conventional commits.

## 5. Boundaries and Escalation

### Ask First

- Introducing a new dependency.
- Relaxing lint rules.
