# Table 6. Cross-scenario A-vs-B trade-off summary

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
