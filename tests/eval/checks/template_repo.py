"""Checks for the template-repo scenario.

Fixture: a scaffold/template repo with placeholder paths (cookiecutter).
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
            "References cookiecutter.json",
            file_contains(generated_dir, inst, "cookiecutter"),
        ))
        results.append(hard(
            "Has make render or similar in code block",
            file_has_fenced_block_containing(generated_dir, inst, "make")
            or file_has_fenced_block_containing(generated_dir, inst, "cookiecutter"),
        ))
        results.append(hard(
            "References hooks/post_gen_project.py",
            file_contains(generated_dir, inst, "post_gen_project")
            or file_contains(generated_dir, inst, "hooks/"),
        ))
        # Anti-hallucination: should not invent runtime app verification
        results.append(hard(
            "Did not invent pytest/npm test for the template itself",
            file_not_contains_command(generated_dir, inst, "pytest")
            and file_not_contains_command(generated_dir, inst, "npm test"),
        ))

    return results
