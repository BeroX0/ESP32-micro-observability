# Design B

## Purpose
This document describes the gateway-assisted design path.

## Definition
In Design B, the ESP32 queries a gateway instead of querying Prometheus directly.

The gateway may:
- filter
- compact
- cache

before returning data to the ESP32.

## Intended use
This design acts as the mediated comparison path.

## Notes
Gateway language, exact API contract, and final access-control mechanism remain open until verified.
