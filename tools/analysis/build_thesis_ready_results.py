#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(".")
RESULTS = ROOT / "analysis" / "results"
OUT = ROOT / "analysis" / "thesis-ready"
OUT.mkdir(parents=True, exist_ok=True)

summary_csv = RESULTS / "final-kpi-design-scenario-summary.csv"

with summary_csv.open(newline="") as f:
    rows = list(csv.DictReader(f))

def get(scenario, design):
    for r in rows:
        if r["scenario"] == scenario and r["design"] == design:
            return r
    raise KeyError((scenario, design))

def val(row, key, empty="N/A"):
    v = row.get(key, "")
    return v if v != "" else empty

def pct(row, key):
    v = row.get(key, "")
    if v == "":
        return "N/A"
    return f"{float(v) * 100:.1f}%"

def md_table(headers, data):
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in data:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)

# Table 1
table1 = """# Table 1. Validation scenario matrix

| Scenario | Design A repetitions | Design B repetitions | Total accepted runs | Main fault injected | Evidence source |
|---|---:|---:|---:|---|---|
| Normal operation | 3 | 3 | 6 | None | Serial logs and processed CSV |
| Wi-Fi loss | 3 | 3 | 6 | ESP32 connectivity interrupted and restored | Serial logs, operator events, processed CSV |
| Slow backend | 3 | 3 | 6 | 2000 ms proxy delay in front of Prometheus | Serial logs, delay-proxy method note, processed CSV |
| Backend down | 3 | 3 | 6 | Prometheus stopped and restarted | Serial logs, operator events, processed CSV |
| **Total** | **12** | **12** | **24** | Four validation scenarios | Frozen validation evidence |

**Thesis note:** This table should be placed early in Chapter 4 to show that the A-vs-B validation campaign was complete.
"""
(OUT / "table-01-validation-scenario-matrix.md").write_text(table1, encoding="utf-8")

# Table 2 Normal
a = get("normal", "design-a")
b = get("normal", "design-b")
table2_data = [
    ["Design A", val(a, "runs"), val(a, "mean_tick_count"), pct(a, "mean_wifi_up_ratio"), pct(a, "mean_live_ratio"), "N/A", "Stable live baseline through direct Prometheus access"],
    ["Design B", val(b, "runs"), val(b, "mean_tick_count"), pct(b, "mean_wifi_up_ratio"), pct(b, "mean_live_ratio"), pct(b, "mean_gateway_live_ratio"), "Stable live baseline through gateway endpoint"],
]
table2 = "# Table 2. Normal-operation results\n\n" + md_table(
    ["Design", "Repetitions", "Mean tick count", "Mean Wi-Fi up ratio", "Mean live ratio", "Mean gateway live ratio", "Main observation"],
    table2_data
) + "\n\n**Thesis note:** Normal operation shows that both designs were viable under healthy baseline conditions.\n"
(OUT / "table-02-normal-operation-results.md").write_text(table2, encoding="utf-8")

# Table 3 Wi-Fi loss
a = get("wifi-loss", "design-a")
b = get("wifi-loss", "design-b")
table3_data = [
    ["Design A", val(a, "runs"), val(a, "mean_wifi_down_count"), val(a, "mean_stale_count"), val(a, "mean_fail_count"), "N/A", val(a, "all_recovered_live_tail"), "FAIL periods occurred during outage, but accepted runs recovered after reconnect fix"],
    ["Design B", val(b, "runs"), val(b, "mean_wifi_down_count"), val(b, "mean_stale_count"), val(b, "mean_fail_count"), val(b, "mean_gateway_stale_count"), val(b, "all_recovered_live_tail"), "STALE behavior dominated and no FAIL occurred in accepted runs"],
]
table3 = "# Table 3. Wi-Fi-loss results\n\n" + md_table(
    ["Design", "Repetitions", "Mean Wi-Fi down count", "Mean stale count", "Mean fail count", "Mean gateway stale count", "Recovered live tail", "Main observation"],
    table3_data
) + "\n\n**Thesis note:** This table should mention that Design A accepted runs used the corrected reconnect behavior.\n"
(OUT / "table-03-wifi-loss-results.md").write_text(table3, encoding="utf-8")

# Table 4 Slow backend
a = get("slow-backend", "design-a")
b = get("slow-backend", "design-b")
table4_data = [
    ["Design A", val(a, "runs"), val(a, "mean_stale_count"), val(a, "mean_fail_count"), "N/A", val(a, "all_recovered_live_tail"), "Remained live under the chosen proxy-delay method and adjusted timeout"],
    ["Design B", val(b, "runs"), val(b, "mean_stale_count"), val(b, "mean_fail_count"), val(b, "mean_gateway_stale_count"), val(b, "all_recovered_live_tail"), "Often exposed STALE state and recovered; one run included a short FAIL pocket"],
]
table4 = "# Table 4. Slow-backend results\n\n" + md_table(
    ["Design", "Repetitions", "Mean stale count", "Mean fail count", "Mean gateway stale count", "Recovered live tail", "Main observation"],
    table4_data
) + "\n\n**Thesis note:** Do not overclaim this result. Design A behavior is configuration-sensitive because the accepted slow-backend runs used an adjusted timeout.\n"
(OUT / "table-04-slow-backend-results.md").write_text(table4, encoding="utf-8")

# Table 5 Backend down
a = get("backend-down", "design-a")
b = get("backend-down", "design-b")
table5_data = [
    ["Design A", val(a, "runs"), val(a, "mean_stale_count"), val(a, "mean_fail_count"), "N/A", val(a, "all_recovered_live_tail"), "Entered FAIL during Prometheus outage and recovered after restart"],
    ["Design B", val(b, "runs"), val(b, "mean_stale_count"), val(b, "mean_fail_count"), val(b, "mean_gateway_stale_count"), val(b, "all_recovered_live_tail"), "Stayed mainly STALE with zero FAIL and recovered to live"],
]
table5 = "# Table 5. Backend-down results\n\n" + md_table(
    ["Design", "Repetitions", "Mean stale count", "Mean fail count", "Mean gateway stale count", "Recovered live tail", "Main observation"],
    table5_data
) + "\n\n**Thesis note:** This is one of the strongest architecture findings and should not be buried.\n"
(OUT / "table-05-backend-down-results.md").write_text(table5, encoding="utf-8")

# Table 6 Cross-scenario trade-off
table6 = """# Table 6. Cross-scenario A-vs-B trade-off summary

| Dimension | Design A result | Design B result | Evidence-based interpretation |
|---|---|---|---|
| Normal operation | Maintained live metric output | Maintained live metric output through gateway | Both designs were viable under healthy conditions |
| Wi-Fi loss | Showed FAIL periods during outage but recovered after reconnect fix | Showed STALE periods and zero FAIL in accepted runs | Design B gave clearer degraded-state behavior during Wi-Fi interruption |
| Slow backend | Stayed live under selected proxy-delay method and adjusted timeout | Often showed STALE, with one short FAIL pocket, then recovered | Slow-backend behavior is configuration-sensitive and should be discussed carefully |
| Backend down | Entered FAIL during Prometheus outage | Stayed mainly STALE with zero FAIL | Strongest evidence for gateway-mediated degraded usefulness |
| Endpoint complexity | ESP32 handles direct backend queries and parsing | ESP32 consumes one compact gateway summary endpoint | Design B simplifies the endpoint |
| System complexity | Fewer components | Adds gateway component | Design A is architecturally simpler, Design B shifts complexity away from the ESP32 |
| Least privilege | Backend-facing access is closer to the device | Backend-facing access can be centralized in gateway | Design B provides a cleaner least-privilege boundary in this proof-of-concept |

**Thesis note:** This table belongs in the cross-scenario summary or at the beginning of Chapter 5.
"""
(OUT / "table-06-cross-scenario-tradeoff.md").write_text(table6, encoding="utf-8")

# Figure 1 data and simple SVG
degraded_scenarios = ["wifi-loss", "slow-backend", "backend-down"]
figure_rows = []
for scenario in degraded_scenarios:
    for design in ["design-a", "design-b"]:
        r = get(scenario, design)
        figure_rows.append({
            "scenario": scenario,
            "design": design,
            "mean_stale_count": float(r["mean_stale_count"]) if r["mean_stale_count"] else 0.0,
            "mean_fail_count": float(r["mean_fail_count"]) if r["mean_fail_count"] else 0.0,
        })

with (OUT / "figure-01-degraded-state-counts-data.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["scenario", "design", "mean_stale_count", "mean_fail_count"])
    writer.writeheader()
    writer.writerows(figure_rows)

# Build a dependency-free SVG bar chart.
max_value = max(max(r["mean_stale_count"], r["mean_fail_count"]) for r in figure_rows)
chart_width = 900
chart_height = 520
left = 190
top = 60
bar_h = 16
gap = 10
scale_w = 570

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="{chart_height}" viewBox="0 0 {chart_width} {chart_height}">')
svg.append('<rect width="100%" height="100%" fill="white"/>')
svg.append('<text x="20" y="32" font-family="Arial" font-size="20" font-weight="bold">Figure 1. Mean STALE and FAIL counts in degraded scenarios</text>')
svg.append('<text x="20" y="55" font-family="Arial" font-size="12">Source: final KPI aggregation from accepted serial-log validation runs.</text>')

y = top + 25
for r in figure_rows:
    label = f'{r["scenario"]} / {r["design"]}'
    stale_w = 0 if max_value == 0 else r["mean_stale_count"] / max_value * scale_w
    fail_w = 0 if max_value == 0 else r["mean_fail_count"] / max_value * scale_w

    svg.append(f'<text x="20" y="{y + 13}" font-family="Arial" font-size="12">{label}</text>')
    svg.append(f'<rect x="{left}" y="{y}" width="{stale_w:.1f}" height="{bar_h}" fill="#b0b0b0"/>')
    svg.append(f'<text x="{left + stale_w + 6:.1f}" y="{y + 12}" font-family="Arial" font-size="11">STALE {r["mean_stale_count"]:.1f}</text>')

    y += bar_h + 3
    svg.append(f'<rect x="{left}" y="{y}" width="{fail_w:.1f}" height="{bar_h}" fill="#4d4d4d"/>')
    svg.append(f'<text x="{left + fail_w + 6:.1f}" y="{y + 12}" font-family="Arial" font-size="11">FAIL {r["mean_fail_count"]:.1f}</text>')

    y += bar_h + gap + 8

svg.append('<text x="190" y="490" font-family="Arial" font-size="12">Light bar = STALE, dark bar = FAIL. Values are means across three accepted repetitions.</text>')
svg.append('</svg>')
(OUT / "figure-01-degraded-state-counts.svg").write_text("\n".join(svg), encoding="utf-8")

figure_note = """# Figure 1. Degraded-state count comparison

Figure description:

**Figure 1. Mean STALE and FAIL counts across degraded scenarios.** The figure summarizes the accepted serial-log validation runs for Wi-Fi loss, slow backend, and backend down. It shows that Design B mainly represented degraded operation as STALE in Wi-Fi-loss and backend-down scenarios, while Design A showed FAIL periods in those cases. The slow-backend result should be interpreted carefully because Design A used the selected proxy-delay method with an adjusted timeout.

Related result section:
- Chapter 4.6 Cross-scenario result summary

This figure supports the bounded observation that Design B gave clearer degraded-state semantics in the tested proof-of-concept scenarios.
"""
(OUT / "figure-01-degraded-state-counts.md").write_text(figure_note, encoding="utf-8")

readme = """# Thesis-ready results package

This folder contains thesis-ready tables and one figure derived from the final KPI aggregation.

Tables:
- table-01-validation-scenario-matrix.md
- table-02-normal-operation-results.md
- table-03-wifi-loss-results.md
- table-04-slow-backend-results.md
- table-05-backend-down-results.md
- table-06-cross-scenario-tradeoff.md

Figure:
- figure-01-degraded-state-counts.svg
- figure-01-degraded-state-counts-data.csv
- figure-01-degraded-state-counts.md

These outputs are intended for Chapter 4 Results and Chapter 5 Analysis/Discussion.
"""
(OUT / "README.md").write_text(readme, encoding="utf-8")

print("Generated thesis-ready outputs:")
for p in sorted(OUT.iterdir()):
    if p.is_file():
        print(f"- {p}")
