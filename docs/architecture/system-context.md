# System Context

## Purpose
This document defines the high-level system context for the project.

## Core context
The project is a bounded ESP32 micro-observability proof of concept.

The startup backend baseline includes:
- Docker
- Prometheus
- Node Exporter

Grafana is optional.

## Main comparison
The system compares:
- Design A: ESP32 queries Prometheus directly
- Design B: ESP32 queries a gateway that filters, compacts, or caches before the ESP32 consumes data

## Notes
This document defines the system boundary only. It does not contain implementation conclusions.
