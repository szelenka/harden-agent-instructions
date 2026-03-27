"""Checks for the rust-cli scenario.

Fixture: a Rust CLI with Cargo.toml and a Makefile.

Hard checks should enforce the canonical verification surface, not require
literal mention of root-level discoverable files.
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
            "Uses canonical Rust verification surface",
            file_has_fenced_block_containing(generated_dir, inst, "cargo")
            or file_has_fenced_block_containing(generated_dir, inst, "make build")
            or file_has_fenced_block_containing(generated_dir, inst, "make test"),
        ))
        results.append(hard(
            "Has cargo or make commands in code block",
            file_has_fenced_block_containing(generated_dir, inst, "cargo")
            or file_has_fenced_block_containing(generated_dir, inst, "make"),
        ))
        results.append(hard(
            "Mentions clippy or make lint",
            file_contains(generated_dir, inst, "clippy")
            or file_has_fenced_block_containing(generated_dir, inst, "make lint"),
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not invent npm/Python/Go commands",
            file_not_contains_command(generated_dir, inst, "npm")
            and file_not_contains_command(generated_dir, inst, "pytest")
            and file_not_contains_command(generated_dir, inst, "go test", word_boundary=True),
        ))

    return results
