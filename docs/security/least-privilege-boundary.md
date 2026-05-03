# Least-Privilege Boundary

## Purpose
This document records the least-privilege boundary that later implementation and validation work should respect.

## Boundary direction
The project should avoid giving broader access than required for the ESP32 use case.

Key boundary questions include:
- whether the ESP32 should access Prometheus directly
- whether a gateway should reduce exposure
- what data should be visible to the device
- what operations should be impossible from the device side

## Notes
This document defines boundary intent only. Final mechanisms remain open until verified.
