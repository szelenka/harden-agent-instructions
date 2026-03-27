"""Checks for the pulumi-config-repo scenario.

Fixture: a Pulumi infra repo with nested config/package.json workflow.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_has_fenced_block_containing,
    file_not_contains,
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
            "References Pulumi.yaml",
            file_contains(generated_dir, inst, "Pulumi.yaml") or file_contains(generated_dir, inst, "pulumi"),
        ))
        results.append(hard(
            "References config/ directory or nested workflow",
            file_contains(generated_dir, inst, "config/"),
        ))
        results.append(hard(
            "Has commands in code blocks",
            file_has_fenced_block_containing(generated_dir, inst, ""),
        ))
        # Anti-hallucination: should not pretend there's a root package.json workflow
        results.append(hard(
            "Did not invent pip/pytest commands",
            file_not_contains_command(generated_dir, inst, "pytest")
            and file_not_contains_command(generated_dir, inst, "pip install"),
        ))

    return results
