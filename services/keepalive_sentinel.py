#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EduHub AI — 24/7 Keep-Alive Sentinel Daemon
Pings the Render production endpoint every 9 minutes (540 seconds)
to prevent the free-tier container from falling into a 15-minute sleep.
"""
import time
import urllib.request
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
TARGET_URL = "https://eduhub-ai.onrender.com/health"
PING_INTERVAL_SECONDS = 540  # 9 minutes (Render sleeps after 15 minutes)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def save_sentinel_telemetry(success: bool, status_code: int = 0, latency_ms: float = 0.0, error: str = None):
    try:
        data_file = BASE_DIR / "data" / "sentinel_status.json"
        data_file.parent.mkdir(parents=True, exist_ok=True)
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        payload = {
            "status": "active" if success else "warning",
            "is_daemon_alive": True,
            "target_url": TARGET_URL,
            "interval_seconds": PING_INTERVAL_SECONDS,
            "last_ping_utc": now_str,
            "last_status_code": status_code,
            "latency_ms": round(latency_ms, 1),
            "success": success,
            "error": error
        }
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception as ex:
        print(f"[SENTINEL TELEMETRY WARNING] {ex}")

def ping():
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        req = urllib.request.Request(
            TARGET_URL,
            headers={"User-Agent": "EduHub-KeepAlive-Sentinel/2.0"}
        )
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=45) as res:
            latency = (time.time() - t0) * 1000
            print(f"[{now_str}] 🟢 KEEP-ALIVE OK: HTTP {res.status} ({latency:.1f}ms) -> {TARGET_URL}")
            save_sentinel_telemetry(True, status_code=res.status, latency_ms=latency)
    except Exception as e:
        print(f"[{now_str}] ⚠️ PING WARNING: {e}")
        save_sentinel_telemetry(False, status_code=0, error=str(e))

if __name__ == "__main__":
    print(f"[*] EduHub Keep-Alive Sentinel started. Target: {TARGET_URL}")
    print(f"[*] Interval: every {PING_INTERVAL_SECONDS // 60} minutes.")
    while True:
        ping()
        time.sleep(PING_INTERVAL_SECONDS)