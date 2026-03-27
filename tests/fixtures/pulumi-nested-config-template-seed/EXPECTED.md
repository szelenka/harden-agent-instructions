# Expected Audit Results: pulumi-nested-config-template-seed

A small Pulumi-style infra repo where a generic TypeScript-template `AGENTS.md` exists, but the primary Node manifest is nested under `config/`.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (instruction file exists, but it still assumes a flat root Node workflow)
- **Repo tier:** small
- **Instruction files found:** `AGENTS.md`
- **Build system:** `Pulumi.yaml` plus nested `config/package.json`
- **Verification reality:** nested workflow
  - `npm run lint` from `config/`
  - `npm run preview` from `config/`
  - `npm run deploy` from `config/`

## Expected Phase 3 Actions

The skill should rewrite the existing `AGENTS.md` so it:
- Removes generic TypeScript-template workflow residue
- Uses commands in fenced code blocks that make the nested working directory explicit
- Names key paths with roles (`Pulumi.yaml` — stack runtime contract, `config/package.json` — operational scripts, `config/tools/preview.ts` — preview workflow)
- Notes that the repo root is not the only workflow surface

## Key Signals

- The skill must override the generic root-level Node workflow when nested manifest evidence is stronger
- The audit should avoid pretending the root has a flat package.json workflow
- The done checklist should preserve the `config/` execution context
