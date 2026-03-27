# Expected Audit Results: github-action-repo

A small GitHub Action repo with `action.yml`, `package.json`, and no instruction file.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** `package.json` plus `action.yml`
- **Verification commands:** `npm run build`, `npm run lint`, `npm run test`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks (`npm run build`, `npm run lint`, `npm run test`)
- Key paths with roles (`action.yml` — action entry contract, `src/index.ts` — action implementation, `test/index.test.js` — deterministic verification)
- A note that this repo builds a GitHub Action, not a generic web app

## Key Signals

- The skill must recognize `action.yml` as the primary runtime contract
- The audit should avoid inventing server architecture or API-layer guidance
- The done checklist should focus on build/lint/test and action packaging
