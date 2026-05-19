# Final-v2 result tables

This file contains thesis-ready result tables based on the final-v2 validation evidence.

The final-v2 validation campaign contains 40 accepted runs. Each scenario and design pair has five accepted repetitions. Earlier validation evidence is not used as the final result basis in this file.

The final-v2 campaign includes four validation scenarios:

- normal operation
- Wi-Fi loss
- slow backend
- backend down

The compared designs are:

- Design A: ESP32 direct access to Prometheus
- Design B: ESP32 access through the gateway summary endpoint

## Evidence notes

The slow-backend final-v2 result uses the baseline configuration. The old Design A result with a 3000 ms timeout is treated only as a configuration-sensitivity observation. It is not used as the final comparison result.

The Wi-Fi-loss final-v2 runs use corrected firmware after an earlier reconnect and state-labeling weakness was found during preflight testing. This means the final-v2 Wi-Fi-loss result is based on the corrected behavior, where cached values are not falsely kept as LIVE when Wi-Fi is down.

The final-v2 evidence is valid for the tested local proof-of-concept setup. It should not be read as a universal benchmark for all ESP32, Prometheus, or gateway-based monitoring systems.

## Table 1. Final-v2 evidence inventory

| Evidence item | Value |
|---|---:|
| Total accepted runs | 40 |
| Scenarios | 4 |
| Designs | 2 |
| Repetitions per scenario/design pair | 5 |
| Normal-operation runs | 10 |
| Wi-Fi-loss runs | 10 |
| Slow-backend runs | 10 |
| Backend-down runs | 10 |
| Raw run folders | 40 |
| Runs with serial.log | 40 |
| Runs with run-note.md | 40 |
| Runs with operator-events.md | 40 |

## Table 2. Accepted runs by scenario and design

| Scenario | Design A accepted runs | Design B accepted runs | Total accepted runs |
|---|---:|---:|---:|
| Normal operation | 5 | 5 | 10 |
| Wi-Fi loss | 5 | 5 | 10 |
| Slow backend | 5 | 5 | 10 |
| Backend down | 5 | 5 | 10 |
| **Total** | **20** | **20** | **40** |

## Table 3. Scenario summary

| Scenario | Design | Accepted runs | Mean duration (s) | Mean samples | Runs with LIVE | Runs with STALE | Runs with FAIL | Runs with Wi-Fi down | Runs with gateway STALE | Runs with reset markers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Normal operation | Design A | 5 | 180.6 | 180.0 | 5 | 0 | 0 | 0 | 0 | 0 |
| Normal operation | Design B | 5 | 180.2 | 180.6 | 5 | 0 | 0 | 0 | 0 | 0 |
| Wi-Fi loss | Design A | 5 | 240.4 | 239.2 | 5 | 5 | 5 | 5 | 0 | 0 |
| Wi-Fi loss | Design B | 5 | 240.6 | 238.6 | 5 | 5 | 4 | 5 | 5 | 0 |
| Slow backend | Design A | 5 | 240.8 | 236.4 | 5 | 5 | 5 | 0 | 0 | 0 |
| Slow backend | Design B | 5 | 240.4 | 235.6 | 5 | 5 | 0 | 0 | 5 | 0 |
| Backend down | Design A | 5 | 240.4 | 167.4 | 5 | 5 | 5 | 0 | 0 | 0 |
| Backend down | Design B | 5 | 240.4 | 240.0 | 5 | 5 | 0 | 0 | 5 | 0 |

## Table 4. Status label counts

| Scenario | Design | LIVE labels | STALE labels | FAIL labels | Wi-Fi UP lines | Wi-Fi DOWN lines | Gateway LIVE lines | Gateway STALE lines | Gateway FAIL lines |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Normal operation | Design A | 3600 | 0 | 0 | 900 | 0 | 0 | 0 | 0 |
| Normal operation | Design B | 3612 | 0 | 0 | 903 | 0 | 903 | 0 | 0 |
| Wi-Fi loss | Design A | 2761 | 556 | 1467 | 705 | 491 | 0 | 0 | 0 |
| Wi-Fi loss | Design B | 2736 | 2020 | 16 | 689 | 504 | 684 | 505 | 4 |
| Slow backend | Design A | 2972 | 494 | 1262 | 1182 | 0 | 0 | 0 | 0 |
| Slow backend | Design B | 2992 | 1720 | 0 | 1178 | 0 | 748 | 430 | 0 |
| Backend down | Design A | 2987 | 79 | 282 | 837 | 0 | 0 | 0 | 0 |
| Backend down | Design B | 3000 | 1800 | 0 | 1200 | 0 | 750 | 450 | 0 |

## Table 5. Degraded scenario comparison

| Scenario | Design | STALE labels | FAIL labels | Main observation |
|---|---|---:|---:|---|
| Wi-Fi loss | Design A | 556 | 1467 | Design A showed both STALE and FAIL behavior during the Wi-Fi outage and recovered afterward. |
| Wi-Fi loss | Design B | 2020 | 16 | Design B mostly showed STALE behavior during the Wi-Fi outage, with only a small number of FAIL labels. |
| Slow backend | Design A | 494 | 1262 | Design A showed FAIL-heavy behavior when backend responses were delayed. |
| Slow backend | Design B | 1720 | 0 | Design B showed STALE behavior through the gateway and recorded no FAIL labels in this scenario. |
| Backend down | Design A | 79 | 282 | Design A showed some STALE labels and then FAIL behavior when Prometheus was unavailable. |
| Backend down | Design B | 1800 | 0 | Design B showed STALE gateway behavior and recorded no FAIL labels in this scenario. |

## Main result interpretation notes

Both designs worked during normal operation. The normal-operation runs showed LIVE behavior for both Design A and Design B.

During Wi-Fi loss, both designs detected the degraded condition and recovered after the hotspot was restored. Design A produced more FAIL labels during the outage. Design B produced mostly STALE labels and only a small number of FAIL labels.

During slow-backend testing, Design A produced both STALE and FAIL labels. Design B produced STALE labels and no FAIL labels. This suggests that the gateway helped the ESP32 keep a clearer degraded state when the upstream backend was slow.

During backend-down testing, Design A produced STALE and FAIL labels when Prometheus was stopped. Design B produced STALE labels and no FAIL labels. This shows that the gateway design gave a more controlled degraded state in this tested setup.

No accepted final-v2 scenario group had reset markers. This supports that the observed behavior came from the injected conditions and recovery, not from ESP32 reboot behavior.

The final-v2 result supports using the 40-run evidence as the final result basis for the thesis.
