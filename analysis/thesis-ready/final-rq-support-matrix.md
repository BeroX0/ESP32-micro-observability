# Final research-question support matrix

## Purpose

This matrix summarizes how the final thesis evidence supports RQ1, RQ2, and RQ3 after the research-question strengthening addendum.

It is intended for final thesis polishing and for checking that each research question has explicit evidence, a clear main result, and an honest caveat.

| RQ | Evidence used | Main result | Caveat |
|---|---|---|---|
| RQ1: Which architecture gives the better balance between update latency, update reliability, and bandwidth usage? | Normal-operation validation, degraded-scenario reliability evidence, final KPI aggregation, supplementary API payload-size measurement, supplementary host-side API timing measurement, architecture comparison | Both designs worked under normal operation. Design B is stronger overall when endpoint simplicity, compact communication, degraded-state handling, and least-privilege separation are included. The supplementary measurement showed Design B used one 338.0-byte gateway response, compared with 946.0 bytes total for Design A’s six Prometheus responses. Design B also showed lower host-side API timing: 2.153 ms compared with 6.712 ms for Design A’s six sequential requests. | Timing is API-level host-side timing, not full ESP32 end-to-end latency. Payload size is HTTP response size, not packet-level bandwidth. |
| RQ2: How useful can the display remain during Wi-Fi loss, slow backend responses, backend downtime, and stale-data situations? | 24-run validation campaign, Wi-Fi-loss scenario, slow-backend scenario, backend-down scenario, processed serial summaries, final KPI aggregation, Chapter 4 results, Chapter 5 discussion | Design B showed stronger degraded-state behavior, especially in Wi-Fi-loss and backend-down scenarios. Design A showed FAIL periods during Wi-Fi loss but recovered after reconnect fix. Design B showed STALE and zero FAIL in accepted Wi-Fi-loss runs. In backend-down, Design A entered FAIL while Design B remained mainly STALE with zero FAIL and recovered. | Evidence is mainly serial-log-based. Design A Wi-Fi-loss accepted runs used corrected reconnect behavior. Slow-backend behavior is configuration-sensitive. |
| RQ3: What minimum access rights, token-handling practices, and architectural controls are required to deploy the device according to least-privilege principles? | Architecture comparison, least-privilege/security comparison, RQ3 security strength check, security checklist table | Design B provides the cleaner least-privilege boundary because backend-facing access can be centralized in the gateway and the ESP32 can be limited to a compact read-only summary endpoint. Design A can follow least privilege, but backend-facing access is closer to the ESP32 and therefore harder to isolate. | This is an architectural least-privilege comparison, not penetration testing, enterprise IAM, or a full production security audit. |

## Final support assessment

RQ1 is now supported by:

- reliability evidence from the 24-run validation campaign;
- supplementary API response payload-size measurement;
- supplementary host-side HTTP timing measurement;
- architectural endpoint-complexity comparison.

RQ2 is supported by:

- Wi-Fi-loss validation evidence;
- slow-backend validation evidence;
- backend-down validation evidence;
- stale/fail/recovery state counts;
- accepted recovery to live tail.

RQ3 is supported by:

- Design A versus Design B access-placement comparison;
- token/API-key placement discussion;
- read-only/scoped-access principles;
- security checklist table;
- explicit boundary that no full security audit was performed.

## Final decision

All three research questions are now sufficiently supported for final thesis polishing.

No Design C is needed.

No new full validation campaign is needed.

No additional hardware testing is needed by default.
