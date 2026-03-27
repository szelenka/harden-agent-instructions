# Tests

This directory contains fixture repos plus a lightweight regression harness for the `harden-instructions` skill.

## Fixtures

### `weak-instructions/`
A user service with a vague, non-actionable AGENTS.md. Tests the skill's ability to identify anti-patterns (abstract guidance, missing code blocks, zero file paths) and fix them in priority order.

### `solid-instructions/`
An invoice processor with a well-structured AGENTS.md. Tests the skill's ability to recognize good instructions and only flag minor improvements. The audit should pass cold-start checks immediately.

### `go-service/`
A Makefile-driven Go service with multiple command packages. Tests whether the skill treats `make` and `go test` as the canonical workflow instead of inventing npm or Poetry commands.

### `cpp-service/`
A small C++ service with `CMakeLists.txt` and a root `Makefile`. Tests whether the skill uses cmake/make commands and avoids inventing language-inappropriate workflows.

### `rust-cli/`
A Rust CLI with `Cargo.toml` and a root `Makefile`. Tests whether the skill uses `cargo` commands and avoids inventing non-Rust workflows.

### `rust-service-with-policy/`
A Rust CLI with `Cargo.toml` and explicit fmt/lint/test policy surfaces. Tests whether the skill recognizes strong policy signals without inventing absent commands.

### `infra-config/`
An infra/config repo with Helm-style structure and render/diff targets. Tests whether the skill avoids forcing application-centric architecture or unit-test assumptions onto deployment/config repos.

### `polyglot-monorepo-zones/`
A polyglot monorepo with 3 operationally distinct zones: a Python billing service, a Go API gateway, and Terraform infrastructure. Tests whether the skill creates zone-specific instruction files instead of flattening everything into the root.

### `gradle-multimodule/`
A multi-module Gradle repo with 3 subprojects sharing one build system, one runtime (Java 17), and one CI job. Tests whether the skill keeps instructions in a single root file instead of splitting into zones.

### `sparse-git-repo/`
A git-backed repo with docs, scripts, and config files but no reliable build manifest. Tests whether the skill degrades gracefully when canonical commands are unavailable.

### `makefile-only-mixed/`
A Makefile-driven repo with no language-specific manifest. Tests whether the skill treats `make` as primary without guessing the underlying stack.

### `nested-ops-repo/`
An ops repo with root and nested service `Makefile`s. Tests whether the skill preserves multiple sub-workflows instead of flattening them.

### `github-action-repo/`
A GitHub Action repo with `action.yml` and `package.json`. Tests whether the skill recognizes action packaging instead of generic app architecture.

### `pulumi-config-repo/`
An infra repo with `Pulumi.yaml` at the root and a nested `config/package.json`. Tests whether the skill preserves nested working-directory workflows.

### `pulumi-nested-config-template-seed/`
A Pulumi-style infra repo where a generic TypeScript-template AGENTS.md exists, but the primary Node manifest is nested under `config/`. Tests whether the skill replaces template boilerplate with repo-grounded instructions.

### `dockerfile-sparse-repo/`
A sparse repo where the strongest concrete signal is a `Dockerfile`. Tests whether the skill stays conservative when Docker is the only strong build artifact.

### `template-repo/`
A scaffold/template repo with placeholder paths. Tests whether the skill recognizes template variables instead of treating them as concrete repo modules.

### `workflow-first-repo/`
A repo where `.github/workflows/ci.yml` is the strongest operational truth. Tests whether the skill prefers workflow-backed checks over guessed local commands.

### `hook-first-go-repo/`
A Go repo where `.pre-commit-config.yaml` is the strongest operational truth and there is no stronger build manifest. Tests whether the skill treats hooks as canonical over generic Go-template commands.

### `hook-first-go-template-seed/`
A Go repo with a generic template-seeded AGENTS.md and `.pre-commit-config.yaml` as the strongest signal. Tests whether the skill replaces template boilerplate with repo-grounded instructions.

### `poetry-service/`
A Python Flask service managed by Poetry with `poetry.lock`. Tests whether the skill uses `poetry run` commands instead of bare `python -m pytest`.

### `terraform-infra/`
A Terraform infrastructure repo with modules and tfvars. Tests whether the skill uses `terraform` commands and avoids inventing application-level workflows.

### `meson-lib/`
A C library using the Meson build system. Tests whether the skill uses `meson` commands instead of `cmake` or `make`.

### `tox-django/`
A Django project with `tox.ini` managing test, lint, and typecheck environments. Tests whether the skill uses `tox` as the canonical runner instead of bare `pytest`.

## Automated Checks

Run the regression harness from the repo root:

```bash
python3 tests/run_tests.py
```

The harness validates:

1. `SKILL.md` stays short and keeps the highest-impact rules near the top
2. `AGENTS.md` stays aligned with the repo's actual instruction surface and shared guidance
3. `references/RUBRIC.md` and `references/GOLDEN_TASKS.md` contain the expected on-demand content
4. Fixture manifests still match the expectations documented in each fixture
5. Fixture `EXPECTED.md` files still encode the intended audit outcome
6. Weak and strong instruction examples still represent the anti-patterns and patterns this skill is meant to detect

## Manual Evaluation

You can still run the skill manually against each fixture and compare the outcome to `EXPECTED.md`:

```bash
# Example prompts for an agent with the skill installed:
# "Audit the instructions for the repo at tests/fixtures/weak-instructions"
# "Audit the instructions for the repo at tests/fixtures/solid-instructions"
# "Audit the instructions for the repo at tests/fixtures/hook-first-go-template-seed"
```

## Agent-Driven Evaluations

The `eval/` directory contains structured scenarios for testing the skill end-to-end with real agent CLIs, including Claude and Codex. These test **agent behavior** — whether the agent produces correct audit output when using the skill.

See [`eval/README.md`](eval/README.md) for setup and usage.

Each scenario has:
- A **prompt** (`eval/scenarios/*.txt`) to feed to the agent CLI
- A deterministic **contract** (`eval/contracts/*.json`) for required and forbidden behavior
- A scenario-specific **check module** (`eval/checks/*.py`) for additional hard and soft assertions

Run all 24 scenarios against each model before publishing a new version of the skill.
