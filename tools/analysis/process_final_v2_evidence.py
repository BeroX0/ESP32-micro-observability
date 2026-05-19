#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "experiments" / "raw"
OUT_DIR = ROOT / "experiments" / "processed" / "final-v2"
ANALYSIS_DIR = ROOT / "analysis" / "results"

RUN_RE = re.compile(
    r"^RUN-20260518-final-v2-"
    r"(?P<scenario>normal|wifi-loss|slow-backend|backend-down)-"
    r"(?P<design>design-a|design-b)-"
    r"r(?P<rep>[1-5])$"
)

TICK_RE = re.compile(r"^tick=(?P<tick>\d+)\b")
CAPTURE_START_RE = re.compile(r"CAPTURE_START (?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")
CAPTURE_END_RE = re.compile(r"CAPTURE_END (?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})")


@dataclass
class RunSummary:
    run_id: str
    scenario: str
    design: str
    repetition: int
    accepted: bool
    line_count: int
    sample_count: int
    capture_start: str
    capture_end: str
    duration_seconds: int | None
    first_tick: int | None
    last_tick: int | None
    wifi_up_lines: int
    wifi_down_lines: int
    gw_live_lines: int
    gw_stale_lines: int
    gw_fail_lines: int
    live_labels: int
    stale_labels: int
    fail_labels: int
    has_hotspot_off: bool
    has_hotspot_on: bool
    has_delay_2000: bool
    has_delay_0: bool
    has_prometheus_stop: bool
    has_prometheus_start: bool
    reset_markers: int


def read_text(path: Path) -> str:
    data = path.read_bytes()

    candidates = []
    for enc in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "latin-1"):
        try:
            decoded = data.decode(enc, errors="replace").lstrip("\ufeff")
            candidates.append(decoded)
        except Exception:
            pass

    # Prefer the decoding that actually exposes serial samples.
    tick_candidates = [(decoded.count("tick="), decoded) for decoded in candidates]
    tick_candidates.sort(key=lambda item: item[0], reverse=True)

    if tick_candidates and tick_candidates[0][0] > 0:
        return tick_candidates[0][1]

    if candidates:
        return candidates[0]

    return data.decode("utf-8", errors="replace").lstrip("\ufeff")

def parse_ts(pattern: re.Pattern[str], text: str) -> str:
    m = pattern.search(text)
    return m.group("ts") if m else ""


def parse_duration(start: str, end: str) -> int | None:
    if not start or not end:
        return None
    try:
        a = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        b = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        return int((b - a).total_seconds())
    except ValueError:
        return None


def analyze_run(run_dir: Path) -> RunSummary:
    run_id = run_dir.name
    m = RUN_RE.match(run_id)
    if not m:
        raise ValueError(f"Unexpected run directory name: {run_id}")

    scenario = m.group("scenario")
    design = m.group("design")
    repetition = int(m.group("rep"))

    serial_path = run_dir / "serial.log"
    note_path = run_dir / "run-note.md"

    serial = read_text(serial_path)
    note = read_text(note_path)

    lines = [line.rstrip("\n\r") for line in serial.splitlines()]
    tick_lines = [line for line in lines if line.startswith("tick=")]

    ticks: list[int] = []
    for line in tick_lines:
        tm = TICK_RE.search(line)
        if tm:
            ticks.append(int(tm.group("tick")))

    capture_start = parse_ts(CAPTURE_START_RE, serial)
    capture_end = parse_ts(CAPTURE_END_RE, serial)
    duration_seconds = parse_duration(capture_start, capture_end)

    text_upper = serial.upper()

    return RunSummary(
        run_id=run_id,
        scenario=scenario,
        design=design,
        repetition=repetition,
        accepted=("ACCEPTED" in note),
        line_count=len(lines),
        sample_count=len(tick_lines),
        capture_start=capture_start,
        capture_end=capture_end,
        duration_seconds=duration_seconds,
        first_tick=min(ticks) if ticks else None,
        last_tick=max(ticks) if ticks else None,
        wifi_up_lines=sum("wifi=UP" in line for line in tick_lines),
        wifi_down_lines=sum("wifi=DOWN" in line for line in tick_lines),
        gw_live_lines=sum("gw=live" in line for line in tick_lines),
        gw_stale_lines=sum("gw=stale" in line for line in tick_lines),
        gw_fail_lines=sum("gw=fail" in line for line in tick_lines),
        live_labels=sum(line.count("/LIVE") for line in tick_lines),
        stale_labels=sum(line.count("/STALE") for line in tick_lines),
        fail_labels=sum(line.count("/FAIL") for line in tick_lines),
        has_hotspot_off=("HOTSPOT_OFF_RESULT" in serial or "HOTSPOT_OFF" in serial),
        has_hotspot_on=("HOTSPOT_ON_RESULT" in serial or "HOTSPOT_ON" in serial),
        has_delay_2000=('DELAY_SET_RESULT {"delay_ms": 2000}' in serial or "DELAY_SET_REQUEST ms=2000" in serial),
        has_delay_0=('DELAY_SET_RESULT {"delay_ms": 0}' in serial or "DELAY_SET_REQUEST ms=0" in serial),
        has_prometheus_stop=("PROMETHEUS_STOP_RESULT" in serial),
        has_prometheus_start=("PROMETHEUS_START_RESULT" in serial),
        reset_markers=sum(1 for marker in ["ESP-ROM", "BOOT", "DESIGN_A_V1_BOOT", "DESIGN_B_V1_BOOT"] if marker in text_upper),
    )


def asdict_flat(r: RunSummary) -> dict[str, object]:
    return {
        "run_id": r.run_id,
        "scenario": r.scenario,
        "design": r.design,
        "repetition": r.repetition,
        "accepted": "YES" if r.accepted else "NO",
        "line_count": r.line_count,
        "sample_count": r.sample_count,
        "capture_start": r.capture_start,
        "capture_end": r.capture_end,
        "duration_seconds": r.duration_seconds if r.duration_seconds is not None else "",
        "first_tick": r.first_tick if r.first_tick is not None else "",
        "last_tick": r.last_tick if r.last_tick is not None else "",
        "wifi_up_lines": r.wifi_up_lines,
        "wifi_down_lines": r.wifi_down_lines,
        "gw_live_lines": r.gw_live_lines,
        "gw_stale_lines": r.gw_stale_lines,
        "gw_fail_lines": r.gw_fail_lines,
        "live_labels": r.live_labels,
        "stale_labels": r.stale_labels,
        "fail_labels": r.fail_labels,
        "has_hotspot_off": "YES" if r.has_hotspot_off else "NO",
        "has_hotspot_on": "YES" if r.has_hotspot_on else "NO",
        "has_delay_2000": "YES" if r.has_delay_2000 else "NO",
        "has_delay_0": "YES" if r.has_delay_0 else "NO",
        "has_prometheus_stop": "YES" if r.has_prometheus_stop else "NO",
        "has_prometheus_start": "YES" if r.has_prometheus_start else "NO",
        "reset_markers": r.reset_markers,
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        out.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out)


def main() -> None:
    run_dirs = sorted(p for p in RAW_DIR.iterdir() if p.is_dir() and RUN_RE.match(p.name))
    if len(run_dirs) != 40:
        raise SystemExit(f"Expected 40 final-v2 run directories, found {len(run_dirs)}")

    runs = [analyze_run(p) for p in run_dirs]

    if sum(r.accepted for r in runs) != 40:
        raise SystemExit(f"Expected 40 accepted runs, found {sum(r.accepted for r in runs)}")

    empty_sample_runs = [r.run_id for r in runs if r.sample_count == 0]
    if empty_sample_runs:
        raise SystemExit("Runs with zero parsed serial samples: " + ", ".join(empty_sample_runs))

    missing_live_runs = [r.run_id for r in runs if r.live_labels == 0]
    if missing_live_runs:
        raise SystemExit("Runs with zero LIVE labels: " + ", ".join(missing_live_runs))

    scenario_order = ["normal", "wifi-loss", "slow-backend", "backend-down"]
    design_order = ["design-a", "design-b"]

    runs.sort(key=lambda r: (scenario_order.index(r.scenario), design_order.index(r.design), r.repetition))

    run_rows = [asdict_flat(r) for r in runs]
    write_csv(OUT_DIR / "final-v2-run-summary.csv", run_rows)

    grouped: dict[tuple[str, str], list[RunSummary]] = defaultdict(list)
    for r in runs:
        grouped[(r.scenario, r.design)].append(r)

    scenario_rows: list[dict[str, object]] = []
    status_rows: list[dict[str, object]] = []

    for scenario in scenario_order:
        for design in design_order:
            group = grouped[(scenario, design)]
            durations = [r.duration_seconds for r in group if r.duration_seconds is not None]
            scenario_rows.append({
                "scenario": scenario,
                "design": design,
                "run_count": len(group),
                "accepted_count": sum(r.accepted for r in group),
                "avg_duration_seconds": round(mean(durations), 1) if durations else "",
                "avg_sample_count": round(mean(r.sample_count for r in group), 1),
                "runs_with_live": sum(r.live_labels > 0 for r in group),
                "runs_with_stale": sum(r.stale_labels > 0 for r in group),
                "runs_with_fail": sum(r.fail_labels > 0 for r in group),
                "runs_with_wifi_down": sum(r.wifi_down_lines > 0 for r in group),
                "runs_with_gw_stale": sum(r.gw_stale_lines > 0 for r in group),
                "runs_with_reset_markers": sum(r.reset_markers > 0 for r in group),
            })

            status_rows.append({
                "scenario": scenario,
                "design": design,
                "live_labels": sum(r.live_labels for r in group),
                "stale_labels": sum(r.stale_labels for r in group),
                "fail_labels": sum(r.fail_labels for r in group),
                "wifi_up_lines": sum(r.wifi_up_lines for r in group),
                "wifi_down_lines": sum(r.wifi_down_lines for r in group),
                "gw_live_lines": sum(r.gw_live_lines for r in group),
                "gw_stale_lines": sum(r.gw_stale_lines for r in group),
                "gw_fail_lines": sum(r.gw_fail_lines for r in group),
            })

    write_csv(OUT_DIR / "final-v2-scenario-summary.csv", scenario_rows)
    write_csv(OUT_DIR / "final-v2-status-counts.csv", status_rows)

    acceptance_rows = [
        [scenario, design, grouped[(scenario, design)].__len__(), sum(r.accepted for r in grouped[(scenario, design)])]
        for scenario in scenario_order
        for design in design_order
    ]

    behavior_rows = []
    for scenario in scenario_order:
        for design in design_order:
            group = grouped[(scenario, design)]
            behavior_rows.append([
                scenario,
                design,
                sum(r.live_labels > 0 for r in group),
                sum(r.stale_labels > 0 for r in group),
                sum(r.fail_labels > 0 for r in group),
                sum(r.wifi_down_lines > 0 for r in group),
                sum(r.gw_stale_lines > 0 for r in group),
                sum(r.reset_markers > 0 for r in group),
            ])

    status_count_rows = [
        [
            row["scenario"],
            row["design"],
            row["live_labels"],
            row["stale_labels"],
            row["fail_labels"],
            row["wifi_down_lines"],
            row["gw_stale_lines"],
        ]
        for row in status_rows
    ]

    md = []
    md.append("# Final-v2 validation evidence tables\n")
    md.append("Generated from the committed final-v2 raw serial logs and run notes.\n")
    md.append("## Evidence inventory\n")
    md.append(md_table(
        ["Measure", "Value"],
        [
            ["Total final-v2 runs", len(runs)],
            ["Accepted runs", sum(r.accepted for r in runs)],
            ["Scenarios", ", ".join(scenario_order)],
            ["Designs", ", ".join(design_order)],
            ["Repetitions per scenario/design", 5],
        ],
    ))
    md.append("\n## Table 1. Accepted runs by scenario and design\n")
    md.append(md_table(
        ["Scenario", "Design", "Run count", "Accepted count"],
        acceptance_rows,
    ))
    md.append("\n## Table 2. Observed behavior by scenario and design\n")
    md.append(md_table(
        [
            "Scenario",
            "Design",
            "Runs with LIVE",
            "Runs with STALE",
            "Runs with FAIL",
            "Runs with wifi=DOWN",
            "Runs with gw=stale",
            "Runs with reset markers",
        ],
        behavior_rows,
    ))
    md.append("\n## Table 3. Status label counts by scenario and design\n")
    md.append(md_table(
        [
            "Scenario",
            "Design",
            "LIVE labels",
            "STALE labels",
            "FAIL labels",
            "wifi=DOWN lines",
            "gw=stale lines",
        ],
        status_count_rows,
    ))

    md.append("\n## Interpretation notes for thesis use\n")
    md.append("- Normal runs are expected to contain LIVE values and no injected fault markers.\n")
    md.append("- Wi-Fi-loss runs are expected to contain wifi=DOWN during the outage and recovery to wifi=UP/LIVE.\n")
    md.append("- Slow-backend runs are expected to contain delay-control markers and degraded STALE/FAIL behavior during the delay interval.\n")
    md.append("- Backend-down runs are expected to contain Prometheus stop/start markers and degraded STALE/FAIL behavior while Prometheus is unavailable.\n")
    md.append("- Design B gateway runs are expected to contain gw=live during normal/recovered operation and gw=stale during upstream degradation.\n")
    md.append("- Reset marker counts should remain zero for accepted fault-injection runs unless a deliberate reset was part of the method.\n")

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    (ANALYSIS_DIR / "final-v2-thesis-tables.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("Generated:")
    print(f"- {OUT_DIR / 'final-v2-run-summary.csv'}")
    print(f"- {OUT_DIR / 'final-v2-scenario-summary.csv'}")
    print(f"- {OUT_DIR / 'final-v2-status-counts.csv'}")
    print(f"- {ANALYSIS_DIR / 'final-v2-thesis-tables.md'}")


if __name__ == "__main__":
    main()
