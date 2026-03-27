#!/usr/bin/env python3
"""Automated eval runner for the harden-agent-instructions skill.

Invokes `claude -p` or `codex exec` per scenario/model, runs mechanical checks
against the output and generated files, optionally runs an LLM judge, and
writes results.

Supported tools:
  claude  — uses `claude -p --model <id> --append-system-prompt <skill>`
  codex   — uses `codex exec -m <id> --full-auto -C <dir>`

Usage:
    python3 tests/eval/run_eval.py                                    # all scenarios, default tool+model
    python3 tests/eval/run_eval.py --tool codex --model o3            # codex with o3
    python3 tests/eval/run_eval.py --tool claude --model haiku sonnet # claude with multiple models
    python3 tests/eval/run_eval.py --scenario rust-cli
    python3 tests/eval/run_eval.py --skip-judge
    python3 tests/eval/run_eval.py --resume 2026-03-21T14-30-00
    python3 tests/eval/run_eval.py --variance 3                       # run each combo 3x, report divergence
    python3 tests/eval/run_eval.py --smoke --variance 5               # smoke subset (5 scenarios) x5, compare to baseline
    python3 tests/eval/run_eval.py --variance 5 --update-baseline     # run and save results as new baseline
    python3 tests/eval/run_eval.py --self-test rust-cli                # replay latest archived run, no CLI needed
    python3 tests/eval/run_eval.py --list
"""

from __future__ import annotations

import argparse
import concurrent.futures
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_DIR = ROOT / "tests" / "eval"
SCENARIOS_DIR = EVAL_DIR / "scenarios"
CONTRACTS_DIR = EVAL_DIR / "contracts"
FIXTURES_DIR = ROOT / "tests" / "fixtures"
RUNS_DIR = EVAL_DIR / "runs"
SKILL_FILE = ROOT / "skills" / "harden-agent-instructions" / "SKILL.md"
JUDGE_PROMPT_FILE = EVAL_DIR / "judge_prompt.txt"
BASELINE_FILE = EVAL_DIR / "baseline.json"

# Representative subset for quick regression checks after SKILL.md edits.
# Covers: weak-file repair, workflow-first source-of-truth selection,
# template hardening, nested workflow routing, and template/runtime separation.
SMOKE_SCENARIOS = [
    "weak-instructions",
    "workflow-first-repo",
    "hook-first-go-template-seed",
    "pulumi-config-repo",
    "template-repo",
]

TOOL_MODELS = {
    "claude": {
        "haiku": "haiku",
        "sonnet": "sonnet",
        "opus": "opus",
    },
    "codex": {
        "gpt-5.4": "gpt-5.4",
        "gpt-5.4-mini": "gpt-5.4-mini",
        "gpt-5.3-codex": "gpt-5.3-codex",
        "gpt-5.3-codex-spark-preview": "gpt-5.3-codex-spark-preview",
        "gpt-5.2-codex": "gpt-5.2-codex",
        "gpt-5.2": "gpt-5.2",
        "gpt-5.1-codex-max": "gpt-5.1-codex-max",
        "gpt-5.1-codex-mini": "gpt-5.1-codex-mini",
    },
}

TOOL_DEFAULTS = {
    "claude": "sonnet",
    "codex": "gpt-5.4",
}

DEFAULT_TOOL = "claude"
DEFAULT_TIMEOUT = 300

INSTRUCTION_FILES = ["AGENTS.md"]


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def available_scenarios() -> list[str]:
    return sorted(p.stem for p in SCENARIOS_DIR.glob("*.txt"))


def scenario_fixture_name(scenario: str) -> str:
    """Map scenario name to fixture directory name (same by convention)."""
    return scenario


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

def preflight(tool: str) -> list[str]:
    """Return a list of problems. Empty means all good."""
    problems = []
    if shutil.which(tool) is None:
        problems.append(f"'{tool}' CLI not found on $PATH")
    if not SKILL_FILE.is_file():
        problems.append(f"SKILL.md not found at {SKILL_FILE}")
    if not SCENARIOS_DIR.is_dir():
        problems.append(f"Scenarios directory missing: {SCENARIOS_DIR}")
    return problems


# ---------------------------------------------------------------------------
# Fixture isolation
# ---------------------------------------------------------------------------

def copy_fixture(scenario: str, dest: Path) -> Path:
    """Copy fixture to dest and return the path."""
    fixture_name = scenario_fixture_name(scenario)
    src = FIXTURES_DIR / fixture_name
    if not src.is_dir():
        raise FileNotFoundError(f"Fixture not found: {src}")
    target = dest / fixture_name
    shutil.copytree(src, target, symlinks=True)
    return target


# ---------------------------------------------------------------------------
# Agent invocation
# ---------------------------------------------------------------------------

def _build_claude_cmd(model_id: str, skill_text: str) -> list[str]:
    return [
        "claude", "-p",
        "--model", model_id,
        "--allowedTools", "Read,Write,Edit,Glob,Grep,Bash(python3:*),Bash(wc:*),Bash(find:*),Bash(ls:*),Bash(cat:*),Bash(head:*)",
        "--append-system-prompt", skill_text,
    ]


def _build_codex_cmd(model_id: str, fixture_path: Path) -> list[str]:
    return [
        "codex", "exec",
        "-m", model_id,
        "--full-auto",
        "--skip-git-repo-check",
        "-C", str(fixture_path),
    ]


def _prepend_skill_to_prompt(prompt: str) -> str:
    """For tools that don't support --append-system-prompt, prepend the skill."""
    skill_text = SKILL_FILE.read_text(encoding="utf-8")
    return (
        "Use the following skill instructions for this task:\n\n"
        "<skill>\n" + skill_text + "\n</skill>\n\n"
        + prompt
    )


def run_agent(
    tool: str, prompt: str, model_id: str, fixture_path: Path, timeout: int,
) -> tuple[str, float, int]:
    """Invoke the agent CLI and return (stdout, elapsed_seconds, returncode)."""
    skill_text = SKILL_FILE.read_text(encoding="utf-8")

    if tool == "claude":
        cmd = _build_claude_cmd(model_id, skill_text)
        stdin_text = prompt
    elif tool == "codex":
        cmd = _build_codex_cmd(model_id, fixture_path)
        stdin_text = _prepend_skill_to_prompt(prompt)
    else:
        return f"Unknown tool: {tool}", 0.0, -2

    start = time.monotonic()
    try:
        result = subprocess.run(
            cmd,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        elapsed = time.monotonic() - start
        output = result.stdout
        if result.returncode != 0 and not output:
            output = result.stderr or f"{tool} exited {result.returncode} with no output"
        return output, elapsed, result.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - start
        return f"TIMEOUT after {timeout}s", elapsed, -1


def rewrite_prompt(scenario: str, fixture_path: Path) -> str:
    """Read the scenario prompt and replace the fixture reference with the tempdir path."""
    prompt_file = SCENARIOS_DIR / f"{scenario}.txt"
    prompt = prompt_file.read_text(encoding="utf-8")
    fixture_name = scenario_fixture_name(scenario)

    # Replace relative fixture reference with absolute tempdir path
    original_ref = f"tests/fixtures/{fixture_name}"
    if original_ref not in prompt:
        raise ValueError(
            f"Scenario {scenario}.txt does not contain expected fixture reference '{original_ref}'"
        )
    return prompt.replace(original_ref, str(fixture_path))


# ---------------------------------------------------------------------------
# Mechanical checks
# ---------------------------------------------------------------------------

def load_check_module(scenario: str):
    """Dynamically import the check module for a scenario."""
    module_name = scenario.replace("-", "_")
    try:
        return importlib.import_module(f"checks.{module_name}")
    except ModuleNotFoundError:
        return None


def run_checks(scenario: str, output: str, generated_dir: Path) -> list:
    from checks.common import load_contract, run_contract_checks

    results = []
    contract = load_contract(CONTRACTS_DIR, scenario)
    if contract is not None:
        results.extend(
            run_contract_checks(
                output,
                generated_dir,
                contract,
                INSTRUCTION_FILES,
                FIXTURES_DIR / scenario_fixture_name(scenario),
            )
        )

    mod = load_check_module(scenario)
    if mod is None:
        return results
    return results + mod.check(output, generated_dir)


# ---------------------------------------------------------------------------
# LLM judge
# ---------------------------------------------------------------------------

def run_judge(scenario: str, generated_dir: Path, tool: str, timeout: int) -> str | None:
    """Run the LLM judge on the generated instruction file vs EXPECTED.md.

    Prefers claude haiku for cost. Falls back to codex with the cheapest model
    if claude is not available.
    """
    if not JUDGE_PROMPT_FILE.is_file():
        return None

    fixture_name = scenario_fixture_name(scenario)
    expected_path = FIXTURES_DIR / fixture_name / "EXPECTED.md"
    if not expected_path.is_file():
        return None

    # Find the generated instruction file
    generated_inst = None
    for name in INSTRUCTION_FILES:
        candidate = generated_dir / name
        if candidate.is_file():
            generated_inst = candidate
            break
    if generated_inst is None:
        return "SKIP: no instruction file generated"

    template = JUDGE_PROMPT_FILE.read_text(encoding="utf-8")
    expected_content = expected_path.read_text(encoding="utf-8")
    generated_content = generated_inst.read_text(encoding="utf-8")

    prompt = template.replace("{expected}", expected_content).replace("{generated}", generated_content)

    # Pick the cheapest available judge
    if shutil.which("claude"):
        judge_model = TOOL_MODELS["claude"]["haiku"]
        cmd = ["claude", "-p", "--model", judge_model]
    elif shutil.which("codex"):
        judge_model = TOOL_MODELS["codex"].get("gpt-5.4-mini", "gpt-5.4-mini")
        cmd = ["codex", "exec", "-m", judge_model]
    else:
        return "JUDGE_SKIP: no CLI available for judge"

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip() if result.returncode == 0 else f"JUDGE_ERROR: exit {result.returncode}"
    except subprocess.TimeoutExpired:
        return "JUDGE_TIMEOUT"


# ---------------------------------------------------------------------------
# Result persistence
# ---------------------------------------------------------------------------

def ensure_run_dir(timestamp: str) -> Path:
    run_dir = RUNS_DIR / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def save_manifest(run_dir: Path, tools: list[str], models_by_tool: dict[str, list[str]], scenarios: list[str]) -> None:
    cli_versions = {}
    for tool in tools:
        try:
            result = subprocess.run(
                [tool, "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                cli_versions[tool] = result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            cli_versions[tool] = "unknown"

    manifest = {
        "timestamp": run_dir.name,
        "tools": tools,
        "models_by_tool": models_by_tool,
        "scenarios": scenarios,
        "cli_versions": cli_versions,
        "skill_lines": len(SKILL_FILE.read_text(encoding="utf-8").splitlines()),
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def _combo_prefix(tool: str, model: str, run_idx: int | None = None) -> str:
    """Return a file-safe prefix for a tool+model combo, e.g. 'claude--sonnet'.

    When *run_idx* is not None (variance mode), appends '.run-{i}' so each
    repetition gets its own result files.
    """
    prefix = f"{tool}--{model}"
    if run_idx is not None:
        prefix += f".run-{run_idx}"
    return prefix


def save_result(
    run_dir: Path,
    tool: str,
    scenario: str,
    model: str,
    output: str,
    checks: list,
    judge: str | None,
    elapsed: float,
    returncode: int,
    run_idx: int | None = None,
) -> None:
    scenario_dir = run_dir / scenario
    scenario_dir.mkdir(parents=True, exist_ok=True)
    prefix = _combo_prefix(tool, model, run_idx)

    (scenario_dir / f"{prefix}.output.md").write_text(output, encoding="utf-8")

    checks_data = [
        {"name": c.name, "status": c.status, "tier": c.tier, "channel": c.channel, "detail": c.detail}
        for c in checks
    ]
    summary = {
        "tool": tool,
        "model": model,
        "elapsed_seconds": round(elapsed, 1),
        "returncode": returncode,
        "checks": checks_data,
        "judge": judge,
    }
    (scenario_dir / f"{prefix}.checks.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )


def snapshot_generated(run_dir: Path, tool: str, scenario: str, model: str, generated_dir: Path, run_idx: int | None = None) -> None:
    prefix = _combo_prefix(tool, model, run_idx)
    dest = run_dir / scenario / f"{prefix}.generated"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(generated_dir, dest, symlinks=True)


def result_exists(run_dir: Path, tool: str, scenario: str, model: str, run_idx: int | None = None) -> bool:
    prefix = _combo_prefix(tool, model, run_idx)
    return (run_dir / scenario / f"{prefix}.checks.json").is_file()


def latest_archived_case(scenario: str) -> tuple[Path, Path] | None:
    """Return (output_file, generated_dir) for the latest archived case."""
    scenario_dirs = sorted(
        [p / scenario for p in RUNS_DIR.iterdir() if p.is_dir() and (p / scenario).is_dir()],
        reverse=True,
    )
    for scenario_dir in scenario_dirs:
        for output_file in sorted(scenario_dir.glob("*.output.md"), reverse=True):
            stem = output_file.name.removesuffix(".output.md")
            generated_dir = scenario_dir / f"{stem}.generated"
            if generated_dir.is_dir():
                return output_file, generated_dir
    return None


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def _format_check_results(checks: list, elapsed: float, tool: str, model: str) -> list[str]:
    """Return formatted check results as lines (for buffered output)."""
    tag = f"[{tool}/{model}]"
    lines: list[str] = []

    hard_pass = sum(1 for c in checks if c.tier == "hard" and c.status == "pass")
    hard_fail = sum(1 for c in checks if c.tier == "hard" and c.status == "fail")
    hard_total = hard_pass + hard_fail
    soft_pass = sum(1 for c in checks if c.tier == "soft" and c.status == "pass")
    soft_fail = sum(1 for c in checks if c.tier == "soft" and c.status == "soft_fail")
    soft_total = soft_pass + soft_fail

    lines.append(f"  {tag} Mechanical checks ({elapsed:.0f}s):")
    if hard_total:
        line = f"    Hard: {hard_pass}/{hard_total} pass"
        if hard_fail:
            line += f" ({hard_fail} FAIL)"
        lines.append(line)
    if soft_total:
        line = f"    Soft: {soft_pass}/{soft_total} pass"
        if soft_fail:
            line += f" ({soft_fail} soft-fail)"
        lines.append(line)

    for c in checks:
        if c.status in ("fail", "soft_fail"):
            label = "FAIL" if c.status == "fail" else "SOFT_FAIL"
            channel = getattr(c, "channel", "general")
            detail = f" — {c.detail}" if c.detail else ""
            lines.append(f"    {label}  [{channel}] {c.name}{detail}")

    return lines


def print_check_results(checks: list, elapsed: float) -> None:
    hard_pass = sum(1 for c in checks if c.tier == "hard" and c.status == "pass")
    hard_fail = sum(1 for c in checks if c.tier == "hard" and c.status == "fail")
    hard_total = hard_pass + hard_fail
    soft_pass = sum(1 for c in checks if c.tier == "soft" and c.status == "pass")
    soft_fail = sum(1 for c in checks if c.tier == "soft" and c.status == "soft_fail")
    soft_total = soft_pass + soft_fail

    print(f"  Mechanical checks ({elapsed:.0f}s):")
    if hard_total:
        print(f"    Hard: {hard_pass}/{hard_total} pass", end="")
        if hard_fail:
            print(f" ({hard_fail} FAIL)", end="")
        print()
    if soft_total:
        print(f"    Soft: {soft_pass}/{soft_total} pass", end="")
        if soft_fail:
            print(f" ({soft_fail} soft-fail)", end="")
        print()

    for c in checks:
        if c.status in ("fail", "soft_fail"):
            label = "FAIL" if c.status == "fail" else "SOFT_FAIL"
            channel = getattr(c, "channel", "general")
            detail = f" — {c.detail}" if c.detail else ""
            print(f"    {label}  [{channel}] {c.name}{detail}")


def write_results_md(run_dir: Path, scenarios: list[str], combos: list[tuple[str, str]]) -> None:
    """Write a Markdown rollup. combos is a list of (tool, model) pairs."""
    lines = [
        f"## Run: {run_dir.name}\n",
    ]

    manifest_path = run_dir / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        cli_versions = manifest.get("cli_versions", {})
        if cli_versions:
            lines.append("CLI versions: " + ", ".join(f"{t}={v}" for t, v in cli_versions.items()) + "\n")

    for scenario in scenarios:
        lines.append(f"\n### {scenario}\n")
        lines.append("| Tool | Model | Hard | Soft | Judge | Time |")
        lines.append("|------|-------|------|------|-------|------|")

        for tool, model in combos:
            prefix = _combo_prefix(tool, model)
            checks_file = run_dir / scenario / f"{prefix}.checks.json"
            if not checks_file.is_file():
                continue

            data = json.loads(checks_file.read_text(encoding="utf-8"))
            checks = data.get("checks", [])
            elapsed = data.get("elapsed_seconds", 0)
            judge = data.get("judge", "")

            hard_checks = [c for c in checks if c["tier"] == "hard"]
            soft_checks = [c for c in checks if c["tier"] == "soft"]
            hard_pass = sum(1 for c in hard_checks if c["status"] == "pass")
            soft_pass = sum(1 for c in soft_checks if c["status"] == "pass")

            hard_str = f"{hard_pass}/{len(hard_checks)}" if hard_checks else "—"
            soft_str = f"{soft_pass}/{len(soft_checks)}" if soft_checks else "—"

            if judge is None:
                judge_str = "skipped"
            elif "NO CONTRADICTIONS" in judge:
                judge_str = "OK"
            elif judge and "CONTRADICTION" in judge:
                judge_str = f"{judge.count('CONTRADICTION')} flag(s)"
            else:
                judge_str = " ".join(judge.split())[:30] if judge else "—"

            lines.append(f"| {tool} | {model} | {hard_str} | {soft_str} | {judge_str} | {elapsed:.0f}s |")

            failing = [c for c in checks if c["status"] in ("fail", "soft_fail")]
            if failing:
                lines.append("")
                lines.append("| Channel | Failing checks |")
                lines.append("|---------|---------------|")
                by_channel: dict[str, list[str]] = {}
                for c in failing:
                    by_channel.setdefault(c.get("channel", "general"), []).append(c["name"])
                for channel, names in sorted(by_channel.items()):
                    lines.append(f"| {channel} | {'; '.join(names)} |")

    results_path = EVAL_DIR / "results.md"
    results_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Variance analysis
# ---------------------------------------------------------------------------

def compute_variance(
    run_dir: Path, tool: str, scenario: str, model: str, num_runs: int,
) -> dict:
    """Compare check results across *num_runs* repetitions and return a report."""
    all_checks: dict[str, list[dict]] = {}  # check_name -> list of per-run dicts

    for i in range(1, num_runs + 1):
        prefix = _combo_prefix(tool, model, i)
        checks_file = run_dir / scenario / f"{prefix}.checks.json"
        if not checks_file.is_file():
            continue
        data = json.loads(checks_file.read_text(encoding="utf-8"))
        for c in data.get("checks", []):
            all_checks.setdefault(c["name"], []).append(c)

    check_results: dict[str, dict] = {}
    for name, runs in all_checks.items():
        pass_count = sum(1 for r in runs if r["status"] == "pass")
        fail_count = len(runs) - pass_count
        tier = runs[0]["tier"] if runs else "unknown"
        stable = pass_count == len(runs) or fail_count == len(runs)
        check_results[name] = {
            "tier": tier,
            "runs": len(runs),
            "pass": pass_count,
            "fail": fail_count,
            "stable": stable,
        }

    total = len(check_results)
    stable_count = sum(1 for v in check_results.values() if v["stable"])
    hard_checks = {k: v for k, v in check_results.items() if v["tier"] == "hard"}
    soft_checks = {k: v for k, v in check_results.items() if v["tier"] == "soft"}

    return {
        "tool": tool,
        "model": model,
        "scenario": scenario,
        "num_runs": num_runs,
        "checks": check_results,
        "stability": stable_count / total if total else 1.0,
        "hard_stability": (
            sum(1 for v in hard_checks.values() if v["stable"]) / len(hard_checks)
            if hard_checks else 1.0
        ),
        "soft_stability": (
            sum(1 for v in soft_checks.values() if v["stable"]) / len(soft_checks)
            if soft_checks else 1.0
        ),
    }


def save_variance_report(run_dir: Path, report: dict) -> None:
    scenario_dir = run_dir / report["scenario"]
    scenario_dir.mkdir(parents=True, exist_ok=True)
    prefix = _combo_prefix(report["tool"], report["model"])
    path = scenario_dir / f"{prefix}.variance.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def print_variance_report(report: dict) -> None:
    tag = f"{report['scenario']} x {report['tool']}/{report['model']}"
    checks = report["checks"]
    total = len(checks)
    stable = sum(1 for v in checks.values() if v["stable"])
    pct = report["stability"] * 100

    print(f"\n  {tag}:")
    print(f"    Stability: {pct:.0f}% ({stable}/{total} checks consistent across {report['num_runs']} runs)")
    if pct < 100:
        print(f"    Hard: {report['hard_stability']*100:.0f}%  Soft: {report['soft_stability']*100:.0f}%")
        print(f"    Unstable checks:")
        for name, v in checks.items():
            if not v["stable"]:
                tier_label = v["tier"].upper()
                print(f"      {tier_label:4s}  {name}  {v['pass']}/{v['runs']} pass")


def write_variance_results_md(run_dir: Path, scenarios: list[str], combos: list[tuple[str, str]], num_runs: int) -> None:
    lines = [
        f"## Variance Run: {run_dir.name}\n",
        f"Repetitions per combo: {num_runs}\n",
        "",
        "| Scenario | Tool | Model | Stability | Hard | Soft | Unstable Checks |",
        "|----------|------|-------|-----------|------|------|-----------------|",
    ]
    for scenario in scenarios:
        for tool, model in combos:
            prefix = _combo_prefix(tool, model)
            vfile = run_dir / scenario / f"{prefix}.variance.json"
            if not vfile.is_file():
                continue
            report = json.loads(vfile.read_text(encoding="utf-8"))
            unstable = [k for k, v in report["checks"].items() if not v["stable"]]
            unstable_str = "; ".join(unstable) if unstable else "—"
            lines.append(
                f"| {scenario} | {tool} | {model} "
                f"| {report['stability']*100:.0f}% "
                f"| {report['hard_stability']*100:.0f}% "
                f"| {report['soft_stability']*100:.0f}% "
                f"| {unstable_str} |"
            )

    results_path = EVAL_DIR / "results.md"
    results_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Baseline comparison
# ---------------------------------------------------------------------------

def load_baseline() -> dict | None:
    if not BASELINE_FILE.is_file():
        return None
    return json.loads(BASELINE_FILE.read_text(encoding="utf-8"))


def compare_to_baseline(
    run_dir: Path, scenarios: list[str], combos: list[tuple[str, str]], num_runs: int,
) -> int:
    """Compare variance results to baseline. Returns count of hard regressions."""
    baseline = load_baseline()
    if baseline is None:
        print("\nNo baseline.json found. Run with --update-baseline to create one.")
        return 0

    base_scenarios = baseline.get("scenarios", {})
    regressions = 0

    print(f"\n{'='*60}")
    print("Baseline comparison")
    print(f"{'='*60}")

    for scenario in scenarios:
        for tool, model in combos:
            report = compute_variance(run_dir, tool, scenario, model, num_runs)
            base = base_scenarios.get(scenario)
            if base is None:
                print(f"\n  {scenario}: no baseline (new scenario)")
                continue

            hard_now = report["hard_stability"]
            hard_was = base["hard_stability"]
            soft_now = report["soft_stability"]
            soft_was = base["soft_stability"]

            hard_delta = hard_now - hard_was
            soft_delta = soft_now - soft_was

            label = ""
            if hard_delta < -0.01:
                label = " REGRESSION"
                regressions += 1
            elif hard_delta > 0.01:
                label = " IMPROVED"

            print(
                f"\n  {scenario}:{label}"
                f"\n    Hard: {hard_was*100:.0f}% -> {hard_now*100:.0f}% ({hard_delta*100:+.0f}%)"
                f"\n    Soft: {soft_was*100:.0f}% -> {soft_now*100:.0f}% ({soft_delta*100:+.0f}%)"
            )

    if regressions:
        print(f"\n{regressions} scenario(s) with hard regressions.")
    else:
        print("\nNo hard regressions detected.")
    return regressions


def update_baseline(
    run_dir: Path, scenarios: list[str], combos: list[tuple[str, str]], num_runs: int,
) -> None:
    """Update baseline.json with results from this variance run."""
    baseline = load_baseline() or {
        "_meta": {
            "description": "Compact variance baseline for regression detection",
            "format": "v2",
        },
        "scenarios": {},
    }

    baseline.setdefault("_meta", {})
    baseline["_meta"]["description"] = "Compact variance baseline for regression detection"
    baseline["_meta"]["format"] = "v2"

    for scenario in scenarios:
        for tool, model in combos:
            report = compute_variance(run_dir, tool, scenario, model, num_runs)
            baseline["scenarios"][scenario] = {
                "stability": round(report["stability"], 3),
                "hard_stability": round(report["hard_stability"], 3),
                "soft_stability": round(report["soft_stability"], 3),
                "num_runs": report["num_runs"],
                "source_run": run_dir.name,
            }

    BASELINE_FILE.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    print(f"\nBaseline updated: {BASELINE_FILE}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run eval scenarios for the harden-agent-instructions skill."
    )
    parser.add_argument(
        "--tool", nargs="+", default=[DEFAULT_TOOL],
        help=f"Agent CLI(s) to use (default: {DEFAULT_TOOL}). "
             f"Valid tools: {', '.join(sorted(TOOL_MODELS))}",
    )
    parser.add_argument(
        "--scenario", nargs="+",
        help="Scenario names to run (default: all)",
    )
    parser.add_argument(
        "--model", nargs="+", default=None,
        help="Model short names or raw model IDs (default: tool-specific). "
             "Short names — Claude: haiku, sonnet, opus. Codex: gpt-5.4, gpt-5.4-mini, etc. "
             "Raw IDs (e.g. us.anthropic.claude-sonnet-4-5-20250929-v1:0) are passed through.",
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT,
        help=f"Timeout per scenario in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--skip-judge", action="store_true",
        help="Skip the LLM judge layer",
    )
    parser.add_argument(
        "--resume", metavar="TIMESTAMP",
        help="Resume a previous run, skipping completed scenario/model combos",
    )
    parser.add_argument(
        "--rerun-failures", metavar="TIMESTAMP",
        help="Rerun only failed checks from a previous run",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Rerun even if results already exist for a combo",
    )
    parser.add_argument(
        "--parallel", "-j", type=int, default=0, metavar="N",
        help="Run up to N combos in parallel (default: 0 = all at once, 1 = sequential)",
    )
    parser.add_argument(
        "--variance", type=int, default=0, metavar="N",
        help="Run each combo N times and report check-level divergence (default: 0 = off)",
    )
    parser.add_argument(
        "--list", action="store_true", dest="list_scenarios",
        help="List available scenarios and exit",
    )
    parser.add_argument(
        "--self-test", nargs="+", metavar="SCENARIO",
        help="Replay latest archived eval run(s) for the given scenario(s) without invoking an agent CLI",
    )
    parser.add_argument(
        "--smoke", action="store_true",
        help=f"Run only the smoke subset ({len(SMOKE_SCENARIOS)} scenarios) instead of all",
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="After a variance run, compare results against baseline.json and report regressions",
    )
    parser.add_argument(
        "--update-baseline", action="store_true",
        help="Update baseline.json with results from this variance run",
    )
    parser.add_argument(
        "--generate-assets", action="store_true",
        help="Generate visual assets (radar charts, diffs, stability bars) from this run into assets/",
    )
    parser.add_argument(
        "--recheck", nargs="?", const="latest", metavar="TIMESTAMP",
        help="Replay checks against stored outputs (no agent invocation). "
             "Rewrites .checks.json and .variance.json in-place. "
             "Use without value for latest run, or pass a TIMESTAMP.",
    )
    parser.add_argument(
        "--retry-failed", nargs="?", const="latest", metavar="TIMESTAMP",
        help="Re-run only combos that had non-zero exit codes (timeouts, crashes) "
             "in a previous run. Deletes the failed results and re-queues them. "
             "Use without value for latest run, or pass a TIMESTAMP.",
    )
    return parser.parse_args()


def scenarios_with_failures(
    run_dir: Path, scenarios: list[str], combos: list[tuple[str, str]],
) -> list[tuple[str, str, str]]:
    """Return (tool, scenario, model) triples that had hard failures in a previous run."""
    triples = []
    for scenario in scenarios:
        for tool, model in combos:
            prefix = _combo_prefix(tool, model)
            checks_file = run_dir / scenario / f"{prefix}.checks.json"
            if not checks_file.is_file():
                triples.append((tool, scenario, model))
                continue
            data = json.loads(checks_file.read_text(encoding="utf-8"))
            has_failure = any(
                c["status"] == "fail" for c in data.get("checks", [])
            )
            if has_failure:
                triples.append((tool, scenario, model))
    return triples


def _find_failed_combos(run_dir: Path) -> list[tuple[str, str, str, int | None]]:
    """Scan a run dir for combos with non-zero returncode (timeouts, crashes).

    Returns list of (tool, scenario, model, run_idx) tuples.
    """
    failed = []
    for scenario_dir in sorted(run_dir.iterdir()):
        if not scenario_dir.is_dir():
            continue
        scenario = scenario_dir.name
        for checks_file in sorted(scenario_dir.glob("*.checks.json")):
            try:
                data = json.loads(checks_file.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            rc = data.get("returncode", 0)
            if rc != 0:
                tool = data.get("tool", "claude")
                model = data.get("model", "sonnet")
                # Parse run_idx from filename: tool--model.run-N.checks.json
                stem = checks_file.name.removesuffix(".checks.json")
                run_idx = None
                if ".run-" in stem:
                    try:
                        run_idx = int(stem.rsplit(".run-", 1)[1])
                    except ValueError:
                        pass
                failed.append((tool, scenario, model, run_idx))
    return failed


def _retry_failed(args) -> int:
    """Re-run combos that had non-zero exit codes in a previous run."""
    # Resolve run directory
    if args.retry_failed == "latest":
        candidates = sorted(RUNS_DIR.iterdir(), reverse=True) if RUNS_DIR.exists() else []
        candidates = [c for c in candidates if c.is_dir()]
        if not candidates:
            print("ERROR: no runs found", file=sys.stderr)
            return 1
        run_dir = candidates[0]
    else:
        run_dir = RUNS_DIR / args.retry_failed
        if not run_dir.is_dir():
            print(f"ERROR: no run found at {run_dir}", file=sys.stderr)
            return 1

    failed = _find_failed_combos(run_dir)
    if not failed:
        print(f"No failed combos found in {run_dir.name}")
        return 0

    print(f"Found {len(failed)} failed combo(s) in {run_dir.name}:")
    for tool, scenario, model, run_idx in failed:
        idx_label = f" run {run_idx}" if run_idx else ""
        print(f"  {scenario} x {tool}/{model}{idx_label}")

    # Delete failed results so they get re-run
    for tool, scenario, model, run_idx in failed:
        prefix = _combo_prefix(tool, model, run_idx)
        scenario_dir = run_dir / scenario
        for suffix in (".checks.json", ".output.md"):
            f = scenario_dir / f"{prefix}{suffix}"
            if f.exists():
                f.unlink()
        gen_dir = scenario_dir / f"{prefix}.generated"
        if gen_dir.exists():
            shutil.rmtree(gen_dir)

    # Re-invoke main run with --resume pointing at this run dir
    # Build a synthetic args-like invocation
    retry_argv = [
        sys.argv[0],
        "--resume", run_dir.name,
        "--skip-judge" if args.skip_judge else None,
        "-j", str(args.parallel),
        "--timeout", str(args.timeout),
    ]
    if args.generate_assets:
        retry_argv.append("--generate-assets")
    # Filter Nones
    retry_argv = [a for a in retry_argv if a is not None]

    # Add variance if the run was a variance run (detect from run_idx presence)
    has_variance = any(ri is not None for _, _, _, ri in failed)
    if has_variance:
        # Detect N from the highest run_idx
        max_idx = max(ri for _, _, _, ri in failed if ri is not None)
        retry_argv.extend(["--variance", str(max_idx)])

    # Add tool/model from the failed combos
    tools_seen = sorted({t for t, _, _, _ in failed})
    models_seen = sorted({m for _, _, m, _ in failed})
    retry_argv.extend(["--tool"] + tools_seen)
    retry_argv.extend(["--model"] + models_seen)

    # Add scenarios
    scenarios_seen = sorted({s for _, s, _, _ in failed})
    retry_argv.extend(["--scenario"] + scenarios_seen)

    print(f"\nRetrying with: {' '.join(retry_argv[1:])}\n")
    os.execvp(sys.executable, [sys.executable] + retry_argv)
    return 0  # unreachable after execvp


def _recheck(args) -> int:
    """Replay checks against stored outputs and rewrite .checks.json + .variance.json."""
    # Resolve run directory
    if args.recheck == "latest":
        candidates = sorted(RUNS_DIR.iterdir(), reverse=True) if RUNS_DIR.exists() else []
        if not candidates:
            print("ERROR: no runs found", file=sys.stderr)
            return 1
        run_dir = candidates[0]
    else:
        run_dir = RUNS_DIR / args.recheck
        if not run_dir.exists():
            print(f"ERROR: run dir not found: {run_dir}", file=sys.stderr)
            return 1

    print(f"Rechecking run: {run_dir.name}")

    # Find all scenario dirs
    scenario_dirs = sorted(d for d in run_dir.iterdir() if d.is_dir())
    rechecked = 0
    variance_combos: dict[str, dict[str, list[int]]] = {}  # scenario -> {combo_base -> [run_idxs]}

    for scenario_dir in scenario_dirs:
        scenario = scenario_dir.name

        # Find all output+generated pairs
        for output_file in sorted(scenario_dir.glob("*.output.md")):
            stem = output_file.name.removesuffix(".output.md")
            generated_dir = scenario_dir / f"{stem}.generated"
            if not generated_dir.is_dir():
                continue

            output = output_file.read_text(encoding="utf-8")
            checks = run_checks(scenario, output, generated_dir)

            # Rewrite checks.json
            checks_data = [
                {"name": c.name, "status": c.status, "tier": c.tier, "channel": c.channel, "detail": c.detail}
                for c in checks
            ]
            checks_file = scenario_dir / f"{stem}.checks.json"
            old_data = json.loads(checks_file.read_text()) if checks_file.exists() else {}
            summary = {
                "tool": old_data.get("tool", "unknown"),
                "model": old_data.get("model", "unknown"),
                "elapsed_seconds": old_data.get("elapsed_seconds", 0),
                "returncode": old_data.get("returncode", 0),
                "checks": checks_data,
                "judge": old_data.get("judge"),
            }
            checks_file.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            rechecked += 1

            # Track variance groupings: strip .run-N suffix to find combo base
            import re as _re
            m = _re.match(r"^(.+)\.run-(\d+)$", stem)
            if m:
                combo_base = m.group(1)
                run_idx = int(m.group(2))
                variance_combos.setdefault(scenario, {}).setdefault(combo_base, []).append(run_idx)

    print(f"  Rechecked {rechecked} result(s)")

    # Recompute variance reports for runs that had multiple repetitions
    variance_count = 0
    for scenario, combos in variance_combos.items():
        for combo_base, run_idxs in combos.items():
            if len(run_idxs) < 2:
                continue
            # Parse tool--model from combo_base
            parts = combo_base.split("--", 1)
            tool = parts[0] if parts else "unknown"
            model = parts[1] if len(parts) > 1 else "unknown"
            num_runs = max(run_idxs)
            report = compute_variance(run_dir, tool, scenario, model, num_runs)
            save_variance_report(run_dir, report)
            variance_count += 1
            print(f"  Updated variance: {scenario} x {combo_base} ({num_runs} runs, stability={report['stability']:.0%})")

    if variance_count:
        print(f"  Rewrote {variance_count} variance report(s)")

    # Generate assets if requested
    if args.generate_assets:
        _generate_assets(run_dir)

    return 0


def _generate_assets(run_dir: Path) -> None:
    """Import and run asset generation from the eval module."""
    try:
        from generate_assets import generate_all
        generate_all(run_dir=run_dir)
    except ImportError as e:
        print(f"  ⚠ Could not import generate_assets: {e}", file=sys.stderr)


def main() -> int:
    args = parse_args()
    tools = args.tool
    all_scenarios = available_scenarios()

    if args.self_test:
        hard_failures = 0
        for scenario in args.self_test:
            if scenario not in all_scenarios:
                print(f"ERROR: unknown scenario '{scenario}'. Available: {', '.join(all_scenarios)}", file=sys.stderr)
                return 1

            archived = latest_archived_case(scenario)
            if archived is None:
                print(f"ERROR: no archived self-test case found for {scenario}", file=sys.stderr)
                return 1

            output_file, generated_dir = archived
            output = output_file.read_text(encoding="utf-8")
            checks = run_checks(scenario, output, generated_dir)

            print(f"\n[self-test] {scenario}")
            print(f"  Output:    {output_file}")
            print(f"  Generated: {generated_dir}")
            for line in _format_check_results(checks, 0.0, "self-test", output_file.stem):
                print(line)

            if any(c.status == "fail" for c in checks):
                hard_failures += 1

        return 1 if hard_failures else 0

    # --recheck: replay checks against stored outputs, rewrite checks.json + variance.json
    if args.recheck:
        return _recheck(args)

    # --retry-failed: find and re-run combos with non-zero exit codes
    if args.retry_failed:
        return _retry_failed(args)

    # Validate tools
    for t in tools:
        if t not in TOOL_MODELS:
            print(f"ERROR: unknown tool '{t}'. Available: {', '.join(sorted(TOOL_MODELS))}", file=sys.stderr)
            return 1

    if args.list_scenarios:
        for s in available_scenarios():
            mod = load_check_module(s)
            status = "checks available" if mod else "no checks yet"
            print(f"  {s} ({status})")
        return 0

    # Pre-flight — check all tools
    for t in tools:
        problems = preflight(t)
        if problems:
            for p in problems:
                print(f"ERROR: {p}", file=sys.stderr)
            return 1

    # Resolve scenarios
    if args.smoke:
        scenarios = [s for s in SMOKE_SCENARIOS if s in all_scenarios]
        if args.scenario:
            print("WARNING: --smoke overrides --scenario", file=sys.stderr)
    else:
        scenarios = args.scenario or all_scenarios
    for s in scenarios:
        if s not in all_scenarios:
            print(f"ERROR: unknown scenario '{s}'. Available: {', '.join(all_scenarios)}", file=sys.stderr)
            return 1

    # Build (tool, model) combos.
    # If --model is given, each model is paired only with tools that recognize
    # it (present in TOOL_MODELS[tool]) or that might accept it as a raw ID
    # (contains "/" or ":" — looks like a Bedrock ARN or versioned ID).
    # If --model is not given, each tool uses its own default.
    all_known_models = {m for models in TOOL_MODELS.values() for m in models}

    def _is_raw_id(model: str) -> bool:
        return "/" in model or ":" in model

    combos: list[tuple[str, str]] = []
    models_by_tool: dict[str, list[str]] = {}
    for t in tools:
        if args.model:
            matched = []
            for m in args.model:
                if m in TOOL_MODELS[t]:
                    # Known short name for this tool
                    matched.append(m)
                elif m not in all_known_models:
                    # Not a known short name for ANY tool — treat as raw ID,
                    # pass to every tool (user's responsibility)
                    matched.append(m)
                # else: known short name for a different tool — skip
            models_by_tool[t] = matched
        else:
            models_by_tool[t] = [TOOL_DEFAULTS[t]]
        for m in models_by_tool[t]:
            combos.append((t, m))

    if not combos:
        print("ERROR: no valid tool/model combos. The specified models don't match any of the specified tools.", file=sys.stderr)
        return 1

    # Resolve run directory
    if args.resume:
        timestamp = args.resume
    elif args.rerun_failures:
        timestamp = args.rerun_failures
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    run_dir = ensure_run_dir(timestamp)
    save_manifest(run_dir, tools, models_by_tool, scenarios)

    # Build the work list: (tool, scenario, model, run_idx) tuples.
    # run_idx is None for normal mode, 1..N for variance mode.
    variance_n = args.variance
    if variance_n and args.rerun_failures:
        print("ERROR: --variance cannot be combined with --rerun-failures", file=sys.stderr)
        return 1

    if args.rerun_failures:
        prev_dir = RUNS_DIR / args.rerun_failures
        if not prev_dir.is_dir():
            print(f"ERROR: no run found at {prev_dir}", file=sys.stderr)
            return 1
        work = [(t, s, m, None) for t, s, m in scenarios_with_failures(prev_dir, scenarios, combos)]
    elif variance_n:
        work = [
            (t, s, m, i)
            for s in scenarios for t, m in combos
            for i in range(1, variance_n + 1)
        ]
    else:
        work = [(t, s, m, None) for s in scenarios for t, m in combos]

    # Filter already-done combos (unless --force)
    if not args.force and (args.resume or args.rerun_failures or variance_n):
        work = [(t, s, m, ri) for t, s, m, ri in work if not result_exists(run_dir, t, s, m, ri)]

    if not work:
        print("Nothing to run (all combos already completed). Use --force to rerun.")
        return 0

    total = len(work)
    hard_failures = 0
    _print_lock = threading.Lock()

    def _run_one(idx: int, tool: str, scenario: str, model: str, run_idx: int | None = None) -> bool:
        """Run a single combo. Returns True if hard checks failed."""
        tool_models_map = TOOL_MODELS[tool]
        model_id = tool_models_map.get(model, model)
        buf: list[str] = []
        run_tag = f" run {run_idx}/{args.variance}" if run_idx is not None else ""
        buf.append(f"\n[{idx}/{total}] {scenario} x {tool}/{model}{run_tag}")

        had_hard_failure = False

        with tempfile.TemporaryDirectory(prefix=f"eval_{scenario}_") as tmpdir:
            tmp = Path(tmpdir)
            fixture_path = copy_fixture(scenario, tmp)

            try:
                prompt = rewrite_prompt(scenario, fixture_path)
            except ValueError as e:
                buf.append(f"  SKIP: {e}")
                with _print_lock:
                    print("\n".join(buf), flush=True)
                return False

            buf.append(f"  Running {tool} --model {model_id} ... (timeout: {args.timeout}s)")
            with _print_lock:
                print("\n".join(buf), flush=True)
                buf.clear()

            max_retries = 2
            for attempt in range(1 + max_retries):
                output, elapsed, returncode = run_agent(tool, prompt, model_id, fixture_path, args.timeout)
                if returncode not in (-1,) or attempt >= max_retries:
                    break
                buf.append(f"  [{tool}/{model}] TIMEOUT — retry {attempt + 1}/{max_retries}")
                with _print_lock:
                    print("\n".join(buf), flush=True)
                    buf.clear()
                time.sleep(5 * (attempt + 1))

            if returncode == -1:
                buf.append(f"  [{tool}/{model}] TIMEOUT after {args.timeout}s (exhausted {max_retries} retries)")
            elif returncode != 0:
                buf.append(f"  [{tool}/{model}] {tool} exited {returncode}")
            else:
                buf.append(f"  [{tool}/{model}] Done ({elapsed:.0f}s)")

            checks = run_checks(scenario, output, fixture_path)
            if checks:
                buf.extend(_format_check_results(checks, elapsed, tool, model))
            else:
                buf.append(f"  [{tool}/{model}] No check module — output saved for manual review")

            judge_result = None
            if not args.skip_judge and returncode == 0:
                buf.append(f"  [{tool}/{model}] Running LLM judge ...")
                judge_result = run_judge(scenario, fixture_path, tool, args.timeout)
                if judge_result:
                    buf.append(f"  [{tool}/{model}] Judge: {judge_result[:120]}")

            save_result(run_dir, tool, scenario, model, output, checks, judge_result, elapsed, returncode, run_idx)
            snapshot_generated(run_dir, tool, scenario, model, fixture_path, run_idx)

            if any(c.status == "fail" for c in checks):
                had_hard_failure = True

        with _print_lock:
            print("\n".join(buf), flush=True)
        return had_hard_failure

    if variance_n:
        print(f"Variance mode: {variance_n} runs per combo, {total} total invocations")
    parallelism = args.parallel if args.parallel > 0 else total
    if parallelism > 1:
        print(f"Running {total} combos with parallelism={parallelism}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallelism) as pool:
            futures = {
                pool.submit(_run_one, idx, t, s, m, ri): (t, s, m, ri)
                for idx, (t, s, m, ri) in enumerate(work, 1)
            }
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    hard_failures += 1
    else:
        for idx, (tool, scenario, model, ri) in enumerate(work, 1):
            if _run_one(idx, tool, scenario, model, ri):
                hard_failures += 1

    # Variance analysis
    if variance_n:
        print(f"\n{'='*60}")
        print(f"Variance report ({variance_n} runs per combo)")
        print(f"{'='*60}")
        for scenario in scenarios:
            for tool, model in combos:
                report = compute_variance(run_dir, tool, scenario, model, variance_n)
                save_variance_report(run_dir, report)
                print_variance_report(report)
        write_variance_results_md(run_dir, scenarios, combos, variance_n)
        print(f"\nResults: {run_dir}")
        print(f"Rollup:  {EVAL_DIR / 'results.md'}")

        # Compare to baseline if requested (or by default when baseline exists)
        baseline_regressions = 0
        if args.compare or (BASELINE_FILE.is_file() and not args.update_baseline):
            baseline_regressions = compare_to_baseline(run_dir, scenarios, combos, variance_n)

        # Update baseline if requested
        if args.update_baseline:
            update_baseline(run_dir, scenarios, combos, variance_n)

        # Generate visual assets if requested
        if args.generate_assets:
            _generate_assets(run_dir)

        # In variance mode, exit 1 if hard regressions detected
        if baseline_regressions:
            return 1

        # Also exit 1 if any combo has <100% hard stability
        unstable = any(
            not v["stable"]
            for s in scenarios for t, m in combos
            for v in compute_variance(run_dir, t, s, m, variance_n)["checks"].values()
            if v["tier"] == "hard"
        )
        if unstable:
            print("\nSome hard checks were unstable across runs.")
        return 1 if unstable else 0

    # Write rollup (normal mode)
    write_results_md(run_dir, scenarios, combos)
    print(f"\nResults: {run_dir}")
    print(f"Rollup:  {EVAL_DIR / 'results.md'}")

    # Generate visual assets if requested
    if args.generate_assets:
        _generate_assets(run_dir)

    if hard_failures:
        print(f"\n{hard_failures} scenario(s) had hard failures.")
        return 1
    return 0


if __name__ == "__main__":
    # Ensure check modules are importable from the eval directory
    sys.path.insert(0, str(EVAL_DIR))
    sys.exit(main())
