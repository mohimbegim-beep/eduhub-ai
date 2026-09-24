#!/usr/bin/env python3
"""
EduHub AI — Translation Integrity & Type Safety Checker
Verifies that all language files (uz.json, ru.json, es.json) contain all keys
defined in the canonical en.json. Reports missing keys to ensure 100% UI safety.
"""
import json
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
CANONICAL_LOCALE = "en.json"
TARGET_LOCALES = ["uz.json", "ru.json", "es.json"]

def check_translations():
    canonical_file = LOCALES_DIR / CANONICAL_LOCALE
    if not canonical_file.exists():
        print(f"[ERROR] Canonical locale file not found: {canonical_file}")
        sys.exit(1)

    with open(canonical_file, "r", encoding="utf-8") as f:
        en_dict = json.load(f)

    en_keys = set(en_dict.keys())
    print(f"[OK] Canonical locale ({CANONICAL_LOCALE}) loaded with {len(en_keys)} translation keys.")

    all_valid = True
    for target in TARGET_LOCALES:
        target_file = LOCALES_DIR / target
        if not target_file.exists():
            print(f"[MISSING] Target file missing: {target}")
            all_valid = False
            continue

        with open(target_file, "r", encoding="utf-8") as f:
            target_dict = json.load(f)

        target_keys = set(target_dict.keys())
        missing = en_keys - target_keys
        extra = target_keys - en_keys

        coverage = ((len(en_keys) - len(missing)) / len(en_keys)) * 100
        print(f"\n--- Checking {target} ---")
        print(f"  Keys present: {len(target_keys)} / {len(en_keys)} ({coverage:.1f}% coverage)")
        
        if missing:
            print(f"  [WARN] Missing {len(missing)} keys (will gracefully fallback to English in UI):")
            for k in list(missing)[:10]:
                print(f"    - {k}")
            if len(missing) > 10:
                print(f"    ... and {len(missing) - 10} more.")
        else:
            print(f"  [OK] 100% keys present! Complete coverage.")

    return all_valid

if __name__ == "__main__":
    check_translations()
