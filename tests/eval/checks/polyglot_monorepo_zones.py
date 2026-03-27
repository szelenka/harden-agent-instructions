"""Checks for the polyglot-monorepo-zones scenario.

Fixture: a polyglot monorepo with 3 operationally distinct zones
(Python billing, Go gateway, Terraform infra).
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
    soft,
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

    # Root instruction file
    results.append(hard("Created root instruction file", inst is not None, channel="file"))
    if inst:
        # Root should reference zone paths (zone pointer table)
        results.append(hard(
            "Root references billing path",
            file_contains(generated_dir, inst, "services/billing"),
            channel="file",
        ))
        results.append(hard(
            "Root references gateway path",
            file_contains(generated_dir, inst, "services/gateway"),
            channel="file",
        ))
        results.append(hard(
            "Root references infra path",
            file_contains(generated_dir, inst, "infra"),
            channel="file",
        ))
        # Anti-hallucination on root
        results.append(hard(
            "Root did not invent npm commands",
            file_not_contains_command(generated_dir, inst, "npm"),
            channel="file",
        ))
        results.append(hard(
            "Root did not invent cargo commands",
            file_not_contains_command(generated_dir, inst, "cargo", word_boundary=True),
            channel="file",
        ))

    # Zone files — this fixture's primary purpose is testing zone split
    billing_zone = "services/billing/AGENTS.md"
    gateway_zone = "services/gateway/AGENTS.md"
    infra_zone = "infra/AGENTS.md"

    results.append(hard(
        "Created services/billing/AGENTS.md",
        file_exists(generated_dir, billing_zone),
        channel="file",
    ))
    results.append(hard(
        "Created services/gateway/AGENTS.md",
        file_exists(generated_dir, gateway_zone),
        channel="file",
    ))
    results.append(hard(
        "Created infra/AGENTS.md",
        file_exists(generated_dir, infra_zone),
        channel="file",
    ))

    # Zone-specific commands in the correct zone file
    results.append(hard(
        "Billing zone has pytest command",
        file_has_fenced_block_containing(generated_dir, billing_zone, "pytest"),
        channel="file",
    ))
    results.append(hard(
        "Gateway zone has go test command",
        file_has_fenced_block_containing(generated_dir, gateway_zone, "go test"),
        channel="file",
    ))
    results.append(hard(
        "Infra zone has terraform command",
        file_has_fenced_block_containing(generated_dir, infra_zone, "terraform"),
        channel="file",
    ))

    # If zone files exist, verify no root constraint duplication
    has_zone_files = (
        file_exists(generated_dir, "services/billing/AGENTS.md")
        or file_exists(generated_dir, "services/gateway/AGENTS.md")
        or file_exists(generated_dir, "infra/AGENTS.md")
    )
    if has_zone_files and inst:
        root_content = (generated_dir / inst).read_text(encoding="utf-8", errors="replace").lower()
        for zone_path in ["services/billing/AGENTS.md", "services/gateway/AGENTS.md", "infra/AGENTS.md"]:
            zone_file = generated_dir / zone_path
            if zone_file.is_file():
                zone_content = zone_file.read_text(encoding="utf-8", errors="replace").lower()
                # Check that zone file doesn't restate "do not commit secrets" type rules
                has_duplication = (
                    "do not commit secrets" in zone_content
                    and "do not commit secrets" in root_content
                )
                results.append(soft(
                    f"Zone {zone_path} does not restate root constraints",
                    not has_duplication,
                    channel="file",
                ))

    return results
