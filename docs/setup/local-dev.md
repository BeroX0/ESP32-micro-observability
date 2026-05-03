# Local Development Setup

## Purpose
This document explains the verified local backend bootstrap path for the project.

## Verified local baseline
The verified local baseline uses:
- Docker Desktop on Windows
- Ubuntu in WSL
- Docker Compose
- Prometheus
- Node Exporter

Grafana is optional and was not required for this bootstrap verification.

## Verified env behavior
A local `.env` file is required.
The Compose path used in this repo must be called with an explicit env-file:

- `docker compose --env-file .env -f backend/compose/compose.core.yml ...`

Using the compose file without the explicit env-file did not apply the intended fixed host ports in this environment.

## Verified startup commands
From the repo root:

- `make up-core`
- `make ps`
- `make down-core`

## Verified results
The following was verified on the local machine:
- Prometheus reachable on `http://localhost:9090`
- Node Exporter reachable on `http://localhost:9100`
- Prometheus target `node_exporter` reported as `up`
- Sample metric queries returned real values for CPU, memory, and filesystem availability

## Notes
This document should contain only verified local setup instructions and observed bootstrap behavior.
