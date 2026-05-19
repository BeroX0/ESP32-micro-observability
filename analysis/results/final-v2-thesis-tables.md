# Final-v2 validation evidence tables

Generated from the committed final-v2 raw serial logs and run notes.

## Evidence inventory

| Measure | Value |
| --- | --- |
| Total final-v2 runs | 40 |
| Accepted runs | 40 |
| Scenarios | normal, wifi-loss, slow-backend, backend-down |
| Designs | design-a, design-b |
| Repetitions per scenario/design | 5 |

## Table 1. Accepted runs by scenario and design

| Scenario | Design | Run count | Accepted count |
| --- | --- | --- | --- |
| normal | design-a | 5 | 5 |
| normal | design-b | 5 | 5 |
| wifi-loss | design-a | 5 | 5 |
| wifi-loss | design-b | 5 | 5 |
| slow-backend | design-a | 5 | 5 |
| slow-backend | design-b | 5 | 5 |
| backend-down | design-a | 5 | 5 |
| backend-down | design-b | 5 | 5 |

## Table 2. Observed behavior by scenario and design

| Scenario | Design | Runs with LIVE | Runs with STALE | Runs with FAIL | Runs with wifi=DOWN | Runs with gw=stale | Runs with reset markers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| normal | design-a | 5 | 0 | 0 | 0 | 0 | 0 |
| normal | design-b | 5 | 0 | 0 | 0 | 0 | 0 |
| wifi-loss | design-a | 5 | 5 | 5 | 5 | 0 | 0 |
| wifi-loss | design-b | 5 | 5 | 4 | 5 | 5 | 0 |
| slow-backend | design-a | 5 | 5 | 5 | 0 | 0 | 0 |
| slow-backend | design-b | 5 | 5 | 0 | 0 | 5 | 0 |
| backend-down | design-a | 5 | 5 | 5 | 0 | 0 | 0 |
| backend-down | design-b | 5 | 5 | 0 | 0 | 5 | 0 |

## Table 3. Status label counts by scenario and design

| Scenario | Design | LIVE labels | STALE labels | FAIL labels | wifi=DOWN lines | gw=stale lines |
| --- | --- | --- | --- | --- | --- | --- |
| normal | design-a | 3600 | 0 | 0 | 0 | 0 |
| normal | design-b | 3612 | 0 | 0 | 0 | 0 |
| wifi-loss | design-a | 2761 | 556 | 1467 | 491 | 0 |
| wifi-loss | design-b | 2736 | 2020 | 16 | 504 | 505 |
| slow-backend | design-a | 2972 | 494 | 1262 | 0 | 0 |
| slow-backend | design-b | 2992 | 1720 | 0 | 0 | 430 |
| backend-down | design-a | 2987 | 79 | 282 | 0 | 0 |
| backend-down | design-b | 3000 | 1800 | 0 | 0 | 450 |

## Interpretation notes for thesis use

- Normal runs are expected to contain LIVE values and no injected fault markers.

- Wi-Fi-loss runs are expected to contain wifi=DOWN during the outage and recovery to wifi=UP/LIVE.

- Slow-backend runs are expected to contain delay-control markers and degraded STALE/FAIL behavior during the delay interval.

- Backend-down runs are expected to contain Prometheus stop/start markers and degraded STALE/FAIL behavior while Prometheus is unavailable.

- Design B gateway runs are expected to contain gw=live during normal/recovered operation and gw=stale during upstream degradation.

- Reset marker counts should remain zero for accepted fault-injection runs unless a deliberate reset was part of the method.
