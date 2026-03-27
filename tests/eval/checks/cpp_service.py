"""Checks for the cpp-service scenario.

Fixture: a C++ service with CMakeLists.txt and a Makefile.

Hard checks should enforce the canonical verification surface, not require
literal mention of conventional source paths when they do not change routing.
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
            "References CMakeLists.txt or cmake or Makefile",
            file_contains(generated_dir, inst, "CMakeLists.txt")
            or file_contains(generated_dir, inst, "cmake")
            or file_contains(generated_dir, inst, "Makefile"),
        ))
        results.append(hard(
            "Has cmake/make/ctest commands in code block",
            file_has_fenced_block_containing(generated_dir, inst, "cmake")
            or file_has_fenced_block_containing(generated_dir, inst, "make")
            or file_has_fenced_block_containing(generated_dir, inst, "ctest"),
        ))
        results.append(hard(
            "Mentions clang-tidy or make lint",
            file_contains(generated_dir, inst, "clang-tidy")
            or file_has_fenced_block_containing(generated_dir, inst, "make lint"),
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not invent npm/Python/Go/Cargo commands",
            file_not_contains_command(generated_dir, inst, "npm")
            and file_not_contains_command(generated_dir, inst, "pytest")
            and file_not_contains_command(generated_dir, inst, "go test")
            and file_not_contains_command(generated_dir, inst, "cargo"),
        ))

    return results
