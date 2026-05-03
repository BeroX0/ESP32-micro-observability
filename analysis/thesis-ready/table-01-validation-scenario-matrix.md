# Table 1. Validation scenario matrix

| Scenario | Design A repetitions | Design B repetitions | Total accepted runs | Main fault injected | Evidence source |
|---|---:|---:|---:|---|---|
| Normal operation | 3 | 3 | 6 | None | Serial logs and processed CSV |
| Wi-Fi loss | 3 | 3 | 6 | ESP32 connectivity interrupted and restored | Serial logs, operator events, processed CSV |
| Slow backend | 3 | 3 | 6 | 2000 ms proxy delay in front of Prometheus | Serial logs, delay-proxy method note, processed CSV |
| Backend down | 3 | 3 | 6 | Prometheus stopped and restarted | Serial logs, operator events, processed CSV |
| **Total** | **12** | **12** | **24** | Four validation scenarios | Frozen validation evidence |

**Thesis note:** This table should be placed early in Chapter 4 to show that the A-vs-B validation campaign was complete.
