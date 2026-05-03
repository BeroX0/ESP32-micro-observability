# Backend-down first summary

This note summarizes the accepted backend-down runs for Design A and Design B.

Accepted runs:
- Design A r1
- Design B r1
- Design A r2
- Design B r2
- Design A r3
- Design B r3

Timing used:
- 30s healthy pre-state
- 90s Prometheus stopped
- 90s Prometheus restored
- 210s total capture

Injection method:
- Prometheus container stopped and restarted during the capture window
- Design A used direct Prometheus access
- Design B used the normal gateway endpoint

Main observed pattern:
- Design A entered FAIL during backend outage and recovered to LIVE after Prometheus was restored
- Design B primarily entered STALE during backend outage and recovered to LIVE after Prometheus was restored
- Design B showed no FAIL in the accepted backend-down repetitions

Processing basis:
- serial log evidence
- operator event notes
- Prometheus stop/start event markers

Caveat:
- this is the first processed scenario summary
- final KPI aggregation still remains
