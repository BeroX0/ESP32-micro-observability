#!/usr/bin/env python3
import csv
from pathlib import Path
from statistics import mean

ROOT = Path(".")
PROCESSED = ROOT / "experiments" / "processed" / "validation-a-vs-b"
OUT = ROOT / "analysis" / "results"

OUT.mkdir(parents=True, exist_ok=True)

CSV_FILES = [
    PROCESSED / "normal-scenario-serial-summary.csv",
    PROCESSED / "wifi-loss-scenario-serial-summary.csv",
    PROCESSED / "slow-backend-scenario-serial-summary.csv",
    PROCESSED / "backend-down-scenario-serial-summary.csv",
]

def to_int(value):
    if value is None or value == "":
        return None
    return int(value)

def ratio(numerator, denominator):
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator

def fmt(value):
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)

rows = []

for csv_file in CSV_FILES:
    with csv_file.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tick_count = to_int(row.get("tick_count"))
            wifi_up_count = to_int(row.get("wifi_up_count"))
            wifi_down_count = to_int(row.get("wifi_down_count"))
            full_live_count = to_int(row.get("full_live_count"))
            stale_count = to_int(row.get("stale_count"))
            fail_count = to_int(row.get("fail_count"))
            gateway_live_count = to_int(row.get("gateway_live_count"))
            gateway_stale_count = to_int(row.get("gateway_stale_count"))

            combined = {
                "run_id": row.get("run_id", ""),
                "scenario": row.get("scenario", ""),
                "design": row.get("design", ""),
                "repetition": row.get("repetition", ""),
                "tick_count": tick_count,
                "wifi_up_count": wifi_up_count,
                "wifi_down_count": wifi_down_count,
                "full_live_count": full_live_count,
                "stale_count": stale_count,
                "fail_count": fail_count,
                "gateway_live_count": gateway_live_count,
                "gateway_stale_count": gateway_stale_count,
                "recovered_live_tail": row.get("recovered_live_tail", ""),
                "live_ratio": ratio(full_live_count, tick_count),
                "wifi_up_ratio": ratio(wifi_up_count, tick_count),
                "wifi_down_ratio": ratio(wifi_down_count, tick_count),
                "stale_ratio": ratio(stale_count, tick_count),
                "fail_ratio": ratio(fail_count, tick_count),
                "gateway_live_ratio": ratio(gateway_live_count, tick_count),
                "gateway_stale_ratio": ratio(gateway_stale_count, tick_count),
            }
            rows.append(combined)

combined_fields = [
    "run_id",
    "scenario",
    "design",
    "repetition",
    "tick_count",
    "wifi_up_count",
    "wifi_down_count",
    "full_live_count",
    "stale_count",
    "fail_count",
    "gateway_live_count",
    "gateway_stale_count",
    "recovered_live_tail",
    "live_ratio",
    "wifi_up_ratio",
    "wifi_down_ratio",
    "stale_ratio",
    "fail_ratio",
    "gateway_live_ratio",
    "gateway_stale_ratio",
]

combined_csv = OUT / "final-kpi-combined-runs.csv"
with combined_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=combined_fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: fmt(row.get(k)) for k in combined_fields})

def group_rows(keys):
    groups = {}
    for row in rows:
        key = tuple(row[k] for k in keys)
        groups.setdefault(key, []).append(row)
    return groups

summary_fields = [
    "scenario",
    "design",
    "runs",
    "mean_tick_count",
    "mean_wifi_up_count",
    "mean_wifi_down_count",
    "mean_full_live_count",
    "mean_stale_count",
    "mean_fail_count",
    "mean_gateway_live_count",
    "mean_gateway_stale_count",
    "mean_live_ratio",
    "mean_wifi_up_ratio",
    "mean_wifi_down_ratio",
    "mean_stale_ratio",
    "mean_fail_ratio",
    "mean_gateway_live_ratio",
    "mean_gateway_stale_ratio",
    "all_recovered_live_tail",
]

def mean_existing(group, field):
    values = [r[field] for r in group if r.get(field) is not None]
    if not values:
        return None
    return mean(values)

design_summaries = []
for (scenario, design), group in sorted(group_rows(["scenario", "design"]).items()):
    recovered_values = [r.get("recovered_live_tail") for r in group if r.get("recovered_live_tail") != ""]
    all_recovered = ""
    if recovered_values:
        all_recovered = str(all(v == "True" for v in recovered_values))

    design_summaries.append({
        "scenario": scenario,
        "design": design,
        "runs": len(group),
        "mean_tick_count": mean_existing(group, "tick_count"),
        "mean_wifi_up_count": mean_existing(group, "wifi_up_count"),
        "mean_wifi_down_count": mean_existing(group, "wifi_down_count"),
        "mean_full_live_count": mean_existing(group, "full_live_count"),
        "mean_stale_count": mean_existing(group, "stale_count"),
        "mean_fail_count": mean_existing(group, "fail_count"),
        "mean_gateway_live_count": mean_existing(group, "gateway_live_count"),
        "mean_gateway_stale_count": mean_existing(group, "gateway_stale_count"),
        "mean_live_ratio": mean_existing(group, "live_ratio"),
        "mean_wifi_up_ratio": mean_existing(group, "wifi_up_ratio"),
        "mean_wifi_down_ratio": mean_existing(group, "wifi_down_ratio"),
        "mean_stale_ratio": mean_existing(group, "stale_ratio"),
        "mean_fail_ratio": mean_existing(group, "fail_ratio"),
        "mean_gateway_live_ratio": mean_existing(group, "gateway_live_ratio"),
        "mean_gateway_stale_ratio": mean_existing(group, "gateway_stale_ratio"),
        "all_recovered_live_tail": all_recovered,
    })

summary_csv = OUT / "final-kpi-design-scenario-summary.csv"
with summary_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=summary_fields)
    writer.writeheader()
    for row in design_summaries:
        writer.writerow({k: fmt(row.get(k)) for k in summary_fields})

matrix_md = OUT / "validation-scenario-matrix.md"
matrix_md.write_text("""# Validation scenario matrix

| Scenario | Design A repetitions | Design B repetitions | Total accepted runs | Main fault injected | Evidence source |
|---|---:|---:|---:|---|---|
| Normal operation | 3 | 3 | 6 | None | Serial logs and processed CSV |
| Wi-Fi loss | 3 | 3 | 6 | ESP32 connectivity interrupted and restored | Serial logs, operator events, processed CSV |
| Slow backend | 3 | 3 | 6 | 2000 ms proxy delay in front of Prometheus | Serial logs, delay-proxy method note, processed CSV |
| Backend down | 3 | 3 | 6 | Prometheus stopped and restarted | Serial logs, operator events, processed CSV |
| **Total** | **12** | **12** | **24** | Four validation scenarios | Frozen validation evidence |
""", encoding="utf-8")

def md_table(headers, data_rows):
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in data_rows:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)

scenario_tables = []

for scenario in ["normal", "wifi-loss", "slow-backend", "backend-down"]:
    scenario_tables.append(f"## {scenario}\n")
    subset = [r for r in design_summaries if r["scenario"] == scenario]

    headers = [
        "Design",
        "Runs",
        "Mean tick count",
        "Mean live ratio",
        "Mean Wi-Fi down count",
        "Mean stale count",
        "Mean fail count",
        "Mean gateway stale count",
        "Recovered live tail",
    ]

    data = []
    for r in subset:
        data.append([
            r["design"],
            fmt(r["runs"]),
            fmt(r["mean_tick_count"]),
            fmt(r["mean_live_ratio"]),
            fmt(r["mean_wifi_down_count"]),
            fmt(r["mean_stale_count"]),
            fmt(r["mean_fail_count"]),
            fmt(r["mean_gateway_stale_count"]),
            fmt(r["all_recovered_live_tail"]),
        ])

    scenario_tables.append(md_table(headers, data))
    scenario_tables.append("")

scenario_md = OUT / "final-kpi-scenario-summary-tables.md"
scenario_md.write_text("# Final KPI scenario summary tables\n\n" + "\n\n".join(scenario_tables), encoding="utf-8")

cross_md = OUT / "cross-scenario-observation-table.md"
cross_md.write_text("""# Cross-scenario A-vs-B observation table

| Dimension | Design A result | Design B result | Evidence-based observation |
|---|---|---|---|
| Normal operation | Maintained live metric output in accepted runs | Maintained live metric output through gateway in accepted runs | Both designs were viable under healthy baseline conditions |
| Wi-Fi loss | Showed FAIL periods during outage but recovered after reconnect fix | Showed STALE periods and zero FAIL in accepted runs | Design B provided more graceful degraded-state semantics during Wi-Fi loss |
| Slow backend | Stayed LIVE under the selected delay-proxy method and adjusted timeout | Often showed STALE, with one short FAIL pocket, then recovered | Slow-backend result is configuration-sensitive and must be discussed carefully |
| Backend down | Entered FAIL during Prometheus outage and recovered after restart | Stayed mainly STALE with zero FAIL and recovered to live | Strongest evidence for gateway-mediated degraded usefulness |
| Endpoint responsibility | ESP32 handles direct backend queries | ESP32 consumes one compact gateway summary endpoint | Design B simplifies the endpoint at the cost of an extra gateway component |
| Least privilege | Backend-facing access is closer to the device | Backend-facing access can be centralized in the gateway | Design B gives a cleaner least-privilege boundary in this proof-of-concept |
""", encoding="utf-8")

readme = OUT / "README.md"
readme.write_text("""# Final results aggregation

This folder contains thesis-ready aggregation products derived from the frozen A-vs-B validation evidence.

Source inputs:
- experiments/processed/validation-a-vs-b/normal-scenario-serial-summary.csv
- experiments/processed/validation-a-vs-b/wifi-loss-scenario-serial-summary.csv
- experiments/processed/validation-a-vs-b/slow-backend-scenario-serial-summary.csv
- experiments/processed/validation-a-vs-b/backend-down-scenario-serial-summary.csv

Generated outputs:
- final-kpi-combined-runs.csv
- final-kpi-design-scenario-summary.csv
- validation-scenario-matrix.md
- final-kpi-scenario-summary-tables.md
- cross-scenario-observation-table.md

The aggregation uses simple descriptive measures only:
- counts
- means
- ratios
- recovered-live-tail boolean summaries

No raw evidence is modified by this aggregation step.
""", encoding="utf-8")

print("Generated:")
for p in [
    combined_csv,
    summary_csv,
    matrix_md,
    scenario_md,
    cross_md,
    readme,
]:
    print(f"- {p}")
