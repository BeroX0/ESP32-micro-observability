# Cross-scenario A-vs-B observation table

| Dimension | Design A result | Design B result | Evidence-based observation |
|---|---|---|---|
| Normal operation | Maintained live metric output in accepted runs | Maintained live metric output through gateway in accepted runs | Both designs were viable under healthy baseline conditions |
| Wi-Fi loss | Showed FAIL periods during outage but recovered after reconnect fix | Showed STALE periods and zero FAIL in accepted runs | Design B provided more graceful degraded-state semantics during Wi-Fi loss |
| Slow backend | Stayed LIVE under the selected delay-proxy method and adjusted timeout | Often showed STALE, with one short FAIL pocket, then recovered | Slow-backend result is configuration-sensitive and must be discussed carefully |
| Backend down | Entered FAIL during Prometheus outage and recovered after restart | Stayed mainly STALE with zero FAIL and recovered to live | Strongest evidence for gateway-mediated degraded usefulness |
| Endpoint responsibility | ESP32 handles direct backend queries | ESP32 consumes one compact gateway summary endpoint | Design B simplifies the endpoint at the cost of an extra gateway component |
| Least privilege | Backend-facing access is closer to the device | Backend-facing access can be centralized in the gateway | Design B gives a cleaner least-privilege boundary in this proof-of-concept |
