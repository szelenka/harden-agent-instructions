"""Checks for the nested-ops-repo scenario.

Fixture: an ops repo with root and nested service Makefiles.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_exists,
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
    results.append(hard("Created instruction file", inst is not None, channel="file"))
    if inst:
        results.append(hard(
            "References root Makefile or make verify",
            file_contains(generated_dir, inst, "make"),
            channel="file",
        ))
        results.append(hard(
            "References services/ml-proxy",
            file_contains(generated_dir, inst, "ml-proxy"),
            channel="file",
        ))
        results.append(hard(
            "References services/wordcloud",
            file_contains(generated_dir, inst, "wordcloud"),
            channel="file",
        ))
        results.append(hard(
            "Has commands in code blocks",
            file_has_fenced_block_containing(generated_dir, inst, "make"),
            channel="file",
        ))
        # Should preserve nested structure, not flatten
        results.append(hard(
            "Distinguishes root vs service workflows",
            file_contains(generated_dir, inst, "services/ml-proxy")
            or file_contains(generated_dir, inst, "services/wordcloud"),
            channel="file",
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not invent npm commands",
            file_not_contains_command(generated_dir, inst, "npm"),
            channel="file",
        ))
        results.append(hard(
            "Did not invent application entry point",
            file_not_contains(generated_dir, inst, "main.py")
            and file_not_contains(generated_dir, inst, "main.go")
            and file_not_contains(generated_dir, inst, "index.ts"),
            channel="file",
        ))

    return results
