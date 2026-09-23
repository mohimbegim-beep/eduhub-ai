#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
EduHub AI — Automated Data Shield and Backup Engine
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

        meta = {
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "files": copied_files,
            "errors": errors
        }
        with open(snapshot_folder / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        self._rotate_snapshots()

        return {
            "status": "success" if copied_files else "empty",
            "snapshot_id": snapshot_folder.name,
            "files_backed_up": copied_files,
            "errors": errors
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
