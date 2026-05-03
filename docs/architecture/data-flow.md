# Data Flow

## Purpose
This document describes the high-level data movement for the startup project baseline.

## Startup flow
- Node Exporter exposes host metrics
- Prometheus scrapes Node Exporter
- Design A reads from Prometheus directly
- Design B reads from a gateway that reads from Prometheus

## Startup metric focus
- CPU
- memory
- disk
- basic network/connectivity
- last successful update timestamp

## Notes
This document is a structural overview only and does not define final implementation details.
