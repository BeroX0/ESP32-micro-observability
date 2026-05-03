# Naming Conventions

## Purpose
This document defines simple naming rules for scenarios, runs, screenshots, and processed outputs.

## Scenario IDs
- `SCN-<area>-<name>`

## Run IDs
- `RUN-YYYYMMDD-HHMM-<shorttag>`

## Screenshot names
- `YYYYMMDD-HHMM_<subject>.png`

Example:
- `20260326-1618_prometheus-targets.png`

## Processed result names
Use one of:
- `YYYYMMDD_<subject>_<source-run-or-scenario>.csv`
- `YYYYMMDD_<subject>_<source-run-or-scenario>.md`

Examples:
- `20260326_target-status_RUN-20260326-1615-bootstrap.md`
- `20260326_memory_summary_SCN-BOOTSTRAP-LOCAL.csv`

## Evidence note names
Use one of:
- `<topic>-verified.md`
- `<scenario-id>__<run-id>.md`

Examples:
- `backend-bootstrap-verified.md`
- `SCN-BOOTSTRAP-LOCAL__RUN-20260326-1615-bootstrap.md`

## Notes
Keep names readable, stable, and traceable.
