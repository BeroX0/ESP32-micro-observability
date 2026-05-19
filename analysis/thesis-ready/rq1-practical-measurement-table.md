# RQ1 practical measurement table

This file summarizes the supplementary RQ1 traffic measurement.

The measurement is not part of the official 40-run final-v2 validation campaign. It was added as extra evidence for the communication-cost part of RQ1 after supervisor feedback.

The measurement focuses on ESP32-facing traffic during normal operation. No Wi-Fi loss, backend delay, or backend outage was injected.

The byte values are based on the sum of `frame.len` for packets matching the ESP32-facing Wireshark/tshark filter.

## Table A. ESP32-facing traffic measurement

| Design | Repetitions | Mean packets per capture | Mean bytes per capture | Mean bytes per minute | Notes |
|---|---:|---:|---:|---:|---|
| Design A | 5 | 1800.0 | 225716.6 | 97338.8 | ESP32-to-Prometheus traffic on port 9090 |
| Design B | 5 | 1021.4 | 122962.4 | 49755.9 | ESP32-to-gateway traffic on port 8080; gateway-to-Prometheus traffic is not included |

## Interpretation note

In this measurement, Design B had lower ESP32-facing traffic than Design A during normal operation. Design B used about 51.1% of Design A's bytes per minute, which corresponds to about 48.9% lower ESP32-facing traffic in the tested setup.

This result supports the RQ1 communication-cost comparison. It should be interpreted together with the final-v2 validation evidence, not as a universal bandwidth benchmark.

## Limitations

The measurement was made in one local test setup using a Windows Mobile Hotspot, one ESP32 device, and a local Prometheus/gateway environment.

The capture durations were not exactly identical, so bytes per minute is the most useful comparison value.

The measurement only covers ESP32-facing traffic. For Design B, gateway-to-Prometheus traffic is intentionally excluded from this endpoint-burden comparison.

ESP32-side update timing was not completed in this measurement block. The final RQ1 strengthening therefore relies on practical ESP32-facing traffic measurement and the existing final-v2 validation evidence.
