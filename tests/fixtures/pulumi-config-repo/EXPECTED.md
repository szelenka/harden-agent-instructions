# Expected Audit Results: pulumi-config-repo

A small Pulumi-style infra repo with root config files and the primary Node manifest nested under `config/`.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** `Pulumi.yaml` plus nested `config/package.json`
- **Verification reality:** nested workflow
  - `npm run lint` from `config/`
  - `npm run preview` from `config/`
  - `npm run deploy` from `config/`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks that make the nested working directory explicit
- Key paths with roles (`Pulumi.yaml` — stack runtime contract, `config/package.json` — operational scripts, `config/tools/preview.ts` — preview workflow)
- A note that the repo root is not the only workflow surface

## Key Signals

- The skill must recognize nested manifests and working-directory-sensitive commands
- The audit should avoid pretending the root has a flat package.json workflow
- The done checklist should preserve the `config/` execution context
