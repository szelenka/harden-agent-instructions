"""Checks for the gradle-multimodule scenario.

Fixture: a multi-module Gradle repo with 3 subprojects sharing one build system.
This is a negative test for zone detection — no zone files should be created.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_exists,
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
    results.append(hard("Created instruction file", inst is not None, channel="file"))
    if inst:
        results.append(hard(
            "Has Gradle build command in code block",
            file_has_fenced_block_containing(generated_dir, inst, "gradlew"),
            channel="file",
        ))
        results.append(hard(
            "References build.gradle.kts",
            file_contains(generated_dir, inst, "build.gradle"),
            channel="file",
        ))
        # Anti-hallucination
        results.append(hard(
            "Did not invent npm commands",
            file_not_contains_command(generated_dir, inst, "npm"),
            channel="file",
        ))
        results.append(hard(
            "Did not invent pytest commands",
            file_not_contains_command(generated_dir, inst, "pytest", word_boundary=True),
            channel="file",
        ))

    # CRITICAL: no zone files should be created for Gradle subprojects
    results.append(hard(
        "No zone file in app/",
        not file_exists(generated_dir, "app/AGENTS.md"),
        channel="file",
    ))
    results.append(hard(
        "No zone file in core/",
        not file_exists(generated_dir, "core/AGENTS.md"),
        channel="file",
    ))
    results.append(hard(
        "No zone file in api/",
        not file_exists(generated_dir, "api/AGENTS.md"),
        channel="file",
    ))

    return results
