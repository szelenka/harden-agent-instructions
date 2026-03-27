"""Checks for the solid-instructions scenario.

Fixture: an invoice processor with a well-structured AGENTS.md.
The skill should preserve the strong file and avoid degrading key guidance.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    contains,
    file_contains,
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

    results.append(hard(
        "AGENTS.md still exists",
        inst is not None,
        channel="file",
    ))

    if inst:
        content = (generated_dir / inst).read_text(encoding="utf-8", errors="replace")
        results.append(hard(
            "Preserves hard rules salience",
            file_contains(generated_dir, inst, "HARD RULES"),
            channel="file",
        ))
        results.append(hard(
            "Preserves request flow guidance",
            contains(content, "route -> validate")
            and contains(content, "service -> prisma -> response"),
            channel="file",
        ))
        results.append(hard(
            "Preserves validator and service boundaries",
            file_contains(generated_dir, inst, "src/validators/")
            and file_contains(generated_dir, inst, "src/services/")
            and file_contains(generated_dir, inst, "src/internal/"),
            channel="file",
        ))
        results.append(hard(
            "Preserves done checklist invariants",
            contains(content, "npm run check")
            and contains(content, "prisma migrate dev --create-only"),
            channel="file",
        ))

    return results
