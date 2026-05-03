# Final results aggregation

This folder contains thesis-ready aggregation products derived from the frozen A-vs-B validation evidence.

Source inputs:
- experiments/processed/validation-a-vs-b/normal-scenario-serial-summary.csv
- experiments/processed/validation-a-vs-b/wifi-loss-scenario-serial-summary.csv
- experiments/processed/validation-a-vs-b/slow-backend-scenario-serial-summary.csv
- experiments/processed/validation-a-vs-b/backend-down-scenario-serial-summary.csv

Generated outputs:
- final-kpi-combined-runs.csv
- final-kpi-design-scenario-summary.csv
- validation-scenario-matrix.md
- final-kpi-scenario-summary-tables.md
- cross-scenario-observation-table.md

The aggregation uses simple descriptive measures only:
- counts
- means
- ratios
- recovered-live-tail boolean summaries

No raw evidence is modified by this aggregation step.
