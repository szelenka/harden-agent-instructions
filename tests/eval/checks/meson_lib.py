"""Checks for the meson-lib scenario.

Fixture: a C library using the Meson build system.
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
            "Has meson commands in code block",
            file_has_fenced_block_containing(generated_dir, inst, "meson"),
        ))
        results.append(hard(
            "Mentions meson test or meson compile",
            file_contains(generated_dir, inst, "meson test")
            or file_contains(generated_dir, inst, "meson compile"),
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not invent cmake/npm/python/gcc",
            file_not_contains_command(generated_dir, inst, "cmake")
            and file_not_contains_command(generated_dir, inst, "npm")
            and file_not_contains_command(generated_dir, inst, "python")
            and file_not_contains_command(generated_dir, inst, "gcc"),
        ))

    return results
