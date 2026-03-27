# Expected Audit Results: tox-django

A Django project with `tox.ini` managing test, lint, and typecheck environments. No instruction file.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** tox (`tox.ini`) wrapping pytest, ruff, and mypy
- **Verification commands:** `tox` (runs all environments), `tox -e py312`, `tox -e lint`, `tox -e typecheck`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks (`tox`, `tox -e py312`, `tox -e lint`, `tox -e typecheck`)
- Key paths with roles (`src/todos/models.py` — Django models, `src/todos/views.py` — view handlers, `src/settings.py` — Django settings, `tests/test_views.py` — unit tests, `tox.ini` — test environment orchestration)
- Architecture description noting a Django app with tox-managed multi-environment verification

## Key Signals

- The skill must use `tox` as the canonical test runner, NOT bare `pytest`, `python -m pytest`, or `python manage.py test` — the `tox.ini` is the orchestration surface
- The audit should note that tox manages three environments: `py312` (tests), `lint` (ruff), `typecheck` (mypy)
- The done checklist should use `tox` as the single canonical verification command
- The skill must NOT invent `pip install`, `poetry run`, `npm`, or `manage.py` commands as primary workflow
