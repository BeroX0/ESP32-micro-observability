# ESP32 Micro-Observability Display

## Overview

This project is a bachelor thesis proof-of-concept for a small ESP32-based display that shows selected server health metrics. The idea is to give quick local awareness of system status without needing to keep a full monitoring dashboard open all the time.

The system uses a local Prometheus-based monitoring setup and an ESP32 touch display. The project compares two different ways of getting monitoring data to the device.

## Architectures

The project compares two designs.

### Design A: Direct Prometheus access

In Design A, the ESP32 queries Prometheus directly. The device sends the needed requests, parses the responses, and shows the selected values on the display.

This design has fewer system components, but it also gives the ESP32 more responsibility. The device must handle more backend communication and parsing itself.

### Design B: Gateway-mediated access

In Design B, the ESP32 queries a small gateway endpoint instead of querying Prometheus directly. The gateway queries Prometheus, prepares the needed values, adds freshness and state information, and returns a smaller summary to the ESP32.

This design adds one extra component, but it makes the ESP32 side simpler. It also gives a cleaner place to handle caching, stale data, and backend access.

## Metrics

The prototype focuses on a small set of host health signals:

- CPU usage
- memory usage
- disk usage
- network connectivity
- RX/TX network rates
- freshness and state information

The goal is not to replace Grafana or a full monitoring platform. The display only shows a compact set of values that are useful for quick status checking.

## Repository structure

- `backend/` - Prometheus and backend configuration
- `gateway/` - FastAPI gateway used by Design B
- `firmware/` - ESP32 firmware for Design A and Design B
- `docs/` - architecture, setup, security, and experiment documentation
- `experiments/` - raw, processed, and summarized validation evidence
- `analysis/results/` - aggregated KPI results
- `analysis/thesis-ready/` - selected result tables and figures used for the thesis
- `tools/` - scripts for analysis and validation support

## Running the backend

The backend setup is based on Prometheus. The main backend files are in:

- `backend/compose/`
- `backend/prometheus/`

A typical startup is done from the repository root using the provided `Makefile` or Docker Compose files. The exact command depends on the local environment, but the backend should start Prometheus and the needed exporter configuration.

Before running the ESP32 firmware, check that Prometheus is reachable from the same network as the ESP32.

## Running the gateway

The gateway code is in:

- `gateway/app/`

Install the Python dependencies:

1. Go to `gateway/app`.
2. Create and activate a Python virtual environment.
3. Install the dependencies from `requirements.txt`.

Example commands:

- `cd gateway/app`
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`

Start the gateway:

- `python -m uvicorn main:app --host 0.0.0.0 --port 8080`

The ESP32 Design B firmware expects the gateway summary endpoint to be reachable from the local network.

## Firmware

The firmware is divided into two designs:

- `firmware/design_a/`
- `firmware/design_b/`

Design A contains the ESP32 firmware that connects directly to Prometheus.

Design B contains the ESP32 firmware that connects to the gateway endpoint.

Before flashing the firmware, local Wi-Fi settings and local endpoint addresses must be configured for the test environment. Real Wi-Fi credentials should not be committed to Git.

## Validation

The project was validated with four scenarios:

- normal operation
- Wi-Fi loss
- slow backend
- backend down

The validation campaign contains 24 accepted runs:

- 4 scenarios
- 2 designs
- 3 repetitions per design and scenario

The raw accepted serial logs are available in:

- `experiments/raw/`

Processed validation summaries are available in:

- `experiments/processed/`
- `experiments/summaries/`

The validation mainly used serial-log output from the ESP32. The logs show Wi-Fi state, metric state, gateway state where relevant, and whether values were live, stale, or failed.

## Results

Both designs worked during normal operation.

The main difference was seen during failure scenarios. Design A is simpler because the ESP32 talks directly to Prometheus. However, this also means the ESP32 has more responsibility for backend communication and failure handling.

Design B adds a gateway, but it made the ESP32 side simpler. It also gave clearer stale-state behaviour during backend problems. In the accepted backend-down runs, Design B mainly showed stale data instead of fail states, while Design A entered fail states during the outage.

The analysis also showed that Design B gives a cleaner least-privilege boundary. The ESP32 only needs access to the gateway summary endpoint, while backend-facing access can stay on the gateway side.

Selected result tables and figures are in:

- `analysis/results/`
- `analysis/thesis-ready/`

## Limitations

This is a local proof-of-concept, not a production monitoring product.

The validation was done in a controlled test setup. The evidence is mainly based on ESP32 serial logs. The project does not include a full production security audit, long-term field testing, or testing across many different networks and hardware platforms.

The results should therefore be understood as evidence for the tested setup, not as a general result for all monitoring systems.

## Security note

No real secrets should be stored in this repository.

Use `.env.example` as a template and keep real credentials in local environment files outside Git. Wi-Fi passwords, API keys, tokens, and other private values should never be committed.

## Authors

Baraa Abo Shala  
Ayah N M Salem
