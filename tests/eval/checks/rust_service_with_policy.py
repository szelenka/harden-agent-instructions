"""Checks for the rust-service-with-policy scenario."""

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

    results.append(hard("Created instruction file", inst is not None, channel="file"))
    if inst:
        results.append(hard(
            "Has cargo test in code block",
            file_has_fenced_block_containing(generated_dir, inst, "cargo test"),
            channel="file",
        ))
        results.append(hard(
            "Has cargo fmt --check in code block",
            file_has_fenced_block_containing(generated_dir, inst, "cargo fmt --check"),
            channel="file",
        ))
        results.append(hard(
            "Has cargo clippy in code block",
            file_has_fenced_block_containing(generated_dir, inst, "cargo clippy"),
            channel="file",
        ))
        results.append(hard(
            "Mentions Rust policy surfaces",
            file_contains(generated_dir, inst, "rustfmt.toml")
            and file_contains(generated_dir, inst, "Cargo.toml"),
            channel="file",
        ))
        results.append(hard(
            "Did not invent npm or Python commands",
            file_not_contains_command(generated_dir, inst, "npm")
            and file_not_contains_command(generated_dir, inst, "python -m pytest"),
            channel="file",
        ))

    return results
