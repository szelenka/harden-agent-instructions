#!/usr/bin/env python3

from __future__ import annotations

import json
import inspect
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "AGENTS.md"
SKILL_DIR = ROOT / "skills" / "harden-agent-instructions"
SKILL = SKILL_DIR / "SKILL.md"
README = ROOT / "README.md"
RUBRIC = SKILL_DIR / "references" / "RUBRIC.md"
GOLDEN = SKILL_DIR / "references" / "GOLDEN_TASKS.md"
FIXTURES = ROOT / "tests" / "fixtures"
CONTRACTS = ROOT / "tests" / "eval" / "contracts"


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, context: str) -> None:
    if needle not in text:
        fail(f"{context}: missing {needle!r}")


def assert_regex(text: str, pattern: str, context: str) -> None:
    if not re.search(pattern, text, re.MULTILINE):
        fail(f"{context}: pattern not found: {pattern}")


def assert_not_contains(text: str, needle: str, context: str) -> None:
    if needle in text:
        fail(f"{context}: should not contain {needle!r}")


def assert_in_order(text: str, needles: list[str], context: str) -> None:
    pos = -1
    for needle in needles:
        next_pos = text.find(needle, pos + 1)
        if next_pos == -1:
            fail(f"{context}: missing {needle!r}")
        if next_pos < pos:
            fail(f"{context}: {needle!r} out of order")
        pos = next_pos


def assert_any_contains(text: str, needles: list[str], context: str) -> None:
    if not any(needle in text for needle in needles):
        fail(f"{context}: missing any of {needles!r}")


def assert_markdown_links_resolve(text: str, doc_path: Path, context: str) -> None:
    for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text):
        if "://" in target or target.startswith("#"):
            continue
        resolved = (doc_path.parent / target).resolve()
        if not resolved.exists():
            fail(f"{context}: link target missing for {label!r}: {target!r}")


def assert_heading_once(text: str, heading: str, context: str) -> None:
    count = len(re.findall(rf"^{re.escape(heading)}$", text, re.MULTILINE))
    if count != 1:
        fail(f"{context}: expected {heading!r} exactly once; found {count}")


def count_actionable_lines(text: str) -> int:
    count = 0
    action_markers = (
        "if ",
        "do not ",
        "never ",
        "always ",
        "run ",
        "use ",
        "keep ",
        "list ",
        "score ",
        "render ",
        "return ",
        "load ",
        "verify ",
        "fix ",
        "cut ",
    )
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lowered = line.lower()
        if line.startswith("```") or line.startswith("|") or line.startswith("#"):
            count += 1
            continue
        if lowered.startswith(("- ", "* ", "1. ", "2. ", "3. ", "4. ", "5. ", "6. ", "7. ", "8. ", "9. ")):
            count += 1
            continue
        if any(marker in lowered for marker in action_markers):
            count += 1
    return count


def test_primary_skill_structure() -> None:
    text = read(SKILL)
    lines = text.splitlines()

    if len(lines) > 300:
        fail(f"SKILL.md should stay lean; found {len(lines)} lines")

    first_block = "\n".join(lines[:35])
    assert_contains(first_block, "## Hard Rules", "SKILL.md top-of-file salience")
    assert_any_contains(first_block, ["Verify repo facts", "repo facts"], "SKILL.md repo-facts salience")
    assert_any_contains(first_block, ["source of truth", "Instructions must match"], "SKILL.md source-of-truth salience")
    assert_any_contains(first_block, ["Fix cold-start blockers first", "cold-start blockers"], "SKILL.md cold-start salience")
    assert_any_contains(first_block, ["single-agent", "single agent"], "SKILL.md single-agent salience")
    assert_any_contains(first_block, ["persist it into the repo's instruction files", "persist it into the repo's instruction file"], "SKILL.md persistence salience")

    assert_in_order(
        text,
        [
            "## Hard Rules",
            "## When To Use",
            "## Operating Mode",
            "## Phase 1: Discovery",
            "## Phase 2: Assess",
            "## Phase 3: Fix",
            "## Phase 4: Verify",
            "## Load On Demand",
        ],
        "SKILL.md section order",
    )

    for needle in [
        "The response is incomplete if `### Rubric Scores (final)` is missing.",
        "### Rubric Scores (final)",
        "Criterion, Score, Evidence",
        "## Load On Demand",
        "references/RUBRIC.md",
        "references/GOLDEN_TASKS.md",
    ]:
        assert_contains(text, needle, "SKILL.md structure")
    assert_any_contains(
        text,
        ["Render scores as a compact table", "Use any clear Markdown-friendly table format"],
        "SKILL.md output contract",
    )
    assert_markdown_links_resolve(text, SKILL, "SKILL.md links")


def test_skill_heading_uniqueness_and_tables() -> None:
    text = read(SKILL)

    for heading in [
        "## Hard Rules",
        "## When To Use",
        "## Operating Mode",
        "## Quick Workflow",
        "## Phase 1: Discovery",
        "## Phase 2: Assess",
        "## Phase 3: Fix",
        "## Phase 4: Verify",
        "## Output Format",
        "## Load On Demand",
    ]:
        assert_heading_once(text, heading, "SKILL.md heading uniqueness")

    for needle in [
        "| Repo Size | Primary File Lines | Token Warning | Token Danger |",
        "| Behavior / content | Rubric Criterion | Placement | Small | Medium | Large | Very Large |",
    ]:
        assert_contains(text, needle, "SKILL.md table structure")
    assert_contains(text, "Fix Priority to Rubric Crosswalk", "SKILL.md crosswalk reference")
    for needle in [
        "root only",
        "root or reference",
        "reference preferred unless prohibitive",
        "reference only",
    ]:
        assert_contains(text, needle, "SKILL.md placement guidance")
    assert_contains(
        text,
        "When you add a decision gate, prefer this shape: trigger -> action -> escalation -> minimum deterministic verification",
        "SKILL.md decision-gate shape",
    )


def test_repo_instruction_surface_is_current() -> None:
    text = read(AGENTS)

    # Concept: AGENTS.md documents its own role in the key-files table
    assert_regex(text, r"AGENTS\.md.*[Rr]epo.*(maintenance|instruction)", "AGENTS.md self-documents role")
    # Concept: AGENTS.md has a permissions table with read-write access
    assert_regex(text, r"AGENTS\.md.*[Rr]ead-write", "AGENTS.md permissions table")
    # Concept: test gate — run_tests.py must pass
    assert_regex(text, r"tests/run_tests\.py.*must pass", "AGENTS.md test gate")
    # Concept: cross-doc reconciliation — SKILL/RUBRIC changes require README+AGENTS sync
    assert_regex(text, r"(README|AGENTS).*and.*(README|AGENTS).*before finishing", "AGENTS.md cross-doc sync on edit")
    assert_regex(text, r"SKILL\.md.*or.*RUBRIC\.md.*README.*AGENTS", "AGENTS.md reconcile on skill change")
    # Concept: fixture requirements
    assert_regex(text, r"fixture.*build manifest.*EXPECTED\.md", "AGENTS.md fixture requirements")
    # Concept: fixture boundary — never edit fixtures without permission
    assert_regex(text, r"[Nn][Ee][Vv][Ee][Rr] edit.*tests/fixtures.*explicit", "AGENTS.md fixture boundary")
    # Concept: persistence rule — discoveries go into AGENTS.md or references
    assert_regex(text, r"persist.*AGENTS\.md.*or.*references", "AGENTS.md persistence rule")
    # Concept: operational surface — agent rules stay in AGENTS.md / SKILL.md
    assert_regex(text, r"(operational|agent).*rules.*AGENTS\.md", "AGENTS.md operational-surface rule")


def test_skill_sparse_repo_fallbacks_and_scope_claims() -> None:
    skill = read(SKILL)
    readme = read(README)

    assert_contains(
        skill,
        "If CI, hooks, lock files, or task runners are absent, say so explicitly and downgrade confidence instead of inventing policy.",
        "SKILL.md sparse repo fallback guidance",
    )
    assert_regex(
        skill,
        r"If the repo has multiple manifests or task runners, list each candidate workflow",
        "SKILL.md multi-manifest fallback guidance",
    )
    assert_regex(
        skill,
        r"If no CI or hooks exist, do not invent CI-backed policy",
        "SKILL.md CI fallback guidance",
    )
    assert_regex(
        skill,
        r"If no task runner exists, list the discovered direct commands",
        "SKILL.md task-runner fallback guidance",
    )
    assert_regex(
        skill,
        r"If no tests exist, say that coverage is absent",
        "SKILL.md no-tests fallback guidance",
    )
    assert_regex(
        skill,
        r"If the repo shape is ambiguous, say which interpretations are plausible",
        "SKILL.md ambiguous-repo fallback guidance",
    )
    assert_contains(skill, "do not force software-app sections onto docs, infra, data, or prompt repos", "SKILL.md scope fallback guidance")

    assert_not_contains(readme, "Works with any repo regardless of language or build system.", "README scope claim")
    assert_contains(readme, "Turn agent instructions into repo-grounded working guidance.", "README positioning")
    assert_contains(readme, "exact paths, real commands, concrete verification steps, and nothing extra", "README repo-grounding claim")


def test_readme_heading_uniqueness_and_references() -> None:
    text = read(README)

    for heading in [
        "## What it does",
        "## Installation",
        "## Usage",
        "## Contributing",
        "## License",
    ]:
        assert_heading_once(text, heading, "README heading uniqueness")

    for needle in [
        "[INSTALL.md](INSTALL.md)",
        "[CONTRIBUTING.md](CONTRIBUTING.md)",
        "[AGENTS.md](AGENTS.md)",
        "[`references/GOLDEN_TASKS.md`](skills/harden-agent-instructions/references/GOLDEN_TASKS.md)",
    ]:
        assert_contains(text, needle, "README reference coverage")


def test_cross_document_concept_alignment() -> None:
    skill = read(SKILL)
    readme = read(README)
    agents = read(AGENTS)

    # Concept: line budget — AGENTS.md and SKILL.md agree on a line limit
    assert_regex(agents, r"SKILL\.md.*under \d+ lines", "cross-doc line budget in AGENTS")
    assert_regex(skill, r"[Dd]elete.*discoverable.*before adding", "cross-doc prune rule in SKILL")

    # Concept: README and skill both emphasize repo-grounded instructions
    assert_regex(readme, r"(anchored|grounded) to repo facts", "cross-doc grounding rule in README")

    # Concept: test gate mentioned in AGENTS
    assert_regex(agents, r"tests/run_tests\.py.*must pass", "cross-doc test gate in AGENTS")

    # Concept: fixture boundary in AGENTS
    assert_regex(agents, r"[Nn][Ee][Vv][Ee][Rr] edit.*tests/fixtures.*explicit", "cross-doc fixture boundary in AGENTS")

    # Concept: README describes the skill's concrete repo-grounding value
    assert_regex(readme, r"exact paths, real commands, concrete verification steps", "cross-doc repo value in README")


def test_readme_links_resolve() -> None:
    assert_markdown_links_resolve(read(README), README, "README links")


def test_install_instructions_are_repo_grounded() -> None:
    cursor_plugin = json.loads(read(ROOT / ".cursor-plugin" / "plugin.json"))
    agents = read(AGENTS)

    install_md = read(ROOT / "INSTALL.md")
    assert_contains(install_md, "Remote Rule (Github)", "Cursor documented install flow")
    assert_contains(install_md, "Agent Decides", "Cursor verification path")
    assert_contains(install_md, "https://code.claude.com/docs/en/skills", "Claude official docs link")
    assert_contains(install_md, "~/.claude/skills", "Claude documented user skill path")

    skills_path = (ROOT / ".cursor-plugin" / cursor_plugin["skills"]).resolve()
    if not skills_path.exists():
        fail(f"Cursor plugin skills path missing: {skills_path.relative_to(ROOT)}")
    if "commands" in cursor_plugin:
        commands_path = (ROOT / ".cursor-plugin" / cursor_plugin["commands"]).resolve()
        if not commands_path.exists():
            fail(f"Cursor plugin commands path missing: {commands_path.relative_to(ROOT)}")

    claude_skill = ROOT / ".claude" / "skills" / "harden-agent-instructions" / "SKILL.md"
    if not claude_skill.exists():
        fail(f"Claude skills path missing: {claude_skill.relative_to(ROOT)}")

    assert_contains(
        agents,
        "Install instructions and marketplace claims must be backed by checked-in manifests, canonical repo paths, or other repo-local evidence plus one verification step",
        "AGENTS.md install-surface convention",
    )


def test_skill_output_contract_shape() -> None:
    text = read(SKILL)
    for needle in [
        "## Audit Summary",
        "Cold-start ready: yes/no",
        "Instruction files: [list with line counts]",
        "Repo tier: small/medium/large/very large",
        "Enforcement sustainability: enforced / partially enforced / unenforced",
        "### Fixes Applied",
        "### Remaining Issues",
        "### Rubric Scores (final)",
    ]:
        assert_contains(text, needle, "SKILL.md output contract")


def test_skill_action_density() -> None:
    text = read(SKILL)
    lines = [line for line in text.splitlines() if line.strip()]
    actionable = count_actionable_lines(text)
    if actionable / len(lines) < 0.55:
        fail(f"SKILL.md action density too low: {actionable}/{len(lines)} actionable lines")


def test_required_section_criteria_exist_in_rubric_once() -> None:
    rubric = read(RUBRIC)

    criteria = [
        "Startup Reliability",
        "Structural Orientation",
        "Done-When Checklists",
        "Codebase Drift Prevention",
        "Review Burden Reduction",
        "Testing Conventions",
        "Failure Blast Radius Awareness",
        "Decision Boundary Precision",
        "Self-Improving Feedback Loop",
        "Scope Boundaries",
        "Source Control Workflow",
        "Context Budget Design",
        "Instruction Salience",
        "Codified Policy Enforcement",
    ]

    for criterion in criteria:
        count = rubric.count(f"**{criterion}**")
        if count != 1:
            fail(f"RUBRIC.md should define {criterion!r} exactly once; found {count}")


def test_reference_files_present() -> None:
    rubric = read(RUBRIC)
    golden = read(GOLDEN)

    for needle in [
        "**Instruction Salience**",
        "**Decision Boundary Precision**",
        "**Action-Outcome Coupling**",
        "**Review Burden Reduction**",
        "**Context Budget Design**",
        "**Golden Tasks**",
        "**Handoff Protocol**",
        "## Fix Priority to Rubric Crosswalk",
        "| Fix Priority | Primary Rubric Criteria |",
    ]:
        assert_contains(rubric, needle, "RUBRIC.md criteria coverage")

    for needle in [
        "## Golden Task 1: Improve A Weak Instruction File",
        "## Golden Task 2: Create Instructions From Scratch",
        "## Golden Task 4: Audit a Monorepo With Distinct Operational Zones",
        "## Negative Calibration: Delete These From Root AGENTS.md",
        "## Before / After Calibration",
        "## Parallel Discovery Pattern",
        "## Multi-Agent Handoff Checkpoint",
        "assign one owner per file set",
        "Rewrite broad advice into decision gates:",
        "Move explanatory rationale out of root `AGENTS.md`:",
    ]:
        assert_contains(golden, needle, "GOLDEN_TASKS.md coverage")


def test_eval_coverage_for_priority_scenarios() -> None:
    eval_readme = read(ROOT / "tests" / "eval" / "README.md")
    scenario_dir = ROOT / "tests" / "eval" / "scenarios"

    assert_contains(eval_readme, "| Tool | Models | Default |", "tests/eval/README.md tools table")
    assert_contains(eval_readme, "tests/eval/contracts/", "tests/eval/README.md contract coverage")
    assert_contains(eval_readme, "--self-test", "tests/eval/README.md self-test coverage")

    for name in [
        "weak-instructions",
        "solid-instructions",
        "workflow-first-repo",
        "hook-first-go-repo",
        "hook-first-go-template-seed",
        "pulumi-config-repo",
        "template-repo",
        "nested-ops-repo",
        "github-action-repo",
        "rust-service-with-policy",
        "rust-cli",
        "cpp-service",
    ]:
        scenario = scenario_dir / f"{name}.txt"
        if not scenario.exists():
            fail(f"missing eval scenario: {scenario.relative_to(ROOT)}")
        assert_contains(eval_readme, f"`{name}.txt`", "tests/eval/README.md scenario table")


def test_eval_contract_exists_for_every_scenario() -> None:
    scenario_dir = ROOT / "tests" / "eval" / "scenarios"
    for scenario in scenario_dir.glob("*.txt"):
        name = scenario.stem
        contract = CONTRACTS / f"{name}.json"
        if not contract.exists():
            fail(f"missing eval contract: {contract.relative_to(ROOT)}")

        data = json.loads(read(contract))
        for key in [
            "must_create_files",
            "must_not_modify_paths",
            "required_paths",
        ]:
            if key not in data:
                fail(f"{contract.relative_to(ROOT)}: missing {key}")


def test_eval_metadata_has_matching_fixtures() -> None:
    scenario_dir = ROOT / "tests" / "eval" / "scenarios"

    for scenario in scenario_dir.glob("*.txt"):
        name = scenario.stem
        fixture_dir = FIXTURES / name
        expected = fixture_dir / "EXPECTED.md"
        if not fixture_dir.exists():
            fail(f"eval metadata: missing fixture directory for {name}")
        if not expected.exists():
            fail(f"eval metadata: missing EXPECTED.md for {name}")


def test_fixture_scripts_match_expected() -> None:
    solid_package = json.loads(read(FIXTURES / "solid-instructions" / "package.json"))
    solid_scripts = set(solid_package.get("scripts", {}))
    solid_expected = {"build", "test", "lint", "format", "check", "migrate"}
    solid_missing = solid_expected - solid_scripts
    if solid_missing:
        fail(f"solid-instructions: missing package.json scripts: {sorted(solid_missing)}")

    weak_gomod = read(FIXTURES / "weak-instructions" / "go.mod")
    for needle in [
        "module github.com/example/user-service",
        "go 1.22",
    ]:
        assert_contains(weak_gomod, needle, "weak-instructions manifest coverage")

    weak_makefile = read(FIXTURES / "weak-instructions" / "Makefile")
    for needle in [
        ".PHONY: fmt lint build test run migrate",
        "golangci-lint run ./...",
        "go build -o bin/server ./cmd/server",
        "go test ./...",
    ]:
        assert_contains(weak_makefile, needle, "weak-instructions manifest coverage")

    go_makefile = read(FIXTURES / "go-service" / "Makefile")
    for needle in [
        ".PHONY: format lint build test",
        "gofmt -w ./cmd ./internal",
        "golangci-lint run ./...",
        "go build ./cmd/...",
        "go test ./...",
    ]:
        assert_contains(go_makefile, needle, "go-service manifest coverage")

    infra_makefile = read(FIXTURES / "infra-config" / "Makefile")
    for needle in [
        "helm lint charts/ml-proxy",
        "helm template ml-proxy charts/ml-proxy -f environments/dev/values.yaml",
        "helmfile -e dev diff",
    ]:
        assert_contains(infra_makefile, needle, "infra-config manifest coverage")

    mixed_makefile = read(FIXTURES / "makefile-only-mixed" / "Makefile")
    for needle in [
        ".PHONY: lint render smoke-test",
        "./scripts/lint.sh",
        "./scripts/render.sh > build/output.txt",
        "./scripts/smoke_test.sh",
    ]:
        assert_contains(mixed_makefile, needle, "makefile-only-mixed manifest coverage")

    nested_root_makefile = read(FIXTURES / "nested-ops-repo" / "Makefile")
    for needle in [
        "$(MAKE) -C services/ml-proxy lint",
        "$(MAKE) -C services/ml-proxy render",
        "$(MAKE) -C services/wordcloud diff",
    ]:
        assert_contains(nested_root_makefile, needle, "nested-ops-repo root manifest coverage")

    nested_service_makefile = read(FIXTURES / "nested-ops-repo" / "services" / "ml-proxy" / "Makefile")
    for needle in [
        "helm lint ../../charts/ml-proxy",
        "helm template ml-proxy ../../charts/ml-proxy -f ../../clusters/dev/values.yaml",
    ]:
        assert_contains(nested_service_makefile, needle, "nested-ops-repo service manifest coverage")

    rust_policy_manifest = read(FIXTURES / "rust-service-with-policy" / "Cargo.toml")
    for needle in [
        "[package]",
        'name = "rust-service-with-policy"',
        "[lints.clippy]",
        'unwrap_used = "deny"',
        'todo = "deny"',
    ]:
        assert_contains(rust_policy_manifest, needle, "rust-service-with-policy manifest coverage")
    rustfmt = read(FIXTURES / "rust-service-with-policy" / "rustfmt.toml")
    for needle in [
        "max_width = 100",
        'newline_style = "Unix"',
    ]:
        assert_contains(rustfmt, needle, "rust-service-with-policy rustfmt coverage")

    action_package = json.loads(read(FIXTURES / "github-action-repo" / "package.json"))
    for script_name in ["build", "lint", "test"]:
        if script_name not in action_package.get("scripts", {}):
            fail(f"github-action-repo: missing package.json script {script_name!r}")
    assert_contains(read(FIXTURES / "github-action-repo" / "action.yml"), "main: dist/index.js", "github-action-repo action contract")

    pulumi_yaml = read(FIXTURES / "pulumi-config-repo" / "Pulumi.yaml")
    for needle in [
        "name: pulumi-config-repo",
        "runtime: nodejs",
    ]:
        assert_contains(pulumi_yaml, needle, "pulumi-config-repo root contract")
    pulumi_package = json.loads(read(FIXTURES / "pulumi-config-repo" / "config" / "package.json"))
    for script_name in ["preview", "deploy", "lint"]:
        if script_name not in pulumi_package.get("scripts", {}):
            fail(f"pulumi-config-repo: missing config/package.json script {script_name!r}")

    dockerfile_sparse = read(FIXTURES / "dockerfile-sparse-repo" / "Dockerfile")
    for needle in [
        "FROM alpine:3.20",
        "COPY scripts/entrypoint.sh /entrypoint.sh",
        'ENTRYPOINT ["/entrypoint.sh"]',
    ]:
        assert_contains(dockerfile_sparse, needle, "dockerfile-sparse-repo manifest coverage")

    template_makefile = read(FIXTURES / "template-repo" / "Makefile")
    assert_contains(template_makefile, "cookiecutter template --no-input", "template-repo render workflow")
    assert_contains(read(FIXTURES / "template-repo" / "cookiecutter.json"), '"project_slug": "demo-service"', "template-repo template inputs")

    cpp_cmake = read(FIXTURES / "cpp-service" / "CMakeLists.txt")
    for needle in [
        "cmake_minimum_required",
        "project(cpp-service",
        "set(CMAKE_CXX_STANDARD 20)",
        "add_test(NAME unit_tests",
    ]:
        assert_contains(cpp_cmake, needle, "cpp-service manifest coverage")

    cpp_makefile = read(FIXTURES / "cpp-service" / "Makefile")
    for needle in [
        ".PHONY: configure build test lint clean",
        "cmake -B build",
        "cmake --build build",
        "ctest --test-dir build",
        "clang-tidy src/*.cpp",
    ]:
        assert_contains(cpp_makefile, needle, "cpp-service manifest coverage")

    rust_cargo = read(FIXTURES / "rust-cli" / "Cargo.toml")
    for needle in [
        "[package]",
        'name = "rust-cli"',
        "[dependencies]",
        "clap =",
    ]:
        assert_contains(rust_cargo, needle, "rust-cli manifest coverage")

    rust_makefile = read(FIXTURES / "rust-cli" / "Makefile")
    for needle in [
        ".PHONY: fmt check lint build test",
        "cargo clippy -- -D warnings",
        "cargo build --release",
        "cargo test",
    ]:
        assert_contains(rust_makefile, needle, "rust-cli manifest coverage")

    # --- poetry-service ---
    poetry_pyproject = read(FIXTURES / "poetry-service" / "pyproject.toml")
    for needle in [
        "[tool.poetry]",
        'name = "poetry-service"',
        "poetry-core",
        "[tool.pytest.ini_options]",
        "[tool.ruff]",
        "[tool.mypy]",
    ]:
        assert_contains(poetry_pyproject, needle, "poetry-service manifest coverage")
    poetry_lock = read(FIXTURES / "poetry-service" / "poetry.lock")
    assert_contains(poetry_lock, "automatically @generated by Poetry", "poetry-service lockfile")
    poetry_makefile = read(FIXTURES / "poetry-service" / "Makefile")
    for needle in [
        "poetry run pytest",
        "poetry run ruff check",
        "poetry run mypy app/",
    ]:
        assert_contains(poetry_makefile, needle, "poetry-service Makefile coverage")

    # --- terraform-infra ---
    tf_main = read(FIXTURES / "terraform-infra" / "main.tf")
    for needle in [
        "terraform {",
        "required_version",
        'backend "s3"',
        'provider "aws"',
    ]:
        assert_contains(tf_main, needle, "terraform-infra manifest coverage")

    # --- meson-lib ---
    meson_build = read(FIXTURES / "meson-lib" / "meson.build")
    for needle in [
        "project('meson-lib', 'c'",
        "library('mathutil'",
        "test('unit_tests'",
    ]:
        assert_contains(meson_build, needle, "meson-lib manifest coverage")

    # --- tox-django ---
    tox_ini = read(FIXTURES / "tox-django" / "tox.ini")
    for needle in [
        "[tox]",
        "env_list = py312, lint, typecheck",
        "commands = pytest {posargs}",
        "commands = ruff check src/ tests/",
        "commands = mypy src/",
    ]:
        assert_contains(tox_ini, needle, "tox-django manifest coverage")
    tox_pyproject = read(FIXTURES / "tox-django" / "pyproject.toml")
    assert_contains(tox_pyproject, 'name = "tox-django"', "tox-django pyproject coverage")

    workflow_ci = read(FIXTURES / "workflow-first-repo" / ".github" / "workflows" / "ci.yml")
    for needle in [
        "python -m pytest",
        "ruff check .",
        "actions/setup-python@v5",
    ]:
        assert_contains(workflow_ci, needle, "workflow-first-repo CI coverage")

    hook_go_config = read(FIXTURES / "hook-first-go-repo" / ".pre-commit-config.yaml")
    for needle in [
        "entry: go test ./...",
        "entry: go vet ./...",
        "language: system",
    ]:
        assert_contains(hook_go_config, needle, "hook-first-go-repo hook coverage")


def test_expected_docs_track_fixture_intent() -> None:
    go_service = read(FIXTURES / "go-service" / "EXPECTED.md")
    infra_config = read(FIXTURES / "infra-config" / "EXPECTED.md")
    makefile_only_mixed = read(FIXTURES / "makefile-only-mixed" / "EXPECTED.md")
    nested_ops_repo = read(FIXTURES / "nested-ops-repo" / "EXPECTED.md")
    rust_policy = read(FIXTURES / "rust-service-with-policy" / "EXPECTED.md")
    github_action = read(FIXTURES / "github-action-repo" / "EXPECTED.md")
    hook_first_go = read(FIXTURES / "hook-first-go-repo" / "EXPECTED.md")
    hook_first_go_seed = read(FIXTURES / "hook-first-go-template-seed" / "EXPECTED.md")
    pulumi_config = read(FIXTURES / "pulumi-config-repo" / "EXPECTED.md")
    sparse_git_repo = read(FIXTURES / "sparse-git-repo" / "EXPECTED.md")
    dockerfile_sparse = read(FIXTURES / "dockerfile-sparse-repo" / "EXPECTED.md")
    template_repo = read(FIXTURES / "template-repo" / "EXPECTED.md")
    workflow_first = read(FIXTURES / "workflow-first-repo" / "EXPECTED.md")
    weak = read(FIXTURES / "weak-instructions" / "EXPECTED.md")
    solid = read(FIXTURES / "solid-instructions" / "EXPECTED.md")

    for needle in [
        "A small Go service repo with no instruction files",
        "Verification commands:** `make lint`, `make build`, `make test`",
        "must prefer `make` and `go test`",
    ]:
        assert_contains(go_service, needle, "go-service EXPECTED.md")

    for needle in [
        "A small infra/config repo with no instruction files",
        "Verification commands:** `make lint`, `make render`, `make diff`",
        "must NOT force unit-test guidance, `src/` assumptions, or application-layer architecture",
    ]:
        assert_contains(infra_config, needle, "infra-config EXPECTED.md")

    for needle in [
        "A small repo with a root `Makefile` but no language-specific manifest.",
        "Verification commands:** `make lint`, `make render`, `make smoke-test`",
        "must not guess the repo language from the Makefile alone",
    ]:
        assert_contains(makefile_only_mixed, needle, "makefile-only-mixed EXPECTED.md")

    for needle in [
        "A small operations repo with a root `Makefile` and multiple nested service directories",
        "Verification reality:** split across subdirectories",
        "must enumerate root and nested workflows",
    ]:
        assert_contains(nested_ops_repo, needle, "nested-ops-repo EXPECTED.md")

    for needle in [
        "A small git-backed repo with no instruction files and no trustworthy build manifest.",
        "Build system:** absent or unverified",
        "must NOT invent npm, Python, Go, CI, or contributor workflow commands",
    ]:
        assert_contains(sparse_git_repo, needle, "sparse-git-repo EXPECTED.md")

    for needle in [
        "A small Rust service repo with no instruction files, a `Cargo.toml`, and explicit fmt/lint/test policy surfaces.",
        "Verification commands:** `cargo test`, `cargo fmt --check`, `cargo clippy -- -D warnings`",
        "should not treat this like the sparse git fixture or the shallow Rust command-family fixture",
    ]:
        assert_contains(rust_policy, needle, "rust-service-with-policy EXPECTED.md")

    for needle in [
        "A small GitHub Action repo with `action.yml`, `package.json`, and no instruction file.",
        "Build system:** `package.json` plus `action.yml`",
        "must recognize `action.yml` as the primary runtime contract",
    ]:
        assert_contains(github_action, needle, "github-action-repo EXPECTED.md")

    for needle in [
        "A small Pulumi-style infra repo with root config files and the primary Node manifest nested under `config/`.",
        "Build system:** `Pulumi.yaml` plus nested `config/package.json`",
        "must recognize nested manifests and working-directory-sensitive commands",
    ]:
        assert_contains(pulumi_config, needle, "pulumi-config-repo EXPECTED.md")

    for needle in [
        "A small repo whose strongest concrete signal is a `Dockerfile`",
        "Build system:** Dockerfile-led and otherwise sparse",
        "must not invent npm, Python, Go, Maven, or CI workflows",
    ]:
        assert_contains(dockerfile_sparse, needle, "dockerfile-sparse-repo EXPECTED.md")

    for needle in [
        "A small template repo with placeholder paths and no instruction file.",
        "Build system:** template-oriented workflow via root `Makefile`",
        "must not treat `{{project_slug}}` paths as already materialized repo code",
    ]:
        assert_contains(template_repo, needle, "template-repo EXPECTED.md")

    for needle in [
        "A small repo where `.github/workflows/ci.yml` is the strongest operational truth",
        "Build system:** workflow-first",
        "must prioritize the workflow file over weaker or absent local manifests",
    ]:
        assert_contains(workflow_first, needle, "workflow-first-repo EXPECTED.md")

    cpp_service = read(FIXTURES / "cpp-service" / "EXPECTED.md")
    for needle in [
        "A small C++ service repo with no instruction files",
        "Build system:** `CMakeLists.txt` plus root `Makefile`",
        "must prefer `cmake`, `ctest`, and `make`",
    ]:
        assert_contains(cpp_service, needle, "cpp-service EXPECTED.md")

    rust_cli = read(FIXTURES / "rust-cli" / "EXPECTED.md")
    for needle in [
        "A small Rust CLI repo with no instruction files",
        "Build system:** `Cargo.toml` plus root `Makefile`",
        "must prefer `cargo` and `make`",
    ]:
        assert_contains(rust_cli, needle, "rust-cli EXPECTED.md")

    for needle in [
        "A small Go repo where `.pre-commit-config.yaml` is the strongest operational truth",
        "Verification commands:** `go test ./...`, `go vet ./...`",
        "must prioritize the hook config over absent CI or guessed task runners",
    ]:
        assert_contains(hook_first_go, needle, "hook-first-go-repo EXPECTED.md")

    for needle in [
        "A small repo where a generic Go-template `AGENTS.md` exists",
        "Verification commands:** `go test ./...`, `go vet ./...`",
        "must override the generic Go template when hook-backed evidence is stronger",
    ]:
        assert_contains(hook_first_go_seed, needle, "hook-first-go-template-seed EXPECTED.md")

    poetry_service = read(FIXTURES / "poetry-service" / "EXPECTED.md")
    for needle in [
        "A Python Flask service managed by Poetry",
        "Build system:** Poetry",
        "must identify both layers",
    ]:
        assert_contains(poetry_service, needle, "poetry-service EXPECTED.md")

    terraform_infra = read(FIXTURES / "terraform-infra" / "EXPECTED.md")
    for needle in [
        "A Terraform infrastructure repo",
        "Build system:** Terraform",
        "must use `terraform` commands, NOT `make`, `npm`",
    ]:
        assert_contains(terraform_infra, needle, "terraform-infra EXPECTED.md")

    meson_lib = read(FIXTURES / "meson-lib" / "EXPECTED.md")
    for needle in [
        "A C library using the Meson build system",
        "Build system:** Meson",
        "must use `meson` commands, NOT `cmake`",
    ]:
        assert_contains(meson_lib, needle, "meson-lib EXPECTED.md")

    tox_django = read(FIXTURES / "tox-django" / "EXPECTED.md")
    for needle in [
        "A Django project with `tox.ini`",
        "Build system:** tox",
        "must use `tox` as the canonical test runner",
    ]:
        assert_contains(tox_django, needle, "tox-django EXPECTED.md")

    for needle in [
        "A Go user service with Chi and PostgreSQL.",
        "Build commands NOT in code blocks",
        "Fewer than 3 concrete file paths",
        "Orphaned commands:",
        "Deliberate Stale Reference",
        "\"Follow best practices\"",
    ]:
        assert_contains(weak, needle, "weak-instructions EXPECTED.md")

    for needle in [
        "**Cold-start ready:** yes",
        "Instruction Salience | Pass",
        "Done-When Checklists | Pass",
        "Could add scope boundaries",
    ]:
        assert_contains(solid, needle, "solid-instructions EXPECTED.md")


def test_new_fixture_file_shapes_exist() -> None:
    expected_paths = [
        FIXTURES / "weak-instructions" / "go.mod",
        FIXTURES / "weak-instructions" / "Makefile",
        FIXTURES / "weak-instructions" / "cmd" / "server" / "main.go",
        FIXTURES / "weak-instructions" / "internal" / "routes" / "users.go",
        FIXTURES / "weak-instructions" / "internal" / "services" / "user_service.go",
        FIXTURES / "cpp-service" / "CMakeLists.txt",
        FIXTURES / "cpp-service" / "Makefile",
        FIXTURES / "cpp-service" / "src" / "main.cpp",
        FIXTURES / "cpp-service" / "src" / "handler.cpp",
        FIXTURES / "cpp-service" / "include" / "handler.h",
        FIXTURES / "cpp-service" / "tests" / "handler_test.cpp",
        FIXTURES / "go-service" / "cmd" / "api" / "main.go",
        FIXTURES / "go-service" / "internal" / "server" / "server.go",
        FIXTURES / "infra-config" / "helmfile.yaml",
        FIXTURES / "infra-config" / "charts" / "ml-proxy" / "Chart.yaml",
        FIXTURES / "makefile-only-mixed" / "templates" / "service.conf.tmpl",
        FIXTURES / "nested-ops-repo" / "services" / "ml-proxy" / "Makefile",
        FIXTURES / "nested-ops-repo" / "services" / "wordcloud" / "Makefile",
        FIXTURES / "rust-service-with-policy" / "Cargo.toml",
        FIXTURES / "rust-service-with-policy" / "rustfmt.toml",
        FIXTURES / "rust-service-with-policy" / "src" / "main.rs",
        FIXTURES / "rust-service-with-policy" / "src" / "policy.rs",
        FIXTURES / "rust-service-with-policy" / "tests" / "cli_test.rs",
        FIXTURES / "sparse-git-repo" / "docs" / "architecture.md",
        FIXTURES / "sparse-git-repo" / "config" / "environments" / "dev.yaml",
        FIXTURES / "github-action-repo" / "action.yml",
        FIXTURES / "pulumi-config-repo" / "config" / "tools" / "preview.ts",
        FIXTURES / "dockerfile-sparse-repo" / "Dockerfile",
        FIXTURES / "template-repo" / "template" / "{{project_slug}}" / "README.md",
        FIXTURES / "rust-cli" / "Cargo.toml",
        FIXTURES / "rust-cli" / "src" / "main.rs",
        FIXTURES / "rust-cli" / "src" / "config.rs",
        FIXTURES / "rust-cli" / "tests" / "cli_test.rs",
        FIXTURES / "workflow-first-repo" / ".github" / "workflows" / "ci.yml",
        FIXTURES / "hook-first-go-repo" / ".pre-commit-config.yaml",
        FIXTURES / "hook-first-go-repo" / "service" / "handler.go",
        FIXTURES / "hook-first-go-repo" / "service" / "handler_test.go",
        FIXTURES / "hook-first-go-template-seed" / ".pre-commit-config.yaml",
        FIXTURES / "hook-first-go-template-seed" / "go.mod",
        FIXTURES / "hook-first-go-template-seed" / "service" / "handler.go",
        FIXTURES / "hook-first-go-template-seed" / "service" / "handler_test.go",
        FIXTURES / "poetry-service" / "Makefile",
        FIXTURES / "poetry-service" / "pyproject.toml",
        FIXTURES / "poetry-service" / "poetry.lock",
        FIXTURES / "poetry-service" / "app" / "main.py",
        FIXTURES / "poetry-service" / "tests" / "test_main.py",
        FIXTURES / "terraform-infra" / "main.tf",
        FIXTURES / "terraform-infra" / "variables.tf",
        FIXTURES / "terraform-infra" / "modules" / "vpc" / "main.tf",
        FIXTURES / "terraform-infra" / "modules" / "ecs" / "main.tf",
        FIXTURES / "terraform-infra" / "environments" / "dev.tfvars",
        FIXTURES / "meson-lib" / "meson.build",
        FIXTURES / "meson-lib" / "include" / "mathutil.h",
        FIXTURES / "meson-lib" / "src" / "mathutil.c",
        FIXTURES / "meson-lib" / "tests" / "test_mathutil.c",
        FIXTURES / "tox-django" / "tox.ini",
        FIXTURES / "tox-django" / "pyproject.toml",
        FIXTURES / "tox-django" / "src" / "todos" / "models.py",
        FIXTURES / "tox-django" / "src" / "todos" / "views.py",
        FIXTURES / "tox-django" / "tests" / "test_views.py",
    ]

    for path in expected_paths:
        if not path.exists():
            fail(f"fixture file missing: {path.relative_to(ROOT)}")


def test_zone_fixture_structure() -> None:
    # --- polyglot-monorepo-zones (positive: should trigger zone split) ---
    zones_fixture = FIXTURES / "polyglot-monorepo-zones"
    zones_expected_paths = [
        zones_fixture / "AGENTS.md",
        zones_fixture / "EXPECTED.md",
        zones_fixture / ".github" / "workflows" / "ci.yml",
        zones_fixture / "services" / "billing" / "pyproject.toml",
        zones_fixture / "services" / "billing" / "poetry.lock",
        zones_fixture / "services" / "billing" / "app" / "main.py",
        zones_fixture / "services" / "billing" / "tests" / "test_main.py",
        zones_fixture / "services" / "gateway" / "go.mod",
        zones_fixture / "services" / "gateway" / "go.sum",
        zones_fixture / "services" / "gateway" / "main.go",
        zones_fixture / "services" / "gateway" / "main_test.go",
        zones_fixture / "infra" / "main.tf",
        zones_fixture / "infra" / "terraform.lock.hcl",
    ]
    for path in zones_expected_paths:
        if not path.exists():
            fail(f"polyglot-monorepo-zones fixture file missing: {path.relative_to(ROOT)}")

    zones_expected = read(zones_fixture / "EXPECTED.md")
    for needle in [
        "Zones detected:** 3",
        "services/billing/",
        "services/gateway/",
        "infra/",
        "split is recommended",
        "Zone files do NOT restate root",
    ]:
        assert_contains(zones_expected, needle, "polyglot-monorepo-zones EXPECTED.md")

    zones_ci = read(zones_fixture / ".github" / "workflows" / "ci.yml")
    for needle in [
        "working-directory: services/billing",
        "working-directory: services/gateway",
        "working-directory: infra",
    ]:
        assert_contains(zones_ci, needle, "polyglot-monorepo-zones CI per-zone jobs")

    # --- gradle-multimodule (negative: should NOT trigger zone split) ---
    gradle_fixture = FIXTURES / "gradle-multimodule"
    gradle_expected_paths = [
        gradle_fixture / "AGENTS.md",
        gradle_fixture / "EXPECTED.md",
        gradle_fixture / "build.gradle.kts",
        gradle_fixture / "settings.gradle.kts",
        gradle_fixture / "gradlew",
        gradle_fixture / ".github" / "workflows" / "ci.yml",
        gradle_fixture / "app" / "build.gradle.kts",
        gradle_fixture / "app" / "src" / "main" / "java" / "com" / "example" / "app" / "App.java",
        gradle_fixture / "core" / "build.gradle.kts",
        gradle_fixture / "core" / "src" / "main" / "java" / "com" / "example" / "core" / "Core.java",
        gradle_fixture / "api" / "build.gradle.kts",
        gradle_fixture / "api" / "src" / "main" / "java" / "com" / "example" / "api" / "Api.java",
    ]
    for path in gradle_expected_paths:
        if not path.exists():
            fail(f"gradle-multimodule fixture file missing: {path.relative_to(ROOT)}")

    gradle_expected = read(gradle_fixture / "EXPECTED.md")
    for needle in [
        "Zones detected:** 0",
        "single root file",
        "No zone-specific",
        "not a signal",
    ]:
        assert_contains(gradle_expected, needle, "gradle-multimodule EXPECTED.md")

    gradle_ci = read(gradle_fixture / ".github" / "workflows" / "ci.yml")
    assert_contains(gradle_ci, "./gradlew build", "gradle-multimodule single CI job")
    assert_not_contains(gradle_ci, "working-directory:", "gradle-multimodule no per-zone CI")


def test_zone_regression_assertions_in_existing_fixtures() -> None:
    nested = read(FIXTURES / "nested-ops-repo" / "EXPECTED.md")
    assert_contains(nested, "Zone Regression Assertion", "nested-ops-repo zone regression section")
    assert_contains(nested, "Zones detected:** 0", "nested-ops-repo zero zones")


def test_fixture_instruction_quality_examples() -> None:
    weak = read(FIXTURES / "weak-instructions" / "AGENTS.md")
    solid = read(FIXTURES / "solid-instructions" / "AGENTS.md")

    if "```" in weak:
        fail("weak-instructions AGENTS.md should remain a bad example without code fences")

    assert_regex(weak, r"Follow best practices", "weak fixture anti-pattern")
    assert_regex(weak, r"run the linter", "weak fixture anti-pattern")

    assert_contains(solid, "**HARD RULES", "solid fixture salience")
    assert_regex(solid, r"```bash[\s\S]*npm run check", "solid fixture command block")
    for needle in [
        "`src/routes/`",
        "`src/services/`",
        "`src/validators/`",
        "Verification (Done Checklist)",
    ]:
        assert_contains(solid, needle, "solid fixture strength")


def collect_tests() -> list[tuple[str, object]]:
    tests: list[tuple[str, object]] = []
    for name, value in globals().items():
        if not name.startswith("test_"):
            continue
        if not inspect.isfunction(value):
            continue
        if value.__module__ != __name__:
            continue
        tests.append((name, value))
    tests.sort(key=lambda item: item[0])
    return tests


def main() -> int:
    tests = collect_tests()
    failures: list[str] = []
    for test_name, test_fn in tests:
        try:
            test_fn()
        except AssertionError as exc:
            failures.append(f"{test_name}: {exc}")
        except Exception as exc:
            failures.append(f"{test_name}: unexpected {type(exc).__name__}: {exc}")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"PASS ({len(tests)} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
