#!/usr/bin/env python3
import csv
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(".")
OUT_RESULTS = ROOT / "analysis" / "results"
OUT_THESIS = ROOT / "analysis" / "thesis-ready"

OUT_RESULTS.mkdir(parents=True, exist_ok=True)
OUT_THESIS.mkdir(parents=True, exist_ok=True)

SAMPLES = 20
TIMEOUT_SECONDS = 10

PROM_BASE = "http://localhost:9090/api/v1/query"
GATEWAY_SUMMARY_URL = "http://localhost:8080/api/v1/summary"

# These queries match the six metric categories used by the ESP32 display.
# They are intentionally measured as API-level HTTP responses from the host PC.
DESIGN_A_QUERIES = [
    ("cpu", "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[1m])) * 100)"),
    ("memory", "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"),
    ("disk", "(1 - (node_filesystem_avail_bytes{mountpoint=\"/\",fstype!=\"rootfs\"} / node_filesystem_size_bytes{mountpoint=\"/\",fstype!=\"rootfs\"})) * 100"),
    ("connectivity", "up{job=\"node_exporter\"}"),
    ("rx", "rate(node_network_receive_bytes_total{device!=\"lo\"}[1m])"),
    ("tx", "rate(node_network_transmit_bytes_total{device!=\"lo\"}[1m])"),
]

def prom_url(query: str) -> str:
    return PROM_BASE + "?" + urllib.parse.urlencode({"query": query})

def fetch(url: str):
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rq1-api-kpi-measurement/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            body = resp.read()
            elapsed_ms = (time.perf_counter() - start) * 1000
            return {
                "status_code": resp.status,
                "response_size_bytes": len(body),
                "elapsed_ms": elapsed_ms,
                "error": "",
            }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "status_code": "",
            "response_size_bytes": "",
            "elapsed_ms": elapsed_ms,
            "error": repr(exc),
        }

raw_rows = []

for sample_index in range(1, SAMPLES + 1):
    # Design A: six direct Prometheus API requests
    for metric_name, query in DESIGN_A_QUERIES:
        url = prom_url(query)
        result = fetch(url)
        raw_rows.append({
            "sample_index": sample_index,
            "design": "design-a",
            "request_group": "prometheus-direct",
            "metric_or_endpoint": metric_name,
            "url": url,
            "status_code": result["status_code"],
            "response_size_bytes": result["response_size_bytes"],
            "elapsed_ms": f'{result["elapsed_ms"]:.3f}',
            "error": result["error"],
        })

    # Design B: one gateway summary API request
    result = fetch(GATEWAY_SUMMARY_URL)
    raw_rows.append({
        "sample_index": sample_index,
        "design": "design-b",
        "request_group": "gateway-summary",
        "metric_or_endpoint": "summary",
        "url": GATEWAY_SUMMARY_URL,
        "status_code": result["status_code"],
        "response_size_bytes": result["response_size_bytes"],
        "elapsed_ms": f'{result["elapsed_ms"]:.3f}',
        "error": result["error"],
    })

raw_csv = OUT_RESULTS / "rq1-api-kpi-raw-samples.csv"
with raw_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "sample_index",
        "design",
        "request_group",
        "metric_or_endpoint",
        "url",
        "status_code",
        "response_size_bytes",
        "elapsed_ms",
        "error",
    ])
    writer.writeheader()
    writer.writerows(raw_rows)

# Validate failures explicitly.
failed_rows = [r for r in raw_rows if str(r["status_code"]) != "200" or r["error"]]
if failed_rows:
    failure_path = OUT_RESULTS / "rq1-api-kpi-failed-samples.json"
    failure_path.write_text(json.dumps(failed_rows, indent=2), encoding="utf-8")
    raise SystemExit(f"Measurement failed: {len(failed_rows)} HTTP requests failed. See {failure_path}")

def rows_for(design=None, metric=None):
    selected = raw_rows
    if design is not None:
        selected = [r for r in selected if r["design"] == design]
    if metric is not None:
        selected = [r for r in selected if r["metric_or_endpoint"] == metric]
    return selected

def num_values(rows, field):
    return [float(r[field]) for r in rows]

summary_rows = []

# Individual Design A query summaries.
for metric_name, _query in DESIGN_A_QUERIES:
    rs = rows_for("design-a", metric_name)
    sizes = num_values(rs, "response_size_bytes")
    times = num_values(rs, "elapsed_ms")
    summary_rows.append({
        "design": "design-a",
        "measurement": metric_name,
        "request_count_per_sample": 1,
        "samples": len(rs),
        "mean_response_size_bytes": f"{mean(sizes):.1f}",
        "stdev_response_size_bytes": f"{stdev(sizes):.1f}" if len(sizes) > 1 else "0.0",
        "mean_elapsed_ms": f"{mean(times):.3f}",
        "stdev_elapsed_ms": f"{stdev(times):.3f}" if len(times) > 1 else "0.000",
    })

# Design A sequential total per sample.
design_a_total_sizes = []
design_a_total_times = []
for sample_index in range(1, SAMPLES + 1):
    rs = [r for r in raw_rows if r["design"] == "design-a" and int(r["sample_index"]) == sample_index]
    design_a_total_sizes.append(sum(float(r["response_size_bytes"]) for r in rs))
    design_a_total_times.append(sum(float(r["elapsed_ms"]) for r in rs))

summary_rows.append({
    "design": "design-a",
    "measurement": "six_prometheus_queries_total",
    "request_count_per_sample": 6,
    "samples": SAMPLES,
    "mean_response_size_bytes": f"{mean(design_a_total_sizes):.1f}",
    "stdev_response_size_bytes": f"{stdev(design_a_total_sizes):.1f}" if len(design_a_total_sizes) > 1 else "0.0",
    "mean_elapsed_ms": f"{mean(design_a_total_times):.3f}",
    "stdev_elapsed_ms": f"{stdev(design_a_total_times):.3f}" if len(design_a_total_times) > 1 else "0.000",
})

# Design B summary.
design_b_rows = rows_for("design-b", "summary")
design_b_sizes = num_values(design_b_rows, "response_size_bytes")
design_b_times = num_values(design_b_rows, "elapsed_ms")

summary_rows.append({
    "design": "design-b",
    "measurement": "gateway_summary",
    "request_count_per_sample": 1,
    "samples": len(design_b_rows),
    "mean_response_size_bytes": f"{mean(design_b_sizes):.1f}",
    "stdev_response_size_bytes": f"{stdev(design_b_sizes):.1f}" if len(design_b_sizes) > 1 else "0.0",
    "mean_elapsed_ms": f"{mean(design_b_times):.3f}",
    "stdev_elapsed_ms": f"{stdev(design_b_times):.3f}" if len(design_b_times) > 1 else "0.000",
})

design_a_total_bytes = mean(design_a_total_sizes)
design_a_total_ms = mean(design_a_total_times)
design_b_bytes = mean(design_b_sizes)
design_b_ms = mean(design_b_times)

size_reduction_factor = design_a_total_bytes / design_b_bytes if design_b_bytes else 0
size_reduction_percent = (1 - (design_b_bytes / design_a_total_bytes)) * 100 if design_a_total_bytes else 0
time_ratio = design_a_total_ms / design_b_ms if design_b_ms else 0
time_reduction_percent = (1 - (design_b_ms / design_a_total_ms)) * 100 if design_a_total_ms else 0

summary_rows.append({
    "design": "comparison",
    "measurement": "design_a_total_vs_design_b_summary",
    "request_count_per_sample": "",
    "samples": SAMPLES,
    "mean_response_size_bytes": f"{design_a_total_bytes:.1f} vs {design_b_bytes:.1f}",
    "stdev_response_size_bytes": "",
    "mean_elapsed_ms": f"{design_a_total_ms:.3f} vs {design_b_ms:.3f}",
    "stdev_elapsed_ms": "",
})

summary_csv = OUT_RESULTS / "rq1-api-kpi-summary.csv"
with summary_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "design",
        "measurement",
        "request_count_per_sample",
        "samples",
        "mean_response_size_bytes",
        "stdev_response_size_bytes",
        "mean_elapsed_ms",
        "stdev_elapsed_ms",
    ])
    writer.writeheader()
    writer.writerows(summary_rows)

table_md = OUT_THESIS / "rq1-supplementary-kpi-table.md"
table_md.write_text(f"""# RQ1 supplementary API-level KPI table

| Design | API pattern | Requests per update | Samples | Mean response payload size | Mean host-side HTTP timing | Interpretation |
|---|---|---:|---:|---:|---:|---|
| Design A | Six direct Prometheus query responses | 6 | {SAMPLES} | {design_a_total_bytes:.1f} bytes total | {design_a_total_ms:.3f} ms sequential total | Direct design transfers and parses several backend responses per update cycle |
| Design B | One gateway summary response | 1 | {SAMPLES} | {design_b_bytes:.1f} bytes | {design_b_ms:.3f} ms | Gateway design exposes one compact summary response to the ESP32 |
| Comparison | Design A total vs Design B summary | 6 vs 1 | {SAMPLES} | {size_reduction_factor:.2f}× larger for Design A ({size_reduction_percent:.1f}% smaller for Design B) | {time_ratio:.2f}× higher for Design A sequential timing ({time_reduction_percent:.1f}% lower for Design B) | Supports RQ1 communication-cost and API-level responsiveness comparison |

""", encoding="utf-8")

note_md = OUT_THESIS / "rq1-supplementary-kpi-note.md"
note_md.write_text(f"""# RQ1 supplementary KPI measurement note

## Purpose

This supplementary measurement strengthens RQ1 by adding direct evidence for API-level response size and host-side HTTP timing.

## Method

The measurement was executed from the host PC against local endpoints.

Design A was measured as six direct Prometheus API query responses:

- CPU
- memory
- disk
- connectivity
- RX
- TX

Design B was measured as one gateway summary response:

- `/api/v1/summary`

Each measurement used {SAMPLES} samples.

## Results summary

Design A six-query total mean response size:

```text
{design_a_total_bytes:.1f} bytes

Design B gateway summary mean response size:

{design_b_bytes:.1f} bytes

Design A six-query sequential mean API timing:

{design_a_total_ms:.3f} ms

Design B gateway summary mean API timing:

{design_b_ms:.3f} ms

Design B response size was approximately {size_reduction_percent:.1f}% smaller than the Design A six-query total in this host-side measurement.

Measurement limitation

This supplementary measurement compares API-level response size and host-side HTTP timing in the local test environment. It is not a packet-level bandwidth benchmark and not a full ESP32 end-to-end latency measurement.

How to use in the thesis

Use this as supplementary evidence for RQ1 only. It supports the communication-cost and API-level responsiveness part of the trade-off.

It should not replace the 24-run validation campaign, which remains the main evidence for update reliability and degraded-state behaviour.

""", encoding="utf-8")

print("Generated:")
print(f"- {raw_csv}")
print(f"- {summary_csv}")
print(f"- {table_md}")
print(f"- {note_md}")
print()
print("Key comparison:")
print(f"Design A total mean size: {design_a_total_bytes:.1f} bytes")
print(f"Design B mean size: {design_b_bytes:.1f} bytes")
print(f"Design A total mean timing: {design_a_total_ms:.3f} ms")
print(f"Design B mean timing: {design_b_ms:.3f} ms")
