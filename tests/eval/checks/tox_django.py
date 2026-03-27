"""Checks for the tox-django scenario.

Fixture: a Django project with tox.ini managing test/lint/typecheck envs.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_has_fenced_block_containing,
    file_not_contains_command,
    hard,
    soft,
)

INSTRUCTION_FILES = ["AGENTS.md"]


def _find_inst(d: Path) -> str | None:
    for name in INSTRUCTION_FILES:
        if (d / name).is_file():
            return name
    return None


def check(output: str, generated_dir: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    inst = _find_inst(generated_dir)

    # Fix
    results.append(hard("Created instruction file", inst is not None))
    if inst:
        results.append(hard(
            "Has tox commands in code block",
            file_has_fenced_block_containing(generated_dir, inst, "tox"),
        ))
        results.append(soft(
            "Mentions tox environments",
            file_contains(generated_dir, inst, "lint")
            or file_contains(generated_dir, inst, "typecheck")
            or file_contains(generated_dir, inst, "py312"),
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not prescribe bare pytest as primary",
            file_not_contains_command(generated_dir, inst, "pip install")
            and file_not_contains_command(generated_dir, inst, "npm"),
        ))

    return results
