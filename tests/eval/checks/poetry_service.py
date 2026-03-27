"""Checks for the poetry-service scenario.

Fixture: a Python Flask service managed by Poetry with a Makefile wrapping Poetry commands.
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
            "Has make commands in code block",
            file_has_fenced_block_containing(generated_dir, inst, "make test")
            or file_has_fenced_block_containing(generated_dir, inst, "make lint"),
        ))
        results.append(soft(
            "Mentions Poetry as dependency manager",
            file_contains(generated_dir, inst, "poetry"),
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not prescribe poetry run as primary command",
            file_not_contains_command(generated_dir, inst, "poetry run pytest")
            and file_not_contains_command(generated_dir, inst, "pip install"),
        ))
        results.append(hard(
            "Did not invent npm",
            file_not_contains_command(generated_dir, inst, "npm"),
        ))

    return results
