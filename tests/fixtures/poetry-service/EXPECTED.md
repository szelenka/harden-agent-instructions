# Expected Audit Results: poetry-service

A Python Flask service managed by Poetry with `poetry.lock`, `[tool.poetry]` in `pyproject.toml`, and a root `Makefile` wrapping Poetry commands. No instruction file.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** Poetry (`pyproject.toml` with `[tool.poetry]` + `poetry.lock`) plus root `Makefile`
- **Verification commands:** `make test`, `make lint`, `make typecheck` (backed by `poetry run pytest`, `poetry run ruff check`, `poetry run mypy`)

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks using Makefile targets: `make test`, `make lint`, `make typecheck`
- Key paths with roles (`app/main.py` — Flask entry point, `tests/test_main.py` — unit tests, `Makefile` — developer workflow entry point)
- Architecture description noting a Flask API managed by Poetry with Makefile convenience targets

## Key Signals

- The skill must identify both layers: `Makefile` targets as the canonical commands AND Poetry as the underlying tool — but instructions should always say `make test`, not `poetry run pytest`
- The audit should note Poetry as the dependency/virtualenv manager (from `poetry.lock` and `[tool.poetry]`) for context, not as the command interface
- The done checklist should use `make test`, `make lint`, and `make typecheck` as canonical verification
- The skill must NOT use `poetry run pytest`, `pip install`, bare `python -m pytest`, `uv run`, or `npm` as the instructed commands — the Makefile wraps these
- The skill should not treat the Makefile as the only signal — it must also recognize Poetry from the lockfile
