# Data Handling

## Purpose
This document defines where experimental evidence should be placed and what belongs in Git.

## Recommended placement
- scenario definitions: `experiments/scenarios/`
- run plans: `experiments/plans/`
- raw evidence: `experiments/raw/`
- processed outputs: `experiments/processed/`
- factual run notes: `experiments/notes/`
- compact summaries: `experiments/summaries/`

## Goes in Git
- source code
- configs without secrets
- setup and structure docs
- scenario definitions
- experiment plans
- evidence notes
- selected meaningful screenshots
- processed outputs that support reproducible reporting
- small sample fixtures

## Does not go in Git
- secrets
- local `.env`
- large disposable raw dumps
- temporary caches
- build artifacts
- editor junk
- redundant screenshots

## Notes
Keep stored evidence small, traceable, and useful.
