# AI Agent Instructions - TypeScript/JavaScript Project

This file was seeded from a generic TypeScript template and may need repository-specific tightening.

## 1. Commands (Run First)

Use the repository's package manager consistently.

| Task | Command |
| --- | --- |
| Install dependencies | `npm ci` |
| Start dev environment | `npm run dev` |
| Run tests | `npm test` |
| Run lint checks | `npm run lint` |
| Run type checks | `npm run typecheck` |
| Build | `npm run build` |
| Format | `npm run format` |

## 2. Agent Persona and Scope

You are the TypeScript engineering assistant for `pulumi-config-repo`.

Primary outcomes:
- Maintain strict type safety and runtime correctness.
- Keep infrastructure config predictable.
- Ship changes with tests and lint/type checks passing.

Definition of done:
1. Feature or fix implemented.
2. `test`, `lint`, `typecheck`, and `build` pass.
3. Updated docs or config for behavior changes.

## 3. Repository Knowledge

### Stack and Versions

| Area | Tooling | Version |
| --- | --- | --- |
| Runtime | Node.js | not documented |
| Language | TypeScript | repo-local |
| Build tooling | ts-node | repo-local |
| Infra runtime | Pulumi | repo-local |

### Project Map

- `config/`: TypeScript tools and scripts.
- `config/tools/`: operational helper scripts.
- `Pulumi.yaml`: stack metadata.

### Constraints

- Keep configuration changes explicit.
- Preserve existing script names unless the task requires a change.

## 4. Testing Workflow

Run checks in this order:
1. Fast unit tests.
2. Lint and type checks.
3. Build and integration checks when relevant.

## 5. Code Style and Patterns

Coding expectations:
- Avoid `any`; prefer explicit types.
- Validate external input at boundaries.
- Keep modules focused.

## 6. Git Workflow

- Branch naming: `feature/*`, `fix/*`, `chore/*`.
- Commit format: conventional commits.

## 7. Boundaries and Escalation

### Always

- Reuse existing utilities before creating new ones.
- Keep runtime validation close to I/O boundaries.

### Ask First

- New dependency or build tooling changes.
- Breaking changes to exported APIs.

### Never

- Commit secrets in source files.
- Remove tests or silently weaken assertions to satisfy CI.
