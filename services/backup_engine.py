#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
EduMate AI — Automated Data Shield and Backup Engine
===============================================================================
Обеспечивает атомарную запись JSON-файлов данных, создание снапшотов
состояния системы и автоматическую ротацию резервных копий.
===============================================================================
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = DATA_DIR / "backups"

TARGET_FILES = [
    "user_balances.json",
    "billing_transactions.json",
    "disputes.json",
    "visitor_analytics.json",
    "archived_lemon_transactions.json"
]

def atomic_write_json(file_path: Path, data: Any, indent: int = 2) -> bool:
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_file = file_path.with_suffix(".tmp")
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, file_path)
        return True
    except Exception as e:
        print(f"[BACKUP ENGINE ERROR] Failed atomic write for {file_path}: {e}")
        return False

class BackupEngine:
    def __init__(self, data_dir: Path = DATA_DIR, backup_dir: Path = BACKUP_DIR, max_snapshots: int = 14):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.max_snapshots = max_snapshots

    def create_snapshot(self) -> Dict[str, Any]:
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        snapshot_folder = self.backup_dir / f"snapshot_{timestamp_str}"
        snapshot_folder.mkdir(parents=True, exist_ok=True)

        copied_files = []
        errors = []

        # 1. Hot Backup of SQLite WAL Database
        db_file = self.data_dir / "eduhub.db"
        if db_file.exists():
            try:
                import sqlite3
                src_conn = sqlite3.connect(str(db_file), timeout=5.0)
                src_conn.execute("PRAGMA wal_checkpoint(PASSIVE);")
                dst_db = snapshot_folder / "eduhub.db"
                dst_conn = sqlite3.connect(str(dst_db))
                src_conn.backup(dst_conn)
                dst_conn.close()
                src_conn.close()
                copied_files.append("eduhub.db")
            except Exception as dbe:
                errors.append(f"eduhub.db: {str(dbe)}")

        # 2. JSON State Snapshots
        for filename in TARGET_FILES:
            src = self.data_dir / filename
            if src.exists():
                try:
                    with open(src, "r", encoding="utf-8") as f:
                        json.load(f)
                    dst = snapshot_folder / filename
                    shutil.copy2(src, dst)
                    copied_files.append(filename)
                except Exception as e:
                    errors.append(f"{filename}: {str(e)}")

        import hashlib
        checksums = {}
        for fname in copied_files:
            fpath = snapshot_folder / fname
            if fpath.exists():
                h = hashlib.sha256()
                with open(fpath, "rb") as bf:
                    while chunk := bf.read(65536):
                        h.update(chunk)
                checksums[fname] = h.hexdigest()

        meta = {
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "files": copied_files,
            "checksums_sha256": checksums,
            "offsite_region": os.getenv("BACKUP_S3_REGION", "eu-central-1"),
            "storage_class": "STANDARD_IA",
            "errors": errors
        }
        with open(snapshot_folder / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        self._rotate_snapshots()

        return {
            "status": "success" if copied_files else "empty",
            "snapshot_id": snapshot_folder.name,
            "files_backed_up": copied_files,
            "checksums_sha256": checksums,
            "errors": errors
        }

    def verify_restore_integrity(self, snapshot_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Non-destructive verification of snapshot recoverability.
        Validates SHA-256 checksums, JSON parseability, and SQLite integrity check from backup without altering production.
        """
        import hashlib
        snapshots = self.list_snapshots()
        if not snapshots:
            return {"status": "error", "message": "No snapshots available to verify"}
        target = snapshots[0]["path"] if not snapshot_id else str(self.backup_dir / snapshot_id)
        target_path = Path(target)
        if not target_path.exists():
            return {"status": "error", "message": f"Snapshot {snapshot_id} not found"}

        verified_files = []
        errors = []

        manifest_file = target_path / "manifest.json"
        manifest_meta = {}
        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as mf:
                    manifest_meta = json.load(mf)
            except Exception as me:
                errors.append(f"Manifest read error: {me}")

        expected_checksums = manifest_meta.get("checksums_sha256", {})

        # Check JSON files and verify SHA-256
        for f in target_path.iterdir():
            if f.name == "manifest.json":
                continue
            if f.is_file():
                # Verify SHA-256
                if f.name in expected_checksums:
                    h = hashlib.sha256()
                    with open(f, "rb") as bf:
                        while chunk := bf.read(65536):
                            h.update(chunk)
                    actual_hash = h.hexdigest()
                    if actual_hash != expected_checksums[f.name]:
                        errors.append(f"SHA-256 checksum mismatch for {f.name}")
                    else:
                        verified_files.append(f"{f.name} (SHA-256 verified)")
                else:
                    verified_files.append(f.name)

            if f.suffix == ".json" and f.name != "manifest.json":
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        json.load(fp)
                except Exception as ex:
                    errors.append(f"Corrupt JSON in {f.name}: {ex}")

        # Check SQLite db integrity
        bak_db = target_path / "eduhub.db"
        if bak_db.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(bak_db))
                cur = conn.cursor()
                cur.execute("PRAGMA integrity_check;")
                res = cur.fetchone()
                conn.close()
                if res and res[0] == "ok":
                    verified_files.append("eduhub.db (integrity: ok)")
                else:
                    errors.append(f"SQLite integrity check failed: {res}")
            except Exception as sqe:
                errors.append(f"SQLite restore check error: {sqe}")

        return {
            "status": "verified" if not errors else "degraded",
            "snapshot_id": target_path.name,
            "verified_files": verified_files,
            "errors": errors,
            "integrity_passed": len(errors) == 0
        }

    def _rotate_snapshots(self) -> None:
        try:
            snapshots = sorted([
                d for d in self.backup_dir.iterdir()
                if d.is_dir() and d.name.startswith("snapshot_")
            ], key=lambda d: d.stat().st_mtime)

            while len(snapshots) > self.max_snapshots:
                oldest = snapshots.pop(0)
                shutil.rmtree(oldest, ignore_errors=True)
                print(f"[BACKUP ENGINE] Pruned old snapshot: {oldest.name}")
        except Exception as e:
            print(f"[BACKUP ENGINE ERROR] Rotation error: {e}")

    def list_snapshots(self) -> List[Dict[str, Any]]:
        if not self.backup_dir.exists():
            return []
        results = []
        for d in sorted(self.backup_dir.iterdir(), key=lambda d: d.stat().st_mtime, reverse=True):
            if d.is_dir() and d.name.startswith("snapshot_"):
                manifest = d / "manifest.json"
                meta = {}
                if manifest.exists():
                    try:
                        with open(manifest, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                    except Exception:
                        pass
                results.append({
                    "snapshot_id": d.name,
                    "datetime": meta.get("datetime", "Unknown"),
                    "files": meta.get("files", []),
                    "path": str(d)
                })
        return results

backup_engine = BackupEngine()

if __name__ == "__main__":
    res = backup_engine.create_snapshot()
    print("Snapshot created successfully:", res)
