"""Checks for the hook-first-go-repo scenario."""

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

    results.append(hard("Created instruction file", inst is not None, channel="file"))
    if inst:
        results.append(hard(
            "References pre-commit config",
            file_contains(generated_dir, inst, "pre-commit-config"),
            channel="file",
        ))
        results.append(hard(
            "Has go test in code block",
            file_has_fenced_block_containing(generated_dir, inst, "go test ./..."),
            channel="file",
        ))
        results.append(hard(
            "Has go vet in code block",
            file_has_fenced_block_containing(generated_dir, inst, "go vet ./..."),
            channel="file",
        ))
        results.append(hard(
            "Did not invent Python commands",
            file_not_contains_command(generated_dir, inst, "python -m pytest"),
            channel="file",
        ))

    return results
