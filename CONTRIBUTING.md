# Contributing

Thanks for contributing to this project.

## Before You Start

1. Read `AGENTS.md` and `README.md`.
2. Open an issue for significant changes.
3. Work in a feature branch from `main`.

## Development Workflow

1. Make focused, reviewable changes.
2. Run local validation before opening a PR.
3. Update docs when behavior or interfaces change.

## Setup and Validation

```bash
python3 tests/run_tests.py
```

## Pull Requests

1. Use a clear title and description.
2. Link related issues.
3. Include test evidence and risk notes.
4. Keep PR scope small; split unrelated work.

## Commit Messages

Use conventional commit style when possible:

```text
type(scope): summary
```

Examples:
- `feat(skill): add zone detection for monorepos`
- `fix(eval): correct contract check for missing paths`

## Code of Conduct

By participating, you agree to be respectful and constructive in all interactions.
