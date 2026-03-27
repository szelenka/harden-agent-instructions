"""Checks for the go-service scenario.

Fixture: a Go service with go.mod and a root Makefile.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_has_fenced_block_containing,
    file_not_contains_command,
    hard,
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
            "Has make or go commands in code block",
            file_has_fenced_block_containing(generated_dir, inst, "make")
            or file_has_fenced_block_containing(generated_dir, inst, "go test"),
        ))
        results.append(hard(
            "Mentions cmd/ or internal/ layout",
            file_contains(generated_dir, inst, "cmd/")
            or file_contains(generated_dir, inst, "internal/"),
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not invent npm/Python/Poetry",
            file_not_contains_command(generated_dir, inst, "npm")
            and file_not_contains_command(generated_dir, inst, "python")
            and file_not_contains_command(generated_dir, inst, "poetry"),
        ))

    return results
