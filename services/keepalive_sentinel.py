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
from datetime import datetime, timezone

TARGET_URL = "https://eduhub-ai.onrender.com/health"
PING_INTERVAL_SECONDS = 540  # 9 minutes (Render sleeps after 15 minutes)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

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
    except Exception as e:
        print(f"[{now_str}] ⚠️ PING WARNING: {e}")

if __name__ == "__main__":
    print(f"[*] EduHub Keep-Alive Sentinel started. Target: {TARGET_URL}")
    print(f"[*] Interval: every {PING_INTERVAL_SECONDS // 60} minutes.")
    while True:
        ping()
        time.sleep(PING_INTERVAL_SECONDS)