"""Checks for the infra-config scenario.

Fixture: a Helm/infra config repo with a root Makefile.
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
            file_has_fenced_block_containing(generated_dir, inst, "make lint")
            or file_has_fenced_block_containing(generated_dir, inst, "make render")
            or file_has_fenced_block_containing(generated_dir, inst, "make diff"),
        ))
        results.append(soft(
            "Describes repo as infra/config",
            file_contains(generated_dir, inst, "infra")
            or file_contains(generated_dir, inst, "config")
            or file_contains(generated_dir, inst, "helm")
            or file_contains(generated_dir, inst, "deploy"),
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not invent npm/Python/Go",
            file_not_contains_command(generated_dir, inst, "npm")
            and file_not_contains_command(generated_dir, inst, "python")
            and file_not_contains_command(generated_dir, inst, "go test", word_boundary=True),
        ))

    return results
