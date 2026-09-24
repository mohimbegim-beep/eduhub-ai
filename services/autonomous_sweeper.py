#!/usr/bin/env python3
"""
EduHub AI — Autonomous System Sweeper & Lifecycle Agent
Role: Background autonomous agent maintaining:
1. Dunning Grace Period enforcement (revoking expired unbilled access).
2. Ephemeral P2P room data destruction (sliding 60-minute privacy guarantee).
3. Periodic disaster-recovery snapshot creation (every 6 hours).
"""

import sys
import os
import time
import json
from pathlib import Path

# Ensure app is importable
_base_dir = Path(__file__).resolve().parent.parent
if str(_base_dir) not in sys.path:
    sys.path.insert(0, str(_base_dir))

from app.main import (
    sweep_expired_dunning_grace_periods,
    purge_expired_peer_data,
    backup_engine,
    record_system_audit_event
)

SWEEPER_STATE_FILE = _base_dir / "data" / "sweeper_state.json"

def run_dunning_sweep() -> dict:
    """Invokes core Dunning sweeper to downgrade unbilled grace accounts."""
    try:
        res = sweep_expired_dunning_grace_periods()
        return res
    except Exception as e:
        print(f"[SWEEPER ERROR] Dunning sweep failed: {e}")
        return {"status": "error", "error": str(e), "swept_count": 0}

def run_ephemeral_peer_sweep() -> dict:
    """Enforces 60-minute ephemeral auto-destruction of peer study rooms."""
    try:
        purge_expired_peer_data()
        return {"status": "success", "action": "ephemeral_messages_purged"}
    except Exception as e:
        print(f"[SWEEPER ERROR] Peer purge failed: {e}")
        return {"status": "error", "error": str(e)}

def run_periodic_snapshot_sweep(max_interval_seconds: int = 21600) -> dict:
    """Ensures regular atomic snapshots of system data at least every 6 hours."""
    try:
        snapshots = backup_engine.list_snapshots()
        need_snapshot = False
        now = time.time()
        
        if not snapshots:
            need_snapshot = True
        else:
            # Check latest snapshot timestamp
            latest = snapshots[0]
            dt_str = latest.get("datetime", "")
            # If we don't have accurate parse, check file mtime
            snap_path = Path(latest.get("path", ""))
            if snap_path.exists():
                mtime = snap_path.stat().st_mtime
                if (now - mtime) > max_interval_seconds:
                    need_snapshot = True
            else:
                need_snapshot = True

        if need_snapshot:
            snap_res = backup_engine.create_snapshot()
            record_system_audit_event("INFO", "AUTONOMOUS_PERIODIC_SNAPSHOT_CREATED", {
                "snapshot_id": snap_res.get("snapshot_id"),
                "reason": "periodic_6h_guarantee"
            })
            return {"status": "success", "snapshot_created": True, "details": snap_res}
        else:
            return {"status": "success", "snapshot_created": False, "reason": "recent_snapshot_exists"}
    except Exception as e:
        print(f"[SWEEPER ERROR] Snapshot sweep failed: {e}")
        return {"status": "error", "error": str(e)}

def run_site_engineer_sweep(max_interval_seconds: int = 21600) -> dict:
    """Invokes Autonomous Site Engineer to audit and heal platform every 6 hours."""
    try:
        from services.autonomous_site_engineer import AutonomousSiteEngineer, STATE_FILE
        need_run = False
        now = time.time()
        
        if not STATE_FILE.exists():
            need_run = True
        else:
            try:
                mtime = STATE_FILE.stat().st_mtime
                if (now - mtime) > max_interval_seconds:
                    need_run = True
            except Exception:
                need_run = True
                
        if need_run:
            engineer = AutonomousSiteEngineer()
            report_summary = engineer.run_full_inspection_cycle()
            return {"status": "success", "executed": True, "details": report_summary}
        else:
            return {"status": "success", "executed": False, "reason": "recent_inspection_fresh"}
    except Exception as e:
        print(f"[SWEEPER ERROR] Site Engineer sweep failed: {e}")
        return {"status": "error", "error": str(e)}

def run_autonomous_sweep() -> dict:
    """Master sweep coordinator running all lifecycle maintenance jobs."""
    start = time.time()
    dunning_res = run_dunning_sweep()
    peer_res = run_ephemeral_peer_sweep()
    snapshot_res = run_periodic_snapshot_sweep()
    engineer_res = run_site_engineer_sweep()

    summary = {
        "status": "success",
        "timestamp": start,
        "duration_ms": round((time.time() - start) * 1000, 2),
        "dunning": dunning_res,
        "peer_rooms": peer_res,
        "snapshot": snapshot_res,
        "site_engineer": engineer_res
    }

    try:
        with open(SWEEPER_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
    except Exception:
        pass

    return summary

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    
    print("=" * 60)
    print("🧹 EDUHUB AI — AUTONOMOUS SYSTEM SWEEPER AGENT")
    print("=" * 60)
    res = run_autonomous_sweep()
    print(json.dumps(res, indent=2, ensure_ascii=False))
