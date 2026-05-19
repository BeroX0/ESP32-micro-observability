# ESP32 Micro-Observability Display

## Overview

This project is a bachelor thesis proof-of-concept for a small ESP32-based display that shows selected server health metrics. The goal is to give quick local awareness of system status without needing to keep a full monitoring dashboard open all the time.

The system uses a local Prometheus-based monitoring setup and an ESP32 touch display. The project compares two ways of getting monitoring data to the device.

## Compared designs

### Design A: Direct Prometheus access

In Design A, the ESP32 queries Prometheus directly. The device sends the needed requests, parses the responses, and shows the selected values on the display.

This design has fewer system components, but it also gives the ESP32 more responsibility. The device must handle more backend communication, parsing, timeouts, and failure handling itself.

Main firmware path: `firmware/design_a/esp32_direct_prometheus/`

### Design B: Gateway-mediated access

In Design B, the ESP32 queries a small gateway endpoint instead of querying Prometheus directly. The gateway queries Prometheus, prepares the needed values, adds state and freshness information, and returns a compact summary to the ESP32.

This design adds one extra component, but it makes the ESP32 side simpler. It also gives a clearer place to handle caching, stale data, and backend access.

Main firmware path: `firmware/design_b/esp32_gateway_summary/`

## Metrics shown by the prototype

The prototype focuses on a small set of host health signals:

- CPU usage
- memory usage
- disk usage
- network connectivity
- RX/TX network rates
- LIVE, STALE, and FAIL display states

The display is not meant to replace Grafana or a full monitoring platform. It only shows a compact set of values for quick status checking.

## Repository structure

- `backend/` - Prometheus and backend configuration
- `gateway/` - FastAPI gateway used by Design B
- `firmware/` - ESP32 firmware for Design A and Design B
- `docs/` - architecture, setup, security, and experiment documentation
- `experiments/processed/` - processed validation and measurement data
- `experiments/raw/` - note about raw evidence handling
- `analysis/results/` - aggregated result files
- `analysis/thesis-ready/` - selected result tables and figures
- `tools/` - analysis and validation support scripts

## Running the backend

The backend setup is based on Prometheus and Node Exporter. The main backend files are in `backend/`.

A typical startup is done from the repository root using the provided Makefile or Docker Compose files. The exact command can depend on the local environment.

Before running the ESP32 firmware, check that Prometheus is reachable from the same network as the ESP32.

## Running the gateway

The gateway code is in `gateway/app/`.

Example commands:

- `cd gateway/app`
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `python -m uvicorn main:app --host 0.0.0.0 --port 8080`

The Design B firmware expects the gateway summary endpoint to be reachable from the local network.

## Validation evidence

The final validation evidence contains 40 accepted final-v2 runs:

- 4 scenarios
- 2 designs
- 5 repetitions per design and scenario
- 40 accepted runs in total

The tested scenarios were:

- normal operation
- Wi-Fi loss
- slow backend response
- backend down

Processed final-v2 validation data is available in:

- `experiments/processed/final-v2/`
- `analysis/results/final-v2-thesis-tables.md`
- `analysis/thesis-ready/final-v2-result-tables.md`

The public repository contains processed data and selected result tables. Full raw serial logs and packet captures are kept outside this public repository.

## Supplementary RQ1 traffic measurement

The project also includes supplementary ESP32-facing traffic measurements for RQ1. These measurements compare the normal-operation communication cost between the ESP32 and the endpoint it contacts.

Design A measures ESP32-to-Prometheus traffic. Design B measures ESP32-to-gateway traffic.

Processed traffic data is available in:

- `experiments/processed/rq1-practical-measurements/`
- `analysis/results/rq1-final-v2-traffic-summary.csv`
- `analysis/thesis-ready/rq1-practical-measurement-table.md`

## RQ3 security sanity checks

The repository includes practical security sanity checks for the least-privilege comparison. These checks focus on access paths, endpoint exposure, credential placement, and query-control boundaries.

They are not penetration testing, vulnerability scanning, or a full production security audit.

The public result files are:

- `analysis/results/security-sanity-checks-results.csv`
- `analysis/thesis-ready/security-sanity-checks-table.md`

## Main result direction

Both designs worked during normal operation.

Design A kept the system path simpler, but placed more backend-facing responsibility on the ESP32.

Design B added a gateway, but gave the ESP32 a simpler endpoint interface and clearer degraded-state behavior in the tested fault scenarios. It also gave a cleaner least-privilege boundary because Prometheus-facing access could stay on the gateway side.

These results are limited to the tested proof-of-concept setup.

## Limitations

This is a local proof-of-concept, not a production monitoring product.

The validation was done in a controlled test setup. The project does not include packet-level production benchmarking, long-term field testing, penetration testing, or a full production security audit.

The results should therefore be understood as practical findings from the tested setup, not as general conclusions for all monitoring systems.

## Security note

No real secrets should be stored in this repository.

Use `.env.example` as a template and keep real credentials in local environment files outside Git. Wi-Fi passwords, API keys, tokens, and other private values should never be committed.

## Authors

Baraa Abo Shala  
Ayah N M Salem
