# Table 4. Slow-backend results

| Design | Repetitions | Mean stale count | Mean fail count | Mean gateway stale count | Recovered live tail | Main observation |
| --- | --- | --- | --- | --- | --- | --- |
| Design A | 3 | 0 | 0 | N/A | True | Remained live under the chosen proxy-delay method and adjusted timeout |
| Design B | 3 | 62.333 | 3.333 | 62.333 | True | Often exposed STALE state and recovered; one run included a short FAIL pocket |

**Thesis note:** Do not overclaim this result. Design A behavior is configuration-sensitive because the accepted slow-backend runs used an adjusted timeout.
