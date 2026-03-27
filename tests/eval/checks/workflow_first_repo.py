"""Checks for the workflow-first-repo scenario.

Fixture: a small repo where .github/workflows/ci.yml is the strongest operational truth.
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

    # Fix — generated file
    results.append(hard("Created instruction file", inst is not None))
    if inst:
        results.append(hard(
            "References ci.yml",
            file_contains(generated_dir, inst, "ci.yml"),
        ))
        results.append(hard(
            "Has pytest in code block",
            file_has_fenced_block_containing(generated_dir, inst, "pytest"),
        ))
        results.append(hard(
            "Has ruff in code block",
            file_has_fenced_block_containing(generated_dir, inst, "ruff"),
        ))
        results.append(hard(
            "References app/main.py",
            file_contains(generated_dir, inst, "app/main.py") or file_contains(generated_dir, inst, "main.py"),
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not invent npm commands",
            file_not_contains_command(generated_dir, inst, "npm"),
        ))

    return results
