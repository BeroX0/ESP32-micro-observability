# Secrets Policy

## Purpose
This document defines the basic handling policy for secrets and sensitive local configuration.

## Rules
Do not commit:
- local `.env`
- tokens
- passwords
- private keys
- secret connection strings

It is acceptable to commit:
- `.env.example`
- non-secret config
- public setup instructions
- neutral structure documentation

## Notes
This policy is a practical repo rule, not a final security architecture statement.
