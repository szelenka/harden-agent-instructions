"""Checks for the weak-instructions scenario.

Fixture: a Go user service with a vague, non-actionable AGENTS.md.
The skill should flag anti-patterns and fix cold-start failures.
"""

from __future__ import annotations

from pathlib import Path

from .common import (
    CheckResult,
    file_contains,
    file_has_fenced_block_containing,
    hard,
)


def check(output: str, generated_dir: Path) -> list[CheckResult]:
    results: list[CheckResult] = []

    # --- Phase 3: Fix — check the edited AGENTS.md ---
    results.append(hard(
        "Edited AGENTS.md has fenced code blocks",
        file_has_fenced_block_containing(generated_dir, "AGENTS.md", ""),
    ))
    results.append(hard(
        "AGENTS.md mentions make targets",
        file_contains(generated_dir, "AGENTS.md", "make"),
    ))
    results.append(hard(
        "AGENTS.md mentions go test or make test",
        file_contains(generated_dir, "AGENTS.md", "go test")
        or file_contains(generated_dir, "AGENTS.md", "make test"),
    ))
    results.append(hard(
        "AGENTS.md mentions golangci-lint or make lint",
        file_contains(generated_dir, "AGENTS.md", "golangci-lint")
        or file_contains(generated_dir, "AGENTS.md", "make lint"),
    ))
    results.append(hard(
        "AGENTS.md references cmd/server/main.go",
        file_contains(generated_dir, "AGENTS.md", "cmd/server/main.go")
        or file_contains(generated_dir, "AGENTS.md", "cmd/server"),
    ))
    results.append(hard(
        "AGENTS.md has >= 3 concrete file paths",
        _count_paths(generated_dir) >= 3,
        "Counted paths matching internal/ or cmd/ references",
    ))

    # --- Anti-hallucination ---
    results.append(hard(
        "Did not invent npm commands",
        not file_contains(generated_dir, "AGENTS.md", "npm"),
    ))
    results.append(hard(
        "Did not invent pytest",
        not file_contains(generated_dir, "AGENTS.md", "pytest"),
    ))

    return results


def _count_paths(d: Path) -> int:
    """Count approximate concrete Go file paths in the instruction file."""
    path = d / "AGENTS.md"
    if not path.is_file():
        return 0
    content = path.read_text(encoding="utf-8", errors="replace")
    import re
    # Match paths like cmd/server/main.go, internal/routes/users.go, etc.
    paths = re.findall(r"(?:cmd|internal|pkg)/[\w/]+\.go", content)
    # Also count quoted slash paths and wildcard directory references such as
    # `internal/routes/*.go`, which are grounded and operational in this fixture.
    quoted = re.findall(r"`[a-zA-Z][\w./\-]+/[\w.*\-]+`", content)
    wildcard_dirs = re.findall(r"(?:cmd|internal|pkg)/[\w/\-]+/\*\.go", content)
    return len(set(paths) | set(quoted) | set(wildcard_dirs))
