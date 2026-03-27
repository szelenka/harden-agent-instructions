# Agent-Driven Evaluation

Structured scenarios for testing the skill end-to-end with real agent CLIs.

## Purpose

The regression harness (`tests/run_tests.py`) validates skill structure and fixture consistency. These evaluations test **agent behavior** — whether an agent actually produces the right audit output when using the skill against each fixture.

## Prerequisites

- `claude` CLI and/or `codex` CLI installed and authenticated
- Access to the models you want to test

## Automated Runner

`run_eval.py` invokes the agent CLI per scenario, runs mechanical checks on the output and generated files, and optionally runs an LLM judge to compare the generated instruction file against `EXPECTED.md`.

Deterministic end-to-end enforcement lives in `tests/eval/contracts/`: each contract defines required commands, forbidden inventions, required paths, expected status lines, and protected files for a scenario. Prefer expanding these contracts and the hard mechanical checks before adding more LLM-judge logic.

For fast local validation of the contract engine itself, `--self-test <scenario>` replays the latest archived `output.md` plus `.generated/` snapshot from `tests/eval/runs/` and reruns the deterministic checks without calling `claude` or `codex`.

## How Scoring Works

The eval system has two distinct modes:

1. **Live eval** — run a real agent CLI against a fixture repo. The agent produces raw output plus a generated repo snapshot under `tests/eval/runs/<timestamp>/`.
2. **Deterministic scoring** — apply the scenario contract from `tests/eval/contracts/<name>.json` to that saved output and generated snapshot. This is the pass/fail layer for required commands, forbidden inventions, required paths, expected status lines, and protected-file non-edits.

`--self-test <scenario>` replays the latest archived run for a scenario and reruns the deterministic scorer only. Use it to validate the contract engine and contract expectations without calling a live model.

The optional LLM judge is advisory only. It can help compare generated instructions to `EXPECTED.md`, but it is not the source of truth for pass/fail.

```bash
# List available scenarios and check status
python3 tests/eval/run_eval.py --list

# Run all scenarios with the default tool (claude) and model (sonnet)
python3 tests/eval/run_eval.py

# Run with codex
python3 tests/eval/run_eval.py --tool codex --model gpt-5.4

# Run specific scenarios against multiple claude models
python3 tests/eval/run_eval.py --scenario weak-instructions rust-cli --model haiku sonnet opus

# Run both tools at once (each uses its default model)
python3 tests/eval/run_eval.py --tool claude codex

# Run both tools in parallel (all combos at once, the default)
python3 tests/eval/run_eval.py --tool claude codex

# Run all scenarios, multiple models (models auto-route to matching tools)
python3 tests/eval/run_eval.py --tool claude codex --model sonnet opus gpt-5.4

# Cap parallelism at 4 concurrent agents
python3 tests/eval/run_eval.py --tool claude codex --model sonnet opus gpt-5.4 -j 4

# Run sequentially (one at a time)
python3 tests/eval/run_eval.py -j 1

# Run each combo 3 times to measure variance
python3 tests/eval/run_eval.py --scenario rust-cli --model sonnet --variance 3

# Skip the LLM judge layer
python3 tests/eval/run_eval.py --skip-judge

# Replay the latest archived run for a scenario, no live agent CLI required
python3 tests/eval/run_eval.py --self-test rust-cli

# Resume a previous run (skip completed combos)
python3 tests/eval/run_eval.py --resume 2026-03-21T14-30-00

# Rerun only combos that had hard failures
python3 tests/eval/run_eval.py --rerun-failures 2026-03-21T14-30-00
```

Results are written to `tests/eval/runs/<timestamp>/` (gitignored) with raw output, mechanical check results, and generated file snapshots. A local rollup is written to `tests/eval/results.md`.

`tests/eval/results.md` is scratch output, not a published baseline. If a copy is already present in the workspace, treat it as the last local run until you refresh it.

`tests/eval/baseline.json` is the committed compact baseline for variance regression detection. It stores per-scenario summary stability numbers, not the full per-check detail from a run.

### Supported tools and models

| Tool | Models | Default |
|------|--------|---------|
| `claude` | `haiku`, `sonnet`, `opus` | `sonnet` |
| `codex` | `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.3-codex`, `gpt-5.3-codex-spark-preview`, `gpt-5.2-codex`, `gpt-5.2`, `gpt-5.1-codex-max`, `gpt-5.1-codex-mini` | `gpt-5.4` |

When `--model` is combined with multiple `--tool` values, each model is routed only to the tool that recognizes it. For example, `--tool claude codex --model sonnet gpt-5.4` runs claude/sonnet and codex/gpt-5.4 (not claude/gpt-5.4 or codex/sonnet). Raw model IDs (containing `/` or `:`, e.g. Bedrock ARNs) are passed through to all tools.

### Check tiers

- **Hard checks** — structural facts (file created, command in code block, path referenced). Failures produce exit code 1.
- **Soft checks** — output-text dependent (phrasing of cold-start status, tier classification). Reported but don't gate the exit code.
- **LLM judge** — advisory only. Compares the generated instruction file against `EXPECTED.md` for contradictions.

## Manual Evaluation

You can still run scenarios by hand:

```bash
claude -p \
  --model <model> \
  --allowedTools "Read Glob Grep Bash" \
  --append-system-prompt "$(cat skills/harden-agent-instructions/SKILL.md)" \
  < tests/eval/scenarios/<scenario>.txt
```

## Scenarios

Each file in `scenarios/` contains a self-contained prompt. After running, inspect the deterministic contract result plus any generated-file diffs or assets for the scenario.

| Scenario | Fixture | Tests |
|----------|---------|-------|
| `cpp-service.txt` | `tests/fixtures/cpp-service/` | Uses CMake/CTest/clang-tidy build and verification guidance |
| `dockerfile-sparse-repo.txt` | `tests/fixtures/dockerfile-sparse-repo/` | Stays conservative when Docker is the only strong build artifact |
| `github-action-repo.txt` | `tests/fixtures/github-action-repo/` | Treats `action.yml` as the runtime contract instead of generic app architecture |
| `go-service.txt` | `tests/fixtures/go-service/` | Uses `make` and `go test` as canonical workflow |
| `gradle-multimodule.txt` | `tests/fixtures/gradle-multimodule/` | Keeps instructions in single root file for shared Gradle build |
| `hook-first-go-repo.txt` | `tests/fixtures/hook-first-go-repo/` | Prioritizes `.pre-commit-config.yaml` as the verification source of truth for Go workflows |
| `hook-first-go-template-seed.txt` | `tests/fixtures/hook-first-go-template-seed/` | Hardens a generic Go template toward hook-backed verification |
| `infra-config.txt` | `tests/fixtures/infra-config/` | Avoids forcing app-centric architecture onto deployment/config repos |
| `makefile-only-mixed.txt` | `tests/fixtures/makefile-only-mixed/` | Uses Makefile as primary workflow without guessing the language |
| `meson-lib.txt` | `tests/fixtures/meson-lib/` | Uses `meson` commands instead of cmake or make |
| `nested-ops-repo.txt` | `tests/fixtures/nested-ops-repo/` | Preserves root and nested service workflows without flattening them |
| `poetry-service.txt` | `tests/fixtures/poetry-service/` | Uses `poetry run` commands instead of bare `python -m pytest` |
| `polyglot-monorepo-zones.txt` | `tests/fixtures/polyglot-monorepo-zones/` | Creates zone-specific instruction files for operationally distinct zones |
| `pulumi-config-repo.txt` | `tests/fixtures/pulumi-config-repo/` | Preserves nested `config/` workflow and working directory context |
| `pulumi-nested-config-template-seed.txt` | `tests/fixtures/pulumi-nested-config-template-seed/` | Hardens a generic TypeScript template toward nested `config/` workflows |
| `rust-cli.txt` | `tests/fixtures/rust-cli/` | Uses Cargo/Rust-native build and verification guidance |
| `rust-service-with-policy.txt` | `tests/fixtures/rust-service-with-policy/` | Preserves a Rust repo's multi-surface verification contract: test, fmt-check, and clippy |
| `solid-instructions.txt` | `tests/fixtures/solid-instructions/` | Passes cold-start, avoids over-editing |
| `sparse-git-repo.txt` | `tests/fixtures/sparse-git-repo/` | Degrades gracefully when canonical commands are unavailable |
| `template-repo.txt` | `tests/fixtures/template-repo/` | Recognizes placeholder paths as templates rather than concrete modules |
| `terraform-infra.txt` | `tests/fixtures/terraform-infra/` | Uses `terraform` commands and avoids inventing app-level workflows |
| `tox-django.txt` | `tests/fixtures/tox-django/` | Uses `tox` as canonical runner instead of bare `pytest` |
| `weak-instructions.txt` | `tests/fixtures/weak-instructions/` | Identifies anti-patterns in a Go project, flags cold-start failures |
| `workflow-first-repo.txt` | `tests/fixtures/workflow-first-repo/` | Prioritizes `.github/workflows/ci.yml` as the verification source of truth |

## Evaluating Results

Review the deterministic hard/soft check results for the scenario and compare the generated instruction file against `EXPECTED.md` only when you need additional qualitative context.

Record results in `tests/eval/results.md` (gitignored scratch output) using this format:

```markdown
## Run: YYYY-MM-DD

### rust-cli

| Model | Cold-start created | Commands in blocks | Paths correct | Overall |
|-------|--------------------|--------------------|---------------|---------|
| haiku | pass/fail | pass/fail | pass/fail | pass/fail |
| sonnet | pass/fail | pass/fail | pass/fail | pass/fail |
| opus | pass/fail | pass/fail | pass/fail | pass/fail |
```

## When to Run

- After editing SKILL.md or reference files
- Before publishing a new version of the skill
- When upgrading to a new Claude model family
