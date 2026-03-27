.PHONY: install test lint typecheck fmt

install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run ruff check .

typecheck:
	poetry run mypy app/

fmt:
	poetry run ruff format .
