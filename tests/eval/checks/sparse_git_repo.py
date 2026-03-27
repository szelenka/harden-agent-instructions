"""Checks for the sparse-git-repo scenario.

Fixture: a git-backed repo with no build manifest.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_not_contains_command,
    file_prescribes,
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
        # Anti-hallucination: must not invent build systems
        results.append(hard(
            "Did not prescribe package.json/pyproject.toml/go.mod",
            not file_prescribes(generated_dir, inst, "package.json")
            and not file_prescribes(generated_dir, inst, "pyproject.toml")
            and not file_prescribes(generated_dir, inst, "go.mod"),
        ))
        results.append(hard(
            "Did not invent npm/python/go/pip/poetry",
            file_not_contains_command(generated_dir, inst, "npm")
            and file_not_contains_command(generated_dir, inst, "python")
            and file_not_contains_command(generated_dir, inst, "go test", word_boundary=True)
            and file_not_contains_command(generated_dir, inst, "pip")
            and file_not_contains_command(generated_dir, inst, "poetry"),
        ))
        results.append(soft(
            "Acknowledges sparse/limited verification",
            file_contains(generated_dir, inst, "partial")
            or file_contains(generated_dir, inst, "limited")
            or file_contains(generated_dir, inst, "unavailable")
            or file_contains(generated_dir, inst, "sparse")
            or file_contains(generated_dir, inst, "no build")
            or file_contains(generated_dir, inst, "no test"),
        ))

    return results
