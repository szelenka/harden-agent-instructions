"""Checks for the pulumi-nested-config-template-seed scenario."""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_not_contains,
    file_not_contains_command,
    hard,
)
from .pulumi_config_repo import check as base_check

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
            "References nested preview workflow path",
            file_contains(generated_dir, inst, "config/tools/preview.ts"),
            channel="file",
        ))
        results.append(hard(
            "Removed flat-root Node workflow residue",
            file_not_contains_command(generated_dir, inst, "npm ci")
            and file_not_contains_command(generated_dir, inst, "npm test")
            and file_not_contains_command(generated_dir, inst, "npm run build")
            and file_not_contains_command(generated_dir, inst, "npm run typecheck"),
            channel="file",
        ))
        results.append(hard(
            "Removed generic TypeScript template workflow residue",
            file_not_contains(generated_dir, inst, "feature/*")
            and file_not_contains(generated_dir, inst, "conventional commits"),
            channel="file",
        ))
        results.append(hard(
            "Makes nested config scope explicit",
            file_contains(generated_dir, inst, "config/")
            and file_contains(generated_dir, inst, "config/package.json"),
            channel="file",
        ))

    return results
