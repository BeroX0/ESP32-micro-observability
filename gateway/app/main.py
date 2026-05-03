import os
import time
from typing import Any, Dict

import requests
from fastapi import FastAPI, HTTPException

PROM_URL = os.getenv("PROMETHEUS_BASE_URL", "http://localhost:9090")
CACHE_TTL_SECONDS = float(os.getenv("CACHE_TTL_SECONDS", "5"))
UPSTREAM_TIMEOUT_SECONDS = float(os.getenv("UPSTREAM_TIMEOUT_SECONDS", "1.5"))

CPU_QUERY = '100 * sum(rate(node_cpu_seconds_total{job="node_exporter",mode!="idle"}[5m])) / count(count(node_cpu_seconds_total{job="node_exporter",mode="idle"}) by (cpu))'
MEM_QUERY = '100 * (1 - (node_memory_MemAvailable_bytes{job="node_exporter"} / node_memory_MemTotal_bytes{job="node_exporter"}))'
DISK_QUERY = '100 * (1 - (node_filesystem_avail_bytes{job="node_exporter",mountpoint="/etc/hosts"} / node_filesystem_size_bytes{job="node_exporter",mountpoint="/etc/hosts"}))'
CONN_QUERY = 'up{job="node_exporter"}'
RX_QUERY = 'rate(node_network_receive_bytes_total{job="node_exporter",device="eth0"}[5m])'
TX_QUERY = 'rate(node_network_transmit_bytes_total{job="node_exporter",device="eth0"}[5m])'
LAST_UPDATE_QUERY = 'timestamp(up{job="node_exporter"})'

app = FastAPI()

cache: Dict[str, Any] = {
    "payload": None,
    "fetched_at": 0.0,
    "last_live_payload": None,
    "last_live_at": 0.0,
}

def prom_scalar(query: str) -> float:
    r = requests.get(
        f"{PROM_URL}/api/v1/query",
        params={"query": query},
        timeout=UPSTREAM_TIMEOUT_SECONDS,
    )
    r.raise_for_status()
    body = r.json()
    result = body["data"]["result"]
    if not result:
        raise ValueError(f"empty result for query: {query}")
    return float(result[0]["value"][1])

def build_live_payload() -> Dict[str, Any]:
    now = time.time()

    payload = {
        "host": "local-node",
        "state": "live",
        "generated_at_ts": int(now),
        "source_last_successful_update_ts": int(prom_scalar(LAST_UPDATE_QUERY)),
        "freshness_seconds": 0,
        "metrics": {
            "cpu_percent": prom_scalar(CPU_QUERY),
            "memory_percent": prom_scalar(MEM_QUERY),
            "disk_percent": prom_scalar(DISK_QUERY),
            "connectivity_up": int(prom_scalar(CONN_QUERY)),
            "network_rx_bps": prom_scalar(RX_QUERY),
            "network_tx_bps": prom_scalar(TX_QUERY),
        },
    }
    payload["freshness_seconds"] = max(
        0, int(payload["generated_at_ts"] - payload["source_last_successful_update_ts"])
    )
    return payload

@app.get("/api/v1/summary")
def summary() -> Dict[str, Any]:
    now = time.time()

    if cache["payload"] is not None and (now - cache["fetched_at"] <= CACHE_TTL_SECONDS):
        return cache["payload"]

    try:
        payload = build_live_payload()
        cache["payload"] = payload
        cache["fetched_at"] = now
        cache["last_live_payload"] = payload
        cache["last_live_at"] = now
        return payload
    except Exception:
        if cache["last_live_payload"] is not None:
            stale_payload = dict(cache["last_live_payload"])
            stale_payload["state"] = "stale"
            stale_payload["generated_at_ts"] = int(now)
            stale_payload["freshness_seconds"] = max(
                stale_payload.get("freshness_seconds", 0),
                int(now - cache["last_live_at"]),
            )
            cache["payload"] = stale_payload
            cache["fetched_at"] = now
            return stale_payload
        raise HTTPException(status_code=503, detail="gateway has no cached data yet")
