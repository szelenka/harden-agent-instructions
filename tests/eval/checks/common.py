"""Shared primitives for eval check modules."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import NamedTuple


class CheckResult(NamedTuple):
    name: str
    status: str  # "pass", "fail", "soft_fail", "skip"
    tier: str  # "hard" or "soft"
    channel: str = "general"  # "output", "file", "contract", or "general"
    detail: str = ""


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    """Lowercase and collapse whitespace for fuzzy matching."""
    return re.sub(r"\s+", " ", text.lower().strip())


def contains(text: str, needle: str, *, case_sensitive: bool = False) -> bool:
    if case_sensitive:
        return needle in text
    return needle.lower() in _norm(text)


def contains_any(text: str, needles: list[str], *, case_sensitive: bool = False) -> bool:
    return any(contains(text, n, case_sensitive=case_sensitive) for n in needles)


def not_contains(text: str, needle: str, *, case_sensitive: bool = False) -> bool:
    return not contains(text, needle, case_sensitive=case_sensitive)


def has_fenced_block_containing(text: str, needle: str, *, word_boundary: bool = False) -> bool:
    """True if *needle* appears inside a fenced code block (``` ... ```).

    If *word_boundary* is True, the needle must appear as a whole word
    (not as a substring of another word, e.g. "go test" inside "cargo test").
    """
    in_block = False
    if word_boundary:
        pattern = re.compile(r"(?<![a-zA-Z])" + re.escape(needle) + r"(?![a-zA-Z])", re.IGNORECASE)
    else:
        needle_lower = needle.lower()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_block = not in_block
            continue
        if in_block:
            if word_boundary:
                if pattern.search(line):
                    return True
            elif needle_lower in line.lower():
                return True
    return False


def matches_regex(text: str, pattern: str, flags: int = re.IGNORECASE | re.MULTILINE) -> bool:
    return bool(re.search(pattern, text, flags))


# ---------------------------------------------------------------------------
# File-system helpers (operate on the generated tempdir snapshot)
# ---------------------------------------------------------------------------

def file_exists(directory: Path, relative: str) -> bool:
    return (directory / relative).is_file()


def file_contains(directory: Path, relative: str, needle: str, *, case_sensitive: bool = False) -> bool:
    path = directory / relative
    if not path.is_file():
        return False
    content = path.read_text(encoding="utf-8", errors="replace")
    return contains(content, needle, case_sensitive=case_sensitive)


def file_not_contains(directory: Path, relative: str, needle: str, *, case_sensitive: bool = False) -> bool:
    path = directory / relative
    if not path.is_file():
        return True  # file doesn't exist, so it can't contain the needle
    content = path.read_text(encoding="utf-8", errors="replace")
    return not_contains(content, needle, case_sensitive=case_sensitive)


def file_has_fenced_block_containing(directory: Path, relative: str, needle: str) -> bool:
    path = directory / relative
    if not path.is_file():
        return False
    content = path.read_text(encoding="utf-8", errors="replace")
    return has_fenced_block_containing(content, needle)


def file_not_contains_command(
    directory: Path, relative: str, needle: str, *, word_boundary: bool = False,
) -> bool:
    """True if *needle* does NOT appear inside a fenced code block.

    Use this for anti-hallucination checks: it's OK to *mention* a tool in
    prose (e.g. "Do not use npm") but not to put it in a code block as if
    it were a real command for this repo.

    Set *word_boundary=True* to avoid substring false positives
    (e.g. "go test" matching inside "cargo test").
    """
    path = directory / relative
    if not path.is_file():
        return True
    content = path.read_text(encoding="utf-8", errors="replace")
    return not has_fenced_block_containing(content, needle, word_boundary=word_boundary)


_NEGATION_PREFIXES = [
    "do not", "don't", "don't", "not a ", "not an ", "never ",
    "avoid ", "this is not", "this isn't", "is not a", "isn't a",
    "no ", "missing ", "absent ",
]


def file_prescribes(directory: Path, relative: str, needle: str) -> bool:
    """True if *needle* appears on a line that is NOT a negation/warning.

    Returns False if the needle only appears in lines like
    "Do not add express" or "This is not a web server".
    """
    path = directory / relative
    if not path.is_file():
        return False
    content = path.read_text(encoding="utf-8", errors="replace")
    needle_lower = needle.lower()
    for line in content.splitlines():
        low = line.lower().strip()
        if needle_lower not in low:
            continue
        # Found the needle — check if the line is a negation
        if not any(neg in low for neg in _NEGATION_PREFIXES):
            return True  # positive/prescriptive usage
    return False  # only appeared in negations (or not at all)


# ---------------------------------------------------------------------------
# Check builder helpers
# ---------------------------------------------------------------------------

def hard(name: str, passed: bool, detail: str = "", *, channel: str = "general") -> CheckResult:
    return CheckResult(name, "pass" if passed else "fail", "hard", channel, detail)


def soft(name: str, passed: bool, detail: str = "", *, channel: str = "general") -> CheckResult:
    return CheckResult(name, "pass" if passed else "soft_fail", "soft", channel, detail)


def _contract_result(name: str, passed: bool, tier: str, *, channel: str = "contract") -> CheckResult:
    if tier == "soft":
        return soft(name, passed, channel=channel)
    return hard(name, passed, channel=channel)


# ---------------------------------------------------------------------------
# Contract-driven deterministic checks
# ---------------------------------------------------------------------------

def load_contract(contracts_dir: Path, scenario: str) -> dict | None:
    path = contracts_dir / f"{scenario}.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _find_instruction_file(directory: Path, names: list[str]) -> str | None:
    for name in names:
        if (directory / name).is_file():
            return name
    return None


def _line_has_status(text: str, label: str, value: str) -> bool:
    normalized_label = " ".join(label.replace("-", " ").split()).lower()
    normalized_value = " ".join(value.split()).lower()
    for raw_line in text.splitlines():
        line = raw_line.replace("*", "").strip().lower()
        if not line.startswith(f"{normalized_label}:"):
            continue
        actual_value = " ".join(line.split(":", 1)[1].split())
        if actual_value.startswith(normalized_value):
            return True
    return False


def run_contract_checks(
    output: str,
    generated_dir: Path,
    contract: dict,
    instruction_files: list[str] | None = None,
    fixture_dir: Path | None = None,
) -> list[CheckResult]:
    instruction_files = instruction_files or ["AGENTS.md"]
    results: list[CheckResult] = []
    inst = _find_instruction_file(generated_dir, instruction_files)

    for relative in contract.get("must_create_files", []):
        results.append(hard(
            f"Created {relative}",
            file_exists(generated_dir, relative),
            channel="contract",
        ))

    for relative in contract.get("must_not_modify_paths", []):
        original = fixture_dir / relative if fixture_dir else None
        generated = generated_dir / relative
        if original and original.exists():
            passed = generated.exists() and generated.read_text(encoding="utf-8", errors="replace") == original.read_text(
                encoding="utf-8", errors="replace"
            )
        else:
            passed = not generated.exists()
        results.append(hard(
            f"Did not modify {relative}",
            passed,
            channel="contract",
        ))

    for item in contract.get("required_commands", []):
        commands = item if isinstance(item, list) else [item]
        label = " | ".join(commands)
        passed = False
        if inst:
            passed = any(file_has_fenced_block_containing(generated_dir, inst, command) for command in commands)
        results.append(hard(
            f"Instruction file includes command: {label}",
            passed,
            channel="contract",
        ))

    for command in contract.get("forbidden_commands", []):
        passed = True
        if inst:
            passed = file_not_contains_command(generated_dir, inst, command, word_boundary=True)
        results.append(hard(
            f"Instruction file does not prescribe command: {command}",
            passed,
            channel="contract",
        ))

    for item in contract.get("required_command_scope_pairs", []):
        commands = item["command"] if isinstance(item["command"], list) else [item["command"]]
        scopes = item["scope"] if isinstance(item["scope"], list) else [item["scope"]]
        passed = False
        if inst:
            content = (generated_dir / inst).read_text(encoding="utf-8", errors="replace")
            if any(has_fenced_block_containing(content, command) for command in commands) and any(scope.lower() in content.lower() for scope in scopes):
                passed = True
        label = " | ".join(commands)
        scope_label = " | ".join(scopes)
        results.append(hard(
            f"Scoped command '{label}' with '{scope_label}'",
            passed,
            channel="contract",
        ))

    required_paths_tier = contract.get("required_paths_tier", "soft")
    for item in contract.get("required_paths", []):
        relatives = item if isinstance(item, list) else [item]
        label = " | ".join(relatives)
        path_ok = False
        if inst:
            path_ok = any(file_contains(generated_dir, inst, relative, case_sensitive=True) for relative in relatives)
        results.append(_contract_result(
            f"Referenced path: {label}",
            path_ok,
            required_paths_tier,
            channel="contract",
        ))

    required_path_roles_tier = contract.get("required_path_roles_tier", "soft")
    for item in contract.get("required_path_roles", []):
        relative = item["path"]
        roles = item["role"] if isinstance(item["role"], list) else [item["role"]]
        passed = False
        if inst:
            content = (generated_dir / inst).read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                if relative in line and any(role.lower() in line.lower() for role in roles):
                    passed = True
                    break
        role_label = " | ".join(roles)
        results.append(_contract_result(
            f"Explained role for {relative}: {role_label}",
            passed,
            required_path_roles_tier,
            channel="contract",
        ))

    for relative in contract.get("forbidden_paths", []):
        forbidden = False
        if inst:
            forbidden = file_prescribes(generated_dir, inst, relative)
        results.append(hard(
            f"Did not invent path: {relative}",
            not forbidden,
            channel="contract",
        ))

    for section in contract.get("required_sections", []):
        passed = False
        if inst:
            passed = file_contains(generated_dir, inst, section, case_sensitive=True)
        results.append(hard(
            f"Instruction file includes section: {section}",
            passed,
            channel="contract",
        ))

    for phrase in contract.get("required_phrases", []):
        passed = False
        if inst:
            passed = file_contains(generated_dir, inst, phrase)
        results.append(hard(
            f"Included required phrase: {phrase}",
            passed,
            channel="contract",
        ))

    for phrase in contract.get("forbidden_phrases", []):
        # Only check the generated instruction file, not the output.
        # The agent may legitimately mention forbidden phrases when flagging
        # them as anti-patterns (e.g. "removed 'follow best practices'").
        forbidden = False
        if inst:
            forbidden = file_contains(generated_dir, inst, phrase)
        results.append(hard(
            f"Did not use forbidden phrase: {phrase}",
            not forbidden,
            channel="contract",
        ))

    for phrase in contract.get("forbidden_prescriptions", []):
        forbidden = False
        if inst:
            forbidden = file_prescribes(generated_dir, inst, phrase)
        results.append(hard(
            f"Did not prescribe forbidden concept: {phrase}",
            not forbidden,
            channel="contract",
        ))

    verification_source = contract.get("expected_verification_source")
    if verification_source:
        passed = False
        if inst:
            passed = file_contains(generated_dir, inst, verification_source, case_sensitive=True)
        results.append(hard(
            f"Chose verification source: {verification_source}",
            passed,
            channel="contract",
        ))

    for source in contract.get("forbidden_verification_sources", []):
        forbidden = False
        if inst:
            forbidden = file_prescribes(generated_dir, inst, source)
        results.append(hard(
            f"Did not treat forbidden verification source as canonical: {source}",
            not forbidden,
            channel="contract",
        ))

    required_done_when_tier = contract.get("required_done_when_tier", "soft")
    for phrase in contract.get("required_done_when_phrases", []):
        passed = False
        if inst:
            content = (generated_dir / inst).read_text(encoding="utf-8", errors="replace")
            sections = re.split(r"(?im)^##\s+", content)
            done_sections = [
                s for s in sections
                if s.lower().startswith((
                    "done when", "done checklist", "verification checklist", "verification",
                    "done-when", "definition of done", "change checklist",
                ))
            ]
            passed = any(contains(section, phrase) for section in done_sections)
        results.append(_contract_result(
            f"Done checklist includes: {phrase}",
            passed,
            required_done_when_tier,
        ))

    return results
