# Table 3. Wi-Fi-loss results

| Design | Repetitions | Mean Wi-Fi down count | Mean stale count | Mean fail count | Mean gateway stale count | Recovered live tail | Main observation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Design A | 3 | 154 | 13 | 139.333 | N/A | True | FAIL periods occurred during outage, but accepted runs recovered after reconnect fix |
| Design B | 3 | 178 | 182.333 | 0 | 182.333 | True | STALE behavior dominated and no FAIL occurred in accepted runs |

**Thesis note:** This table should mention that Design A accepted runs used the corrected reconnect behavior.
