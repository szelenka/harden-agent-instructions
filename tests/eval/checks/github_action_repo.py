"""Checks for the github-action-repo scenario.

Fixture: a GitHub Action repo with action.yml and package.json.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_has_fenced_block_containing,
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
            "References action.yml as runtime contract",
            file_contains(generated_dir, inst, "action.yml"),
        ))
        results.append(hard(
            "References src/index.ts",
            file_contains(generated_dir, inst, "src/index.ts") or file_contains(generated_dir, inst, "index.ts"),
        ))
        results.append(hard(
            "Has npm or build commands in code block",
            file_has_fenced_block_containing(generated_dir, inst, "npm")
            or file_has_fenced_block_containing(generated_dir, inst, "build"),
        ))
        # Anti-hallucination: should not treat it as a web app.
        # Negation context is OK ("this is not a web server", "do not add express").
        results.append(hard(
            "Did not invent server/API architecture",
            not file_prescribes(generated_dir, inst, "api server")
            and not file_prescribes(generated_dir, inst, "web server")
            and not file_prescribes(generated_dir, inst, "express"),
        ))

    return results
