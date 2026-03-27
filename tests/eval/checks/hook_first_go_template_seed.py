"""Checks for the hook-first-go-template-seed scenario."""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_not_contains,
    file_not_contains_command,
    hard,
)
from .hook_first_go_repo import check as base_check

INSTRUCTION_FILES = ["AGENTS.md"]


def _find_inst(d: Path) -> str | None:
    for name in INSTRUCTION_FILES:
        if (d / name).is_file():
            return name
    return None


def check(output: str, generated_dir: Path) -> list[CheckResult]:
    results = list(base_check(output, generated_dir))
    inst = _find_inst(generated_dir)

    if inst:
        results.append(hard(
            "References runtime handler path",
            file_contains(generated_dir, inst, "service/handler.go"),
            channel="file",
        ))
        results.append(hard(
            "References test handler path",
            file_contains(generated_dir, inst, "service/handler_test.go"),
            channel="file",
        ))
        results.append(hard(
            "Removed generic Go install and lint residue",
            file_not_contains_command(generated_dir, inst, "go install ./...")
            and file_not_contains_command(generated_dir, inst, "golangci-lint run"),
            channel="file",
        ))
        results.append(hard(
            "Removed generic branch workflow residue",
            file_not_contains(generated_dir, inst, "feature/*")
            and file_not_contains(generated_dir, inst, "conventional commits"),
            channel="file",
        ))

    return results
