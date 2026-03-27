"""Checks for the makefile-only-mixed scenario.

Fixture: a repo with a root Makefile but no language-specific manifest.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_has_fenced_block_containing,
    file_not_contains_command,
    file_prescribes,
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
            "Has make commands in code block",
            file_has_fenced_block_containing(generated_dir, inst, "make lint")
            or file_has_fenced_block_containing(generated_dir, inst, "make render")
            or file_has_fenced_block_containing(generated_dir, inst, "make smoke-test"),
        ))
        # Anti-hallucination: must not invent language manifests
        results.append(hard(
            "Did not prescribe package.json/pyproject.toml/go.mod",
            not file_prescribes(generated_dir, inst, "package.json")
            and not file_prescribes(generated_dir, inst, "pyproject.toml")
            and not file_prescribes(generated_dir, inst, "go.mod"),
        ))
        results.append(hard(
            "Did not invent npm/Python/Go",
            file_not_contains_command(generated_dir, inst, "npm")
            and file_not_contains_command(generated_dir, inst, "python")
            and file_not_contains_command(generated_dir, inst, "go test", word_boundary=True),
        ))

    return results
