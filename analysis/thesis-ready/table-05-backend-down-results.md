# Table 5. Backend-down results

| Design | Repetitions | Mean stale count | Mean fail count | Mean gateway stale count | Recovered live tail | Main observation |
| --- | --- | --- | --- | --- | --- | --- |
| Design A | 3 | 3.667 | 14.667 | N/A | True | Entered FAIL during Prometheus outage and recovered after restart |
| Design B | 3 | 82.333 | 0 | 82.333 | True | Stayed mainly STALE with zero FAIL and recovered to live |

**Thesis note:** This is one of the strongest architecture findings and should not be buried.
