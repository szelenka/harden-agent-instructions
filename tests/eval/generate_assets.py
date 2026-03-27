#!/usr/bin/env python3
"""Generate visual assets from eval data — pure stdlib, no external dependencies.

Usage (standalone):
    python3 tests/eval/generate_assets.py [--run-dir EVAL_RUN_DIR]

Usage (from run_eval.py):
    python3 tests/eval/run_eval.py --smoke --variance 5 --skip-judge --generate-assets

Outputs go to tests/eval/assets/ in the repo.

Assets produced:
  - tests/eval/assets/stability-bars.svg           Per-scenario stability bar chart from latest variance runs
  - tests/eval/assets/<scenario>/checks.svg         Per-scenario before/after stacked bar chart
  - tests/eval/assets/<scenario>/diff.svg          Side-by-side diff of original vs hardened AGENTS.md
  - tests/eval/assets/<scenario>/audit.svg         Styled audit output from a real eval run
"""

from __future__ import annotations

import difflib
import html
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS = Path(__file__).resolve().parent / "assets"
BASELINE = ROOT / "tests" / "eval" / "baseline.json"
FIXTURES = ROOT / "tests" / "fixtures"
SCENARIOS = ROOT / "tests" / "eval" / "scenarios"


def current_scenarios() -> set[str]:
    return {p.stem for p in SCENARIOS.glob("*.txt")}

# -- Helpers ------------------------------------------------------------------

def find_latest_run() -> Path | None:
    runs = ROOT / "tests" / "eval" / "runs"
    if not runs.exists():
        return None
    dirs = sorted(runs.iterdir(), reverse=True)
    return dirs[0] if dirs else None


def _prefix_from_checks_json(checks_path: Path) -> str:
    """Extract the run prefix from a checks.json filename.

    e.g. 'claude--sonnet.run-3.checks.json' -> 'claude--sonnet.run-3'
         'claude--sonnet.checks.json' -> 'claude--sonnet'
    """
    return checks_path.name.removesuffix(".checks.json")


def find_generated_agents(run_dir: Path, scenario: str, prefix: str = "") -> Path | None:
    scenario_dir = run_dir / scenario
    if not scenario_dir.exists():
        return None
    if prefix:
        candidate = scenario_dir / f"{prefix}.generated" / "AGENTS.md"
        if candidate.exists():
            return candidate
    for d in sorted(scenario_dir.iterdir()):
        candidate = d / "AGENTS.md"
        if candidate.exists():
            return candidate
    return None


def find_output_md(run_dir: Path, scenario: str, prefix: str = "") -> Path | None:
    scenario_dir = run_dir / scenario
    if not scenario_dir.exists():
        return None
    if prefix:
        candidate = scenario_dir / f"{prefix}.output.md"
        if candidate.exists():
            return candidate
    for f in sorted(scenario_dir.iterdir()):
        if f.name.endswith(".output.md"):
            return f
    return None


# -- Side-by-Side Diff (SVG) -------------------------------------------------

def _diff_segments(text: str) -> list[tuple[str, str]]:
    """Split a cell into (class, text) segments for SVG rendering."""
    if not text:
        return [("ctx", "")]
    segments: list[tuple[str, str]] = []
    pos = 0
    pattern = re.compile(r'<span class="(diff_add|diff_sub|diff_chg)">(.*?)</span>', re.S)
    for match in pattern.finditer(text):
        if match.start() > pos:
            prefix = html.unescape(re.sub(r"<[^>]+>", "", text[pos:match.start()])).replace("\xa0", " ")
            if prefix:
                segments.append(("ctx", prefix))
        cls = match.group(1).replace("diff_", "")
        value = html.unescape(re.sub(r"<[^>]+>", "", match.group(2))).replace("\xa0", " ")
        segments.append((cls, value))
        pos = match.end()
    if pos < len(text):
        suffix = html.unescape(re.sub(r"<[^>]+>", "", text[pos:])).replace("\xa0", " ")
        if suffix:
            segments.append(("ctx", suffix))
    return segments or [("ctx", "")]


def _clean_diff_cell(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).replace("\xa0", " ").rstrip()


def _wrap_segments(segments: list[tuple[str, str]], max_chars: int) -> list[list[tuple[str, str]]]:
    """Wrap colored text segments into multiple lines within a fixed character width."""
    if max_chars <= 0:
        return [segments]

    lines: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] = []
    current_len = 0

    def push_current() -> None:
        nonlocal current, current_len
        lines.append(current if current else [("ctx", "")])
        current = []
        current_len = 0

    def append_piece(cls: str, piece: str) -> None:
        nonlocal current_len
        if not piece:
            return
        if current and current[-1][0] == cls:
            prev_cls, prev_text = current[-1]
            current[-1] = (prev_cls, prev_text + piece)
        else:
            current.append((cls, piece))
        current_len += len(piece)

    for cls, text in segments:
        if not text:
            continue
        tokens = re.split(r"(\s+)", text)
        for token in tokens:
            if token == "":
                continue
            remaining = token
            while remaining:
                if current_len == 0 and len(remaining) <= max_chars:
                    append_piece(cls, remaining)
                    remaining = ""
                    continue
                available = max_chars - current_len
                if available <= 0:
                    push_current()
                    continue
                if len(remaining) <= available:
                    append_piece(cls, remaining)
                    remaining = ""
                    continue
                if remaining.isspace():
                    push_current()
                    remaining = remaining.lstrip()
                    continue

                split_at = remaining.rfind(" ", 0, available + 1)
                if split_at > 0:
                    append_piece(cls, remaining[:split_at])
                    remaining = remaining[split_at:].lstrip()
                    push_current()
                    continue

                append_piece(cls, remaining[:available])
                remaining = remaining[available:]
                push_current()

    if current or not lines:
        push_current()
    return lines


def generate_diff_svg(before_path: Path | None, after_path: Path, out_path: Path, scenario: str = "") -> None:
    before = before_path.read_text().splitlines() if before_path and before_path.exists() else []
    after = after_path.read_text().splitlines()

    label = scenario or (before_path.parent.name if before_path else after_path.parent.name)
    left_title = f"Before ({label}/AGENTS.md)" if before_path and before_path.exists() else "Before (no AGENTS.md)"
    right_title = "After (hardened by skill)"

    rows: list[tuple[str, list[tuple[str, str]], str, str, list[tuple[str, str]], str]] = []
    matcher = difflib.SequenceMatcher(a=before, b=after)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for left_idx, right_idx in zip(range(i1, i2), range(j1, j2)):
                text = before[left_idx]
                rows.append((
                    str(left_idx + 1), [("ctx", text)], "ctx",
                    str(right_idx + 1), [("ctx", text)], "ctx",
                ))
            continue

        left_chunk = before[i1:i2]
        right_chunk = after[j1:j2]
        span = max(len(left_chunk), len(right_chunk))
        for offset in range(span):
            has_left = offset < len(left_chunk)
            has_right = offset < len(right_chunk)
            left_no = str(i1 + offset + 1) if has_left else ""
            right_no = str(j1 + offset + 1) if has_right else ""

            if tag == "delete":
                left_segments = [("sub", left_chunk[offset])] if has_left else [("ctx", "")]
                right_segments = [("ctx", "")]
                left_cls, right_cls = "sub", "ctx"
            elif tag == "insert":
                left_segments = [("ctx", "")]
                right_segments = [("add", right_chunk[offset])] if has_right else [("ctx", "")]
                left_cls, right_cls = "ctx", "add"
            else:  # replace
                left_segments = [("sub", left_chunk[offset])] if has_left else [("ctx", "")]
                right_segments = [("add", right_chunk[offset])] if has_right else [("ctx", "")]
                left_cls = "sub" if has_left else "ctx"
                right_cls = "add" if has_right else "ctx"

            rows.append((left_no, left_segments, left_cls, right_no, right_segments, right_cls))

    while rows and not any((rows[0][0], "".join(t for _, t in rows[0][1]), rows[0][3], "".join(t for _, t in rows[0][4]))):
        rows.pop(0)
    while rows and not any((rows[-1][0], "".join(t for _, t in rows[-1][1]), rows[-1][3], "".join(t for _, t in rows[-1][4]))):
        rows.pop()

    width = 1440
    header_h = 110
    line_h = 26
    left_x = 40
    gap = 20
    panel_w = (width - left_x * 2 - gap) // 2
    num_w = 42
    text_pad = 14
    inner_pad = 18
    # Conservative monospace width estimate so rendered lines stay inside the panel.
    char_w = 9.6
    max_chars = max(12, int((panel_w - num_w - text_pad - inner_pad * 2) / char_w) - 1)

    colors = {
        "bg": "#0d1117",
        "panel": "#161b22",
        "border": "#30363d",
        "title": "#c9d1d9",
        "muted": "#8b949e",
        "ctx_bg": "#161b22",
        "ctx_fg": "#c9d1d9",
        "add_bg": "#12261e",
        "add_fg": "#56d364",
        "sub_bg": "#2d1215",
        "sub_fg": "#f85149",
        "chg_bg": "#272115",
        "chg_fg": "#e3b341",
    }

    wrapped_rows: list[tuple[str, list[list[tuple[str, str]]], str, str, list[list[tuple[str, str]]], str, int]] = []
    for left_no, left_segments, left_cls, right_no, right_segments, right_cls in rows:
        left_lines = _wrap_segments(left_segments, max_chars)
        right_lines = _wrap_segments(right_segments, max_chars)
        wrapped_rows.append((left_no, left_lines, left_cls, right_no, right_lines, right_cls, max(len(left_lines), len(right_lines))))

    body_h = sum(row[-1] for row in wrapped_rows) * line_h + 20
    height = header_h + body_h + 40

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{html.escape(label)} side-by-side diff</title>',
        f'<desc id="desc">A side-by-side diff of {html.escape(label)} AGENTS.md before and after hardening. Removed lines appear red on the left, added lines green on the right.</desc>',
        f'<rect width="{width}" height="{height}" fill="{colors["bg"]}"/>',
        f'<text x="40" y="46" fill="{colors["title"]}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="26" font-weight="700">{html.escape(label)}: side-by-side diff</text>',
        f'<text x="40" y="76" fill="{colors["muted"]}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16">source: generated from fixture AGENTS.md (or empty baseline) and hardened output</text>',
    ]

    for col_x, title in ((left_x, left_title), (left_x + panel_w + gap, right_title)):
        svg.append(
            f'<rect x="{col_x}" y="{header_h}" width="{panel_w}" height="{body_h}" rx="10" fill="{colors["panel"]}" stroke="{colors["border"]}"/>'
        )
        svg.append(
            f'<text x="{col_x + 14}" y="{header_h - 14}" fill="{colors["muted"]}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16">{html.escape(title)}</text>'
        )

    def _render_cell(col_x: int, y: int, line_no: str, wrapped_lines: list[list[tuple[str, str]]], cls_name: str, row_span: int) -> None:
        cell_h = row_span * line_h
        svg.append(
            f'<rect x="{col_x + 1}" y="{y}" width="{panel_w - 2}" height="{cell_h}" fill="{colors[f"{cls_name}_bg"]}"/>'
        )
        if line_no:
            svg.append(
                f'<text x="{col_x + num_w - 8}" y="{y + 18}" text-anchor="end" fill="{colors["muted"]}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="15">{html.escape(line_no)}</text>'
            )
        for line_idx, segments in enumerate(wrapped_lines):
            cursor_x = col_x + num_w + text_pad
            line_y = y + 18 + line_idx * line_h
            for seg_cls, seg_text in segments:
                if not seg_text:
                    continue
                fg = colors[f"{seg_cls}_fg"] if f"{seg_cls}_fg" in colors else colors["ctx_fg"]
                svg.append(
                    f'<text x="{cursor_x:.1f}" y="{line_y}" fill="{fg}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="15">{html.escape(seg_text)}</text>'
                )
                cursor_x += len(seg_text) * char_w

    y = header_h + 10
    for left_no, left_lines, left_cls, right_no, right_lines, right_cls, row_span in wrapped_rows:
        _render_cell(left_x, y, left_no, left_lines, left_cls, row_span)
        _render_cell(left_x + panel_w + gap, y, right_no, right_lines, right_cls, row_span)
        y += row_span * line_h

    svg.append("</svg>")
    content = "\n".join(svg)
    ET.fromstring(content)
    out_path.write_text(content)
    print(f"  ✓ {out_path.relative_to(ROOT)}")


# -- Stability Bar Chart (SVG) -----------------------------------------------

BAR_COLORS = {"high": "#56d364", "mid": "#e3b341", "low": "#f85149"}


def stability_color(val: float) -> str:
    if val >= 0.9:
        return BAR_COLORS["high"]
    if val >= 0.7:
        return BAR_COLORS["mid"]
    return BAR_COLORS["low"]


def _find_latest_variance_per_scenario() -> dict[str, dict]:
    """Scan eval runs for the latest variance.json per scenario.

    Returns {scenario_name: {stability, hard_stability, soft_stability,
    hard_rates: [float], soft_rates: [float]}} where *_rates are per-check
    pass rates (pass/runs) for computing min/max variance bars.
    """
    runs_dir = ROOT / "tests" / "eval" / "runs"
    if not runs_dir.exists():
        return {}
    # Keyed by scenario -> (run_timestamp, data_dict) to keep the latest
    latest: dict[str, tuple[str, dict]] = {}
    active = current_scenarios()
    for run_dir in sorted(runs_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        for scenario_dir in run_dir.iterdir():
            if not scenario_dir.is_dir():
                continue
            if scenario_dir.name not in active:
                continue
            for f in scenario_dir.iterdir():
                if f.name.endswith(".variance.json"):
                    try:
                        data = json.loads(f.read_text())
                    except (json.JSONDecodeError, OSError):
                        continue
                    checks = data.get("checks", {})
                    hard_rates = [
                        v["pass"] / v["runs"] for v in checks.values()
                        if v.get("tier") == "hard" and v.get("runs", 0) > 0
                    ]
                    soft_rates = [
                        v["pass"] / v["runs"] for v in checks.values()
                        if v.get("tier") == "soft" and v.get("runs", 0) > 0
                    ]
                    scenario = scenario_dir.name
                    ts = run_dir.name
                    if scenario not in latest or ts > latest[scenario][0]:
                        latest[scenario] = (ts, {
                            "stability": data.get("stability", 0),
                            "hard_stability": data.get("hard_stability", 0),
                            "soft_stability": data.get("soft_stability", 0),
                            "hard_rates": hard_rates,
                            "soft_rates": soft_rates,
                            "num_runs": data.get("num_runs", 0),
                        })
    return {s: info for s, (_, info) in latest.items()}


def generate_stability_svg(out_path: Path, variance_data: dict[str, dict] | None = None) -> None:
    """Render per-scenario variance as dot-whisker plots.

    Each scenario gets two rows (hard checks, soft checks). Each row shows
    individual check pass-rates as dots along a 0–100% axis, with a whisker
    line spanning min→max. Dots are colored green (100%), yellow (partial),
    or red (0%) matching the checks.svg palette.
    """
    if variance_data is None:
        variance_data = _find_latest_variance_per_scenario()
    if not variance_data:
        if BASELINE.exists():
            bl = json.loads(BASELINE.read_text())
            active = current_scenarios()
            variance_data = {
                name: {
                    "stability": info["stability"],
                    "hard_stability": info["hard_stability"],
                    "soft_stability": info.get("soft_stability", info["stability"]),
                    "hard_rates": [],
                    "soft_rates": [],
                }
                for name, info in bl.get("scenarios", {}).items()
                if name in active
            }
        else:
            print("  ⚠ No variance data or baseline found, skipping stability chart")
            return

    scenarios = sorted(variance_data.items(), key=lambda item: item[0])
    num_runs = _variance_n(variance_data)

    # Colors matching checks.svg
    C_PASS = "#56d364"
    C_FLAKY = "#e3b341"
    C_FAIL = "#f85149"

    # Layout
    row_h = 20
    row_gap = 3
    group_gap = 14
    label_w = 190
    axis_w = 300
    right_margin = 120
    padding_top = 36
    padding_bottom = 10
    legend_h = 52
    tier_label_w = 35

    n = len(scenarios)
    chart_h = n * (2 * row_h + row_gap + group_gap) - group_gap
    total_h = padding_top + chart_h + legend_h + padding_bottom
    total_w = label_w + tier_label_w + axis_w + right_margin

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}">',
        f'<rect width="100%" height="100%" fill="#0d1117" rx="8"/>',
        f'<text x="{total_w // 2}" y="22" text-anchor="middle" fill="#58a6ff" font-family="sans-serif" font-size="14" font-weight="bold">Eval Variance by Scenario (N={num_runs} runs each)</text>',
    ]

    y = padding_top

    for name, info in scenarios:
        hard_rates = info.get("hard_rates", [])
        soft_rates = info.get("soft_rates", [])

        # Scenario label (centered between the two rows), wrapped if needed
        label_y = y + row_h + row_gap / 2
        label_lines = _wrap_label(name)
        line_gap = 12
        start_y = label_y - ((len(label_lines) - 1) * line_gap) / 2 + 4
        for idx, line in enumerate(label_lines):
            svg.append(
                f'<text x="{label_w - 8}" y="{start_y + idx * line_gap:.1f}" text-anchor="end" '
                f'fill="#8b949e" font-family="monospace" font-size="11">{html.escape(line)}</text>'
            )

        # Hard row
        _variance_row(svg, y, label_w, tier_label_w, axis_w, row_h, "hard", hard_rates, C_PASS, C_FLAKY, C_FAIL)
        y += row_h + row_gap

        # Soft row
        _variance_row(svg, y, label_w, tier_label_w, axis_w, row_h, "soft", soft_rates, C_PASS, C_FLAKY, C_FAIL)
        y += row_h + group_gap

    # Legend
    color_items = [("Stable (≥90%)", C_PASS), ("Acceptable (70–89%)", C_FLAKY), ("Flaky (&lt;70%)", C_FAIL)]
    center_x = total_w / 2
    color_y = y + 6
    color_spacing = 120
    color_row_w = color_spacing * (len(color_items) - 1) + 108
    color_start = center_x - color_row_w / 2
    for i, (label, color) in enumerate(color_items):
        x = color_start + i * color_spacing
        svg.append(f'<rect x="{x:.1f}" y="{color_y}" width="12" height="12" fill="{color}" opacity="0.7" rx="2"/>')
        svg.append(f'<text x="{x + 16:.1f}" y="{color_y + 10}" fill="#8b949e" font-family="sans-serif" font-size="10">{label}</text>')

    bubble_y = color_y + 22
    bubble_radii = [2, 6, 10]
    bubble_centers = [r for r in bubble_radii]
    bubble_centers[1] = bubble_centers[0] + bubble_radii[0] + 8 + bubble_radii[1]
    bubble_centers[2] = bubble_centers[1] + bubble_radii[1] + 10 + bubble_radii[2]
    bubble_label = "checks at that score"
    bubble_label_x = bubble_centers[2] + bubble_radii[2] + 12
    approx_char_w = 5.8
    bubble_row_w = bubble_label_x + len(bubble_label) * approx_char_w
    bubble_start = center_x - bubble_row_w / 2
    for cx, r in zip(bubble_centers, bubble_radii):
        svg.append(f'<circle cx="{bubble_start + cx:.1f}" cy="{bubble_y + 6}" r="{r}" fill="#8b949e" opacity="0.9"/>')
    svg.append(f'<text x="{bubble_start + bubble_label_x:.1f}" y="{bubble_y + 10}" fill="#8b949e" font-family="sans-serif" font-size="10">{bubble_label}</text>')

    svg.append("</svg>")
    content = "\n".join(svg)
    ET.fromstring(content)  # validate XML before writing
    out_path.write_text(content)
    print(f"  ✓ {out_path.relative_to(ROOT)}")


def _variance_n(variance_data: dict[str, dict]) -> str:
    """Extract the run count from variance data for the legend label."""
    for info in variance_data.values():
        n = info.get("num_runs")
        if n:
            return str(n)
    return "?"


def _wrap_label(name: str, max_chars: int = 22) -> list[str]:
    """Wrap long scenario labels onto multiple lines at hyphen boundaries."""
    if len(name) <= max_chars:
        return [name]
    parts = name.split("-")
    lines: list[str] = []
    current = parts[0]
    for part in parts[1:]:
        candidate = f"{current}-{part}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            lines.append(current)
            current = part
    lines.append(current)
    return lines


def _variance_row(
    svg: list[str], y: float, label_w: float, tier_label_w: float,
    axis_w: float, row_h: float, tier: str, rates: list[float],
    c_pass: str, c_flaky: str, c_fail: str,
) -> None:
    """Draw a bubble distribution row for per-check pass rates."""
    ax_left = label_w + tier_label_w
    cy = y + row_h / 2

    # Tier label
    svg.append(f'<text x="{label_w + tier_label_w - 4}" y="{cy + 4}" text-anchor="end" fill="#484f58" font-family="sans-serif" font-size="9">{tier}</text>')

    # Baseline
    is_soft = tier == "soft"
    baseline_opacity = 0.55 if is_soft else 1.0
    bubble_opacity = 0.5 if is_soft else 0.85
    baseline_width = 1 if is_soft else 2
    svg.append(f'<line x1="{ax_left}" y1="{cy}" x2="{ax_left + axis_w}" y2="{cy}" stroke="#30363d" stroke-width="{baseline_width}" opacity="{baseline_opacity}"/>')

    if not rates:
        empty_label = f"no {tier} checks"
        bg_w = max(88, len(empty_label) * 6.2)
        bg_h = 14
        bg_x = ax_left + axis_w / 2 - bg_w / 2
        bg_y = cy - bg_h / 2
        svg.append(f'<rect x="{bg_x:.1f}" y="{bg_y:.1f}" width="{bg_w:.1f}" height="{bg_h:.1f}" fill="#0d1117" rx="3"/>')
        svg.append(f'<text x="{ax_left + axis_w / 2:.1f}" y="{cy:.1f}" text-anchor="middle" dominant-baseline="middle" fill="#484f58" font-family="sans-serif" font-size="10" font-style="italic">{empty_label}</text>')
        return

    mean_r = sum(rates) / len(rates)
    counts = Counter(rates)
    total_count = len(rates)
    max_diameter = row_h
    min_diameter = max(4.0, row_h / 5.0)

    for rate, count in sorted(counts.items()):
        if rate >= 0.9:
            fill = c_pass
        elif rate >= 0.7:
            fill = c_flaky
        else:
            fill = c_fail
        diameter = max_diameter * (count / total_count)
        diameter = max(min_diameter, diameter)
        radius = diameter / 2
        x = ax_left + rate * axis_w
        x = max(ax_left + radius, min(ax_left + axis_w - radius, x))
        svg.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{radius:.1f}" fill="{fill}" opacity="{bubble_opacity}"/>')

    # Mean % label
    svg.append(f'<text x="{ax_left + axis_w + 8}" y="{cy + 4}" fill="#8b949e" font-family="monospace" font-size="10">{mean_r * 100:.0f}%</text>')


# -- Before/After Check Bar Chart (SVG) --------------------------------------

def score_original_file(original_text: str, checks: list[dict]) -> list[float]:
    """Score the original fixture file against the same checks used for the after state.

    Uses simple heuristics based on check names to estimate before-state scores.
    """
    text_lower = original_text.lower()
    scores = []
    for c in checks:
        name = c["name"].lower()
        if "created agents.md" in name:
            # File exists in both states
            scores.append(1.0)
        elif "did not modify" in name:
            # Unchanged fixture — pass in both states
            scores.append(1.0)
        elif "includes command:" in name:
            # Extract command after the colon, check if any variant is in original
            cmd_part = c["name"].split(":", 1)[1].strip()
            variants = [v.strip().lower() for v in cmd_part.split("|")]
            scores.append(1.0 if any(v in text_lower for v in variants) else 0.0)
        elif "does not prescribe command:" in name:
            cmd_part = c["name"].split(":", 1)[1].strip().lower()
            scores.append(0.0 if cmd_part in text_lower else 1.0)
        elif "referenced path:" in name:
            path_part = c["name"].split(":", 1)[1].strip().lower()
            scores.append(1.0 if path_part in text_lower else 0.0)
        elif "did not use forbidden phrase:" in name:
            phrase = c["name"].split(":", 1)[1].strip().lower()
            scores.append(0.0 if phrase in text_lower else 1.0)
        elif "included required phrase:" in name:
            phrase = c["name"].split(":", 1)[1].strip().lower()
            scores.append(1.0 if phrase in text_lower else 0.0)
        elif "reported repo_tier" in name:
            scores.append(0.0)  # Original file doesn't report tier
        elif "fenced code blocks" in name:
            scores.append(1.0 if "```" in original_text else 0.0)
        elif "rubric scores" in name or "audit" in name.lower():
            scores.append(0.0)  # Original doesn't have rubric output
        elif "flagged" in name:
            scores.append(0.0)  # Original doesn't flag anything
        elif "assessed" in name:
            scores.append(0.0)  # Original doesn't assess
        else:
            # Default: assume the original weak file fails unknown checks.
            # The fallback heuristic of matching individual words is too noisy.
            scores.append(0.0)
    return scores


def _is_noise_check(name: str) -> bool:
    """Return True for checks that aren't useful in a before/after comparison.

    Filters: negative checks (pass by absence), meta checks (file exists),
    and output-format checks (rubric section present).
    """
    low = name.lower()
    return (
        "does not prescribe" in low
        or "did not use forbidden" in low
        or "did not modify" in low
        or "did not invent" in low
        or "created agents.md" in low
        or "reported repo_tier" in low
        or "rubric scores" in low
    )


def generate_checks_svg(
    checks_json_path: Path,
    out_path: Path,
    original_file: Path | None = None,
    title: str = "Check Results",
) -> None:
    """Render a before/after stacked bar chart from checks.json."""
    data = json.loads(checks_json_path.read_text())
    checks = [c for c in data["checks"] if not _is_noise_check(c["name"])]

    n = len(checks)
    if n == 0:
        return

    # Count after-state results
    after_pass = sum(1 for c in checks if c["status"] == "pass")
    after_soft = sum(1 for c in checks if c["status"] == "soft_fail")
    after_fail = n - after_pass - after_soft

    # Count before-state results
    has_before = False
    before_pass = before_soft = before_fail = 0
    if original_file and original_file.exists():
        before_scores = score_original_file(original_file.read_text(), checks)
        has_before = True
        before_pass = sum(1 for v in before_scores if v == 1.0)
        before_soft = sum(1 for v in before_scores if v == 0.5)
        before_fail = n - before_pass - before_soft

    # Layout
    bar_w = 340
    bar_h = 32
    label_w = 60
    left_margin = 20
    row_gap = 12
    title_h = 50
    legend_h = 40
    total_w = left_margin + label_w + bar_w + 60
    total_h = title_h + 2 * (bar_h + row_gap) + legend_h + 10

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" width="{total_w}" height="{total_h}">',
        f'<rect width="100%" height="100%" fill="#0d1117" rx="8"/>',
        f'<text x="{total_w // 2}" y="22" text-anchor="middle" fill="#58a6ff" font-family="sans-serif" font-size="14" font-weight="bold">{html.escape(title)}</text>',
        f'<text x="{total_w // 2}" y="38" text-anchor="middle" fill="#484f58" font-family="sans-serif" font-size="11">{n} checks (positive assertions only)</text>',
    ]

    def _stacked_bar(y: float, label: str, n_pass: int, n_soft: int, n_fail: int) -> None:
        x = left_margin + label_w
        svg.append(f'<text x="{x - 8}" y="{y + bar_h * 0.68}" text-anchor="end" fill="#8b949e" font-family="sans-serif" font-size="12">{label}</text>')
        # Background track
        svg.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="#161b22" rx="4"/>')
        # Segments
        segments = [
            (n_pass, "#56d364"),
            (n_soft, "#e3b341"),
            (n_fail, "#f85149"),
        ]
        sx = x
        for count, color in segments:
            if count == 0:
                continue
            w = (count / n) * bar_w
            svg.append(f'<rect x="{sx:.1f}" y="{y}" width="{w:.1f}" height="{bar_h}" fill="{color}" opacity="0.85" rx="0"/>')
            # Label inside segment if wide enough
            if w > 24:
                svg.append(f'<text x="{sx + w / 2:.1f}" y="{y + bar_h * 0.68}" text-anchor="middle" fill="#0d1117" font-family="sans-serif" font-size="11" font-weight="bold">{count}</text>')
            sx += w
        # Round the corners of the composite bar
        svg.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" fill="none" stroke="#0d1117" stroke-width="1" rx="4"/>')
        # Total label
        pct = n_pass / n * 100
        svg.append(f'<text x="{x + bar_w + 8}" y="{y + bar_h * 0.68}" fill="#8b949e" font-family="monospace" font-size="11">{pct:.0f}%</text>')

    y = title_h
    if has_before:
        _stacked_bar(y, "Before", before_pass, before_soft, before_fail)
        y += bar_h + row_gap
    else:
        # No original file — show placeholder
        x = left_margin + label_w
        svg.append(f'<text x="{x - 8}" y="{y + bar_h * 0.68}" text-anchor="end" fill="#8b949e" font-family="sans-serif" font-size="12">Before</text>')
        svg.append(f'<text x="{x + 8}" y="{y + bar_h * 0.68}" fill="#484f58" font-family="sans-serif" font-size="11" font-style="italic">No original file (created from scratch)</text>')
        y += bar_h + row_gap
    _stacked_bar(y, "After", after_pass, after_soft, after_fail)
    y += bar_h + row_gap

    # Legend
    ly = y + 6
    lx = left_margin + label_w
    for label, color in [("Pass", "#56d364"), ("Soft fail", "#e3b341"), ("Hard fail", "#f85149")]:
        svg.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" fill="{color}" opacity="0.85" rx="2"/>')
        svg.append(f'<text x="{lx + 16}" y="{ly + 10}" fill="#8b949e" font-family="sans-serif" font-size="10">{label}</text>')
        lx += 80

    svg.append("</svg>")
    content = "\n".join(svg)
    ET.fromstring(content)  # validate XML before writing
    out_path.write_text(content)
    print(f"  ✓ {out_path.relative_to(ROOT)}")


# -- Audit Output (SVG) -------------------------------------------------------

def _wrap_plain_text(text: str, max_chars: int) -> list[str]:
    if not text:
        return [""]
    words = re.split(r"(\s+)", text)
    lines: list[str] = []
    current = ""
    for token in words:
        if token == "":
            continue
        candidate = current + token
        if not current:
            if len(token) <= max_chars:
                current = token
            else:
                while len(token) > max_chars:
                    lines.append(token[:max_chars])
                    token = token[max_chars:]
                current = token
            continue
        if len(candidate) <= max_chars:
            current = candidate
            continue
        lines.append(current.rstrip())
        token = token.lstrip()
        if len(token) <= max_chars:
            current = token
            continue
        while len(token) > max_chars:
            lines.append(token[:max_chars])
            token = token[max_chars:]
        current = token
    if current or not lines:
        lines.append(current.rstrip())
    return lines


def _clean_audit_text(text: str) -> str:
    """Strip markdown-only noise while keeping the human-readable content."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _chars_for_width(width_px: int, size: int) -> int:
    """Estimate monospaced character capacity for a given pixel width."""
    char_px = max(6, int(round(size * 0.62)))
    return max(8, width_px // char_px)


def _wrap_hanging_text(text: str, first_width: int, rest_width: int) -> list[str]:
    """Wrap text with a smaller first line width and a hanging indent width after."""
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = ""
    width = first_width
    idx = 0
    while idx < len(words):
        word = words[idx]
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
            idx += 1
            continue
        if current:
            lines.append(current)
            current = ""
            width = rest_width
            continue
        # Single very long token: hard-wrap it.
        lines.append(word[:width])
        words[idx] = word[width:]
        width = rest_width
    if current:
        lines.append(current)
    return lines


def _svg_text_lines(
    svg: list[str], x: int, y: int, lines: list[str], *, fill: str, size: int, weight: str = "400", line_height: int | None = None
) -> int:
    lh = line_height or (size + 7)
    for idx, line in enumerate(lines):
        yy = y + idx * lh
        svg.append(
            f'<text x="{x}" y="{yy}" fill="{fill}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{size}" font-weight="{weight}">{html.escape(line)}</text>'
        )
    return y + len(lines) * lh


def _render_wrapped_block(
    svg: list[str],
    *,
    x: int,
    y: int,
    text: str,
    max_width: int,
    fill: str,
    size: int,
    line_height: int,
    weight: str = "400",
    indent_px: int = 0,
    prefix: str = "",
    block_gap: int = 6,
) -> int:
    """Render one wrapped paragraph or list item with optional hanging indent."""
    base_x = x + indent_px
    prefix_px = 0
    if prefix:
        prefix_px = max(10, int(round(len(prefix) * size * 0.62)))
        first_width = _chars_for_width(max_width - indent_px - prefix_px, size)
        rest_width = _chars_for_width(max_width - indent_px - prefix_px, size)
        wrapped = _wrap_hanging_text(text, first_width, rest_width)
        if wrapped:
            y = _svg_text_lines(svg, base_x, y, [f"{prefix}{wrapped[0]}"], fill=fill, size=size, weight=weight, line_height=line_height)
            if len(wrapped) > 1:
                y = _svg_text_lines(
                    svg,
                    base_x + prefix_px,
                    y,
                    wrapped[1:],
                    fill=fill,
                    size=size,
                    weight=weight,
                    line_height=line_height,
                )
        return y + block_gap

    wrapped = _wrap_plain_text(text, _chars_for_width(max_width - indent_px, size))
    y = _svg_text_lines(svg, base_x, y, wrapped, fill=fill, size=size, weight=weight, line_height=line_height)
    return y + block_gap


def generate_audit_svg(output_md_path: Path, out_path: Path) -> None:
    text = output_md_path.read_text(encoding="utf-8")
    width = 920
    x0 = 28
    content_w = width - x0 * 2
    y = 34
    table_rows: list[list[str]] = []
    in_table = False
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="1000" viewBox="0 0 {width} 1000" role="img" aria-labelledby="title desc">',
        '<title id="title">Audit Output</title>',
        '<desc id="desc">Styled audit output from a real eval run.</desc>',
        f'<rect width="{width}" height="1000" fill="#0d1117" rx="10"/>',
    ]

    def close_table() -> None:
        nonlocal y, in_table, table_rows
        if not in_table or not table_rows:
            in_table = False
            table_rows = []
            return
        col_x = [x0, x0 + 210, x0 + 360]
        col_w = [190, 130, content_w - 340]
        row_heights: list[int] = []
        wrapped_rows: list[list[list[str]]] = []
        for r_idx, row in enumerate(table_rows):
            wrapped_cells: list[list[str]] = []
            max_lines = 1
            for c_idx, cell in enumerate(row[:3]):
                clean = _clean_audit_text(cell)
                wrapped = _wrap_plain_text(clean, max(12, int(col_w[c_idx] / 8.8)))
                wrapped_cells.append(wrapped)
                max_lines = max(max_lines, min(3, len(wrapped)))
            wrapped_rows.append(wrapped_cells)
            row_heights.append(24 if r_idx == 0 else 10 + max_lines * 13)
        table_height = sum(row_heights)
        svg.append(f'<rect x="{x0}" y="{y}" width="{content_w}" height="{table_height}" fill="#161b22" stroke="#30363d" rx="6"/>')
        yy = y
        for r_idx, row in enumerate(table_rows):
            this_h = row_heights[r_idx]
            if r_idx == 0:
                svg.append(f'<rect x="{x0}" y="{yy}" width="{content_w}" height="{this_h}" fill="#1f2937" rx="6"/>')
            else:
                svg.append(f'<line x1="{x0}" y1="{yy}" x2="{x0 + content_w}" y2="{yy}" stroke="#30363d"/>')
            for c_idx, cell in enumerate(row[:3]):
                color = "#8b949e" if r_idx == 0 else "#c9d1d9"
                low = cell.lower()
                if r_idx > 0 and low in {"pass", "weak", "missing", "unverified"}:
                    color = {"pass": "#56d364", "weak": "#e3b341", "missing": "#f85149", "unverified": "#8b949e"}[low]
                wrapped = wrapped_rows[r_idx][c_idx]
                for w_idx, line in enumerate(wrapped[:3]):
                    svg.append(
                        f'<text x="{col_x[c_idx] + 10}" y="{yy + 15 + w_idx * 12}" fill="{color}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="11">{html.escape(line)}</text>'
                    )
            yy += this_h
        y += table_height + 20
        in_table = False
        table_rows = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("| ") and "---" not in line:
            if not in_table:
                in_table = True
            table_rows.append([c.strip() for c in line.split("|")[1:-1]])
            continue
        if line.startswith("|") and "---" in line:
            continue
        close_table()
        if line.startswith("## "):
            wrapped = _wrap_plain_text(_clean_audit_text(line[3:]), 48)
            y = _svg_text_lines(svg, x0, y, wrapped, fill="#58a6ff", size=20, weight="700", line_height=26) + 8
            continue
        if line.startswith("### "):
            wrapped = _wrap_plain_text(_clean_audit_text(line[4:]), 70)
            y = _svg_text_lines(svg, x0, y, wrapped, fill="#8b949e", size=15, weight="700", line_height=20) + 6
            continue
        if not line:
            y += 10
            continue
        bullet_match = re.match(r"^(\s*)([-*])\s+(.*)$", line)
        ordered_match = re.match(r"^(\s*)(\d+\.)\s+(.*)$", line)
        if bullet_match:
            indent_spaces, _, body = bullet_match.groups()
            y = _render_wrapped_block(
                svg,
                x=x0,
                y=y,
                text=_clean_audit_text(body),
                max_width=content_w,
                fill="#c9d1d9",
                size=13,
                line_height=20,
                indent_px=len(indent_spaces) * 8 + 12,
                prefix="• ",
                block_gap=4,
            )
            continue
        if ordered_match:
            indent_spaces, marker, body = ordered_match.groups()
            y = _render_wrapped_block(
                svg,
                x=x0,
                y=y,
                text=_clean_audit_text(body),
                max_width=content_w,
                fill="#c9d1d9",
                size=13,
                line_height=20,
                indent_px=len(indent_spaces) * 8 + 12,
                prefix=f"{marker} ",
                block_gap=4,
            )
            continue
        y = _render_wrapped_block(
            svg,
            x=x0,
            y=y,
            text=_clean_audit_text(line),
            max_width=content_w,
            fill="#c9d1d9",
            size=13,
            line_height=20,
            block_gap=6,
        )

    close_table()
    final_h = max(180, y + 22)
    svg[3] = f'<rect width="{width}" height="{final_h}" fill="#0d1117" rx="10"/>'
    svg[0] = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{final_h}" viewBox="0 0 {width} {final_h}" role="img" aria-labelledby="title desc">'
    svg.append("</svg>")
    content = "\n".join(svg)
    ET.fromstring(content)
    out_path.write_text(content, encoding="utf-8")
    print(f"  ✓ {out_path.relative_to(ROOT)}")


# -- Main ---------------------------------------------------------------------

def generate_all(run_dir: Path | None = None) -> None:
    """Public entry point — callable from run_eval.py or standalone.

    If run_dir is provided, uses that run for radar/diff/audit assets.
    Otherwise searches all runs for the best result per scenario.
    """
    ASSETS.mkdir(exist_ok=True)

    scenarios = sorted(
        name for name in current_scenarios()
        if (FIXTURES / name).is_dir()
    )

    print(f"\nGenerating assets for {len(scenarios)} fixtures...")

    # Stability bar chart (repo-wide, lives at top level)
    generate_stability_svg(ASSETS / "stability-bars.svg")

    # Per-scenario assets: assets/<scenario>/{checks,diff,audit}
    for scenario in scenarios:
        if run_dir:
            checks_json = _pick_median_checks_json(run_dir / scenario)
            if not checks_json:
                continue
            effective_run = run_dir
        else:
            result = find_best_run_for_scenario(scenario)
            if not result:
                print(f"  ⚠ {scenario}: no eval run found, skipping")
                continue
            checks_json, effective_run = result

        prefix = _prefix_from_checks_json(checks_json)
        scenario_dir = ASSETS / scenario
        scenario_dir.mkdir(exist_ok=True)

        # Before/after check bar chart
        original_agents = FIXTURES / scenario / "AGENTS.md"
        generate_checks_svg(
            checks_json,
            scenario_dir / "checks.svg",
            original_file=original_agents if original_agents.exists() else None,
            title=scenario,
        )

        # Diff (uses original AGENTS.md when present, otherwise an empty baseline)
        before = FIXTURES / scenario / "AGENTS.md"
        after = find_generated_agents(effective_run, scenario, prefix=prefix)
        if after:
            generate_diff_svg(before if before.exists() else None, after, scenario_dir / "diff.svg", scenario=scenario)

        # Audit output
        output_md = find_output_md(effective_run, scenario, prefix=prefix)
        if output_md:
            generate_audit_svg(output_md, scenario_dir / "audit.svg")

    print("Assets done.\n")


def _pass_count(checks_path: Path) -> int:
    """Count passing checks in a checks.json file."""
    try:
        data = json.loads(checks_path.read_text())
        return sum(1 for c in data.get("checks", []) if c["status"] == "pass")
    except (json.JSONDecodeError, OSError, KeyError):
        return 0


def _pick_median_checks_json(scenario_dir: Path) -> Path | None:
    """Pick the checks.json with the median pass count (typical run)."""
    if not scenario_dir.exists():
        return None
    candidates = sorted(f for f in scenario_dir.iterdir() if f.name.endswith(".checks.json"))
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    ranked = sorted(candidates, key=_pass_count)
    return ranked[len(ranked) // 2]


def find_best_run_for_scenario(scenario: str) -> tuple[Path, Path] | None:
    """Find the median checks.json for the latest run that contains a scenario.

    Within the latest run directory for that scenario, picks the median
    run by pass count (the typical result).
    Returns (checks_json_path, run_dir) or None.
    """
    runs_dir = ROOT / "tests" / "eval" / "runs"
    if not runs_dir.exists():
        return None
    # Find the latest run_dir with this scenario
    best_run: tuple[str, Path] | None = None  # (timestamp, run_dir)
    for run_dir in sorted(runs_dir.iterdir()):
        scenario_dir = run_dir / scenario
        if not scenario_dir.exists():
            continue
        candidate = (run_dir.name, run_dir)
        if best_run is None or candidate[0] > best_run[0]:
            best_run = candidate
    if not best_run:
        return None
    run_dir = best_run[1]
    checks_json = _pick_median_checks_json(run_dir / scenario)
    return (checks_json, run_dir) if checks_json else None


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, help="Eval run directory (default: search all runs per scenario)")
    args = parser.parse_args()

    generate_all(run_dir=args.run_dir)


if __name__ == "__main__":
    main()
