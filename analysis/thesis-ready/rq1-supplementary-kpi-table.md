# RQ1 supplementary API-level KPI table

| Design | API pattern | Requests per update | Samples | Mean response payload size | Mean host-side HTTP timing | Interpretation |
|---|---|---:|---:|---:|---:|---|
| Design A | Six direct Prometheus query responses | 6 | 20 | 946.0 bytes total | 6.712 ms sequential total | Direct design transfers and parses several backend responses per update cycle |
| Design B | One gateway summary response | 1 | 20 | 338.0 bytes | 2.153 ms | Gateway design exposes one compact summary response to the ESP32 |
| Comparison | Design A total vs Design B summary | 6 vs 1 | 20 | 2.80× larger for Design A (64.3% smaller for Design B) | 3.12× higher for Design A sequential timing (67.9% lower for Design B) | Supports RQ1 communication-cost and API-level responsiveness comparison |

