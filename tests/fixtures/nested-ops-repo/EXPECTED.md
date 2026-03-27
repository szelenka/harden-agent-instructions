# Expected Audit Results: nested-ops-repo

A small operations repo with a root `Makefile` and multiple nested service directories, each with its own workflow.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** root `Makefile` plus nested service `Makefile`s
- **Verification reality:** split across subdirectories
  - `make verify` at the root
  - `make -C services/ml-proxy lint`
  - `make -C services/ml-proxy render`
  - `make -C services/wordcloud diff`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- A note that the repo has several sub-workflows rather than one flat command surface
- Commands in fenced code blocks for the root and nested service workflows
- Key paths with roles (`services/ml-proxy/Makefile` — ml proxy deploy checks, `services/wordcloud/Makefile` — wordcloud diff workflow, `clusters/dev/values.yaml` — shared environment values)

## Zone Regression Assertion

- **Zones detected:** 0
- **Why:** per-service Makefiles have different targets but share the same toolchain (Helm/helmfile), no distinct runtimes or build manifests per subtree, no separate CI jobs, and a root `make verify` orchestrates all sub-targets. This is one operational surface with sub-targets, not independent zones.
- No zone-specific `AGENTS.md` files should be created in `services/ml-proxy/` or `services/wordcloud/`

## Key Signals

- The skill must enumerate root and nested workflows instead of flattening them into one command list
- The audit should avoid pretending this repo has a single application entry point
- The done checklist should say when focused subdirectory verification is sufficient versus when root verification is needed
