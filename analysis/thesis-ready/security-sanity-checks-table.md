# Practical security sanity checks for RQ3

These checks were performed as practical sanity checks for the tested prototype. They were not penetration testing, vulnerability scanning, or a full production security audit.

| Check | Purpose | Evidence used | Result | Interpretation |
|---|---|---|---|---|
| SEC-1 | Check that committed/shareable files do not expose Wi-Fi passwords, tokens, API keys, or secrets. | grep checks over firmware, gateway, backend, analysis, experiments, docs, README, `.gitignore`, and `.env.example` | PASS | Supports that committed/shareable project files avoid obvious secret exposure. Only empty Wi-Fi placeholders and documentation discussion of secrets/tokens were found. |
| SEC-2 | Check that public repo does not include `.env` or private config. | `find` and `git ls-files` checks in `repo-public` | PASS | Supports public repository hygiene. The only secret-related match was `docs/security/secrets-policy.md`, which is a documentation file. |
| SEC-3 | Check that Design B firmware uses gateway summary endpoint instead of direct Prometheus query URLs. | `firmware/design_b` grep inspection | PASS | Supports that the ESP32 in Design B only needs the gateway summary endpoint. |
| SEC-4 | Check that gateway exposes fixed `/api/v1/summary` endpoint. | Gateway route inspection and `curl` runtime test | PASS | Supports a controlled ESP32-facing API surface. The runtime endpoint returned JSON with `state` and `metrics`. |
| SEC-5 | Check that gateway does not expose arbitrary Prometheus query access to ESP32. | Gateway route inspection and negative `curl` tests | PASS | Supports the query-control boundary in Design B. `/api/v1/query?query=up` and `/query?query=up` returned 404; `/api/v1/summary?query=up` returned the normal summary response. |
| SEC-6 | Check that Design A requires direct Prometheus endpoint knowledge. | `firmware/design_a` grep inspection | PASS | Confirms that Design A places backend-facing Prometheus query knowledge on the ESP32. |
| SEC-7 | Check that Design B separates backend-facing Prometheus access into the gateway. | `firmware/design_b` and `gateway/app` inspection | PASS | Confirms that Design B moves Prometheus-facing responsibility away from the ESP32 and into the gateway. |

## Notes

- These checks are limited to the tested prototype and repository state.
- The checks do not prove production security.
- No penetration testing or vulnerability scanning was performed.
- The result supports the architectural least-privilege comparison between Design A and Design B.
- The correct interpretation is that Design B gave a cleaner least-privilege boundary in the tested prototype because the ESP32 used a fixed summary endpoint while the gateway handled Prometheus-facing access.
