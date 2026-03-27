# harden-agent-instructions

## Hard Rules

- NEVER edit `tests/fixtures/` without explicit request. Fixtures are calibration data, not code to improve.
- `skills/harden-agent-instructions/SKILL.md` must stay under 300 lines. If it grows past that, move detail into `skills/harden-agent-instructions/references/`.
- `tests/run_tests.py` must pass before any change is considered done.
- Do not add runtime dependencies. This repo is Markdown plus a Python test harness.
- If you discover a reusable convention, failure pattern, or missing rule, persist it into `AGENTS.md` or the relevant `references/` file before ending the session.
- If you run the same non-trivial shell command 3+ times in one session, promote it into a named script or test helper before running it again.
- If you edit `SKILL.md` or `RUBRIC.md`, verify the same behavior is still represented consistently in both `README.md` and `AGENTS.md` before finishing.
- Keep root `AGENTS.md` operational: constraints, commands, boundaries, non-obvious caveats, and done criteria. Agent rules belong in `AGENTS.md` and `SKILL.md`; human-oriented explanation belongs elsewhere.

## Build & Test

```bash
python3 tests/run_tests.py
```

- There is no build step, CI pipeline, or pre-commit hook in this repo today. Manual enforcement relies on `python3 tests/run_tests.py`.
- After editing `SKILL.md` or `skills/harden-agent-instructions/references/RUBRIC.md`, also run:

```bash
python3 tests/eval/run_eval.py --smoke --variance 5 --skip-judge --timeout 600
```

- If smoke variance improves and you intend to keep the new behavior, update the baseline with `--update-baseline`.

## Key Files

| File | Role |
|------|------|
| `AGENTS.md` | Repo maintenance instructions for agents editing this skill package |
| `skills/harden-agent-instructions/SKILL.md` | Primary execution playbook loaded on skill activation |
| `skills/harden-agent-instructions/references/RUBRIC.md` | Scoring rubric and fix-priority crosswalk |
| `skills/harden-agent-instructions/references/GOLDEN_TASKS.md` | Worked examples and handoff patterns |
| `tests/run_tests.py` | Structural regression harness; must pass before completion |
| `tests/eval/run_eval.py` | Smoke and variance eval runner |
| `tests/eval/contracts/` | Deterministic eval contracts |
| `README.md` | Human-facing overview and usage |

Tool-specific install metadata lives in `.claude-plugin/` and `.cursor-plugin/`; keep install claims grounded in those checked-in surfaces.

## Repo Conventions

- Prefer concrete wording: exact paths, command names, approval triggers, and deterministic verification.
- Treat `tests/run_tests.py` plus the current tree as the source of truth when docs disagree.
- Keep shared terms aligned across `SKILL.md`, `RUBRIC.md`, `README.md`, and `AGENTS.md`.
- If no CI or hooks exist, agents may recommend lightweight enforcement, but must not invent new workflow or hook paths that are not already present.
- Install instructions and marketplace claims must be backed by checked-in manifests, canonical repo paths, or other repo-local evidence plus one verification step.
- `README.md` is human-facing; do not move agent-operational rules or install-surface policy out of `AGENTS.md` / `SKILL.md`.

## Eval Maintenance

- Prefer deterministic contracts in `tests/eval/contracts/` and matching checks in `tests/eval/checks/` over prose-only expectations.
- Separate mechanical regressions from judgment-call regressions when reviewing eval output.
- If an eval result changes unexpectedly, check whether the fixture, contract, or skill changed before debugging the agent.
- New fixtures must justify a distinct failure mode. Do not add near-duplicate language or tool variants.
- Every fixture should include a build manifest, representative repo artifacts, and `EXPECTED.md`.
- When adding, renaming, or deleting eval scenarios, reconcile `tests/eval/scenarios/`, `tests/eval/contracts/`, `tests/eval/checks/`, stale assets, archived run subtrees, and `tests/eval/baseline.json` in the same change.

## Scope Boundaries

| Area | Permission | Condition |
|------|-----------|-----------|
| `AGENTS.md` | Read-write | Any session |
| `skills/harden-agent-instructions/SKILL.md` | Read-write | Keep under 300 lines and re-run tests after edits |
| `skills/harden-agent-instructions/references/*.md` | Read-write | Update when rubric criteria or examples change |
| `tests/run_tests.py` | Read-write | Only add or modify `test_*` functions; do not remove assertions without explicit request |
| `tests/eval/` | Read-write | Scenarios, contracts, checks, runner, and baselines |
| `tests/fixtures/` | Read-only | Never edit without explicit request |
| `README.md` | Read-write | Human-facing only |

## Codebase Drift Prevention

- Extend `SKILL.md`, `RUBRIC.md`, or `GOLDEN_TASKS.md` before creating a parallel doc that duplicates agent guidance.
- If you add or rename a rubric criterion that maps to a required `SKILL.md` section, update `RUBRIC.md` and the `SKILL.md` tier table in the same change.
- If you change shared guidance in `AGENTS.md` or `README.md`, reconcile overlapping facts and rules in both files in the same change.
- If you change `SKILL.md` or `RUBRIC.md`, reconcile any overlapping summary in `README.md` and any repo-level enforcement note in `AGENTS.md` before finishing.
- If `.git/` metadata is absent, mark contributor history and source-control workflow as unavailable instead of inventing policy.
- Only change fixture `EXPECTED.md` files when the intended audit standard changed.

## Verification (Done Checklist)

1. `python3 tests/run_tests.py` exits 0.
2. `skills/harden-agent-instructions/SKILL.md` stays under 300 lines.
3. No fixture files were modified unless explicitly requested.
4. If you added a rubric criterion tied to a required `SKILL.md` section, it appears in both `RUBRIC.md` and the `SKILL.md` tier table.
5. If you changed shared guidance in `AGENTS.md` or `README.md`, overlapping rules still agree.
6. If you changed `SKILL.md` or `RUBRIC.md`, `README.md` and `AGENTS.md` still describe the same repo-specific behavior.
7. If you changed `SKILL.md` or `RUBRIC.md`, smoke variance shows no hard regression versus baseline.
8. If you added a fixture, it includes a build manifest, representative repo artifacts, and `EXPECTED.md`.
