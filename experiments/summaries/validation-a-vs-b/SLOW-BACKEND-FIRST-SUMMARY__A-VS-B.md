# Slow backend first summary

This note summarizes the accepted slow-backend runs for Design A and Design B.

Accepted runs:
- Design A r1
- Design B r1
- Design A r2
- Design B r2
- Design A r3
- Design B r3

Timing used:
- 30s healthy pre-state
- 90s injected backend delay
- 90s restored normal timing
- 210s total capture

Injection method:
- shared delayed proxy on port 9091
- 0 ms -> 2000 ms -> 0 ms
- same proxy method used for both designs

Main observed pattern:
- Design A mostly remained LIVE during the delayed phase after timeout was raised to 3000 ms
- Design B often shifted into STALE during the delayed phase and then recovered to LIVE
- one Design B run showed a short FAIL pocket during the delayed period

Processing basis:
- serial log evidence
- operator event notes
- proxy delay control events

Caveat:
- this is the first processed scenario summary
- final KPI aggregation still remains
