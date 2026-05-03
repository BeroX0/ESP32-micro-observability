# Wi-Fi loss first summary

This note summarizes the first accepted Wi-Fi-loss runs for Design A and Design B.

Accepted runs:
- Design A r1 fixed-long
- Design B r1 long
- Design A r2 long
- Design B r2 long
- Design A r3 redo long
- Design B r3 long

Timing used:
- 30s healthy pre-state
- 90s interrupted connectivity
- 180s restored observation
- 300s total capture

Main observed pattern:
- Design A entered FAIL during outage and later recovered to LIVE after Wi-Fi restore
- Design B remained mainly STALE during outage and later returned to LIVE after restore

Processing basis:
- serial log evidence
- operator event notes
- manual Wi-Fi cut/restore timing

Caveat:
- this is a first processed scenario summary
- final KPI aggregation and comparison tables still remain
