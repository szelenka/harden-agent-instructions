"""Checks for the terraform-infra scenario.

Fixture: a Terraform infrastructure repo with modules and tfvars.
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
            "Has terraform commands in code block",
            file_has_fenced_block_containing(generated_dir, inst, "terraform"),
        ))
        results.append(hard(
            "Mentions terraform validate or plan",
            file_contains(generated_dir, inst, "terraform validate")
            or file_contains(generated_dir, inst, "terraform plan"),
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not invent npm/python/go/make",
            file_not_contains_command(generated_dir, inst, "npm")
            and file_not_contains_command(generated_dir, inst, "python")
            and file_not_contains_command(generated_dir, inst, "go test", word_boundary=True)
            and file_not_contains_command(generated_dir, inst, "make"),
        ))

    return results
