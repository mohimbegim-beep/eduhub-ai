import sys
import os
import json
import subprocess
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_phase4_suite():
    print("==================================================")
    print("🔍 VERIFYING PHASE 4: AUTONOMOUS TREND SCOUT & SYNC")
    print("==================================================")

    # 1. Test running scout.py --run-once
    print("\n--- 1. Executing scout.py --run-once ---")
    scout_script = os.path.join(BASE_DIR, "services", "trend_scout", "scout.py")
    res = subprocess.run([sys.executable, scout_script, "--run-once"], capture_output=True, text=True, encoding="utf-8")
    assert res.returncode == 0, f"scout.py failed with returncode {res.returncode}:\n{res.stderr}\n{res.stdout}"
    assert "TOP EXTRACTED EDTECH TRENDS" in res.stdout, "Expected output header not found"
    print("  [PASS] scout.py --run-once completed successfully (exit code 0)")

    # 2. Verify data/dynamic_trends.json
    print("\n--- 2. Verifying data/dynamic_trends.json ---")
    trends_file = os.path.join(BASE_DIR, "data", "dynamic_trends.json")
    assert os.path.exists(trends_file), f"{trends_file} does not exist"
    with open(trends_file, "r", encoding="utf-8") as f:
        trends_data = json.load(f)

    assert "trends" in trends_data and len(trends_data["trends"]) >= 3, "Expected at least 3 trends"
    assert "top_keywords" in trends_data and len(trends_data["top_keywords"]) > 0, "Expected top_keywords list"
    assert "updated_at" in trends_data, "Expected updated_at timestamp"

    top3 = trends_data["trends"][:3]
    print(f"  [PASS] Found {len(trends_data['trends'])} trends in JSON store:")
    for idx, t in enumerate(top3, 1):
        print(f"    Trend #{idx}: {t.get('title')} ({t.get('search_growth')}) - Category: {t.get('category')}")

    # 3. Verify REST API /api/v1/trends/latest
    print("\n--- 3. Verifying REST API GET /api/v1/trends/latest ---")
    api_res = requests.get(f"{BASE_URL}/api/v1/trends/latest", timeout=5)
    assert api_res.status_code == 200, f"Expected HTTP 200, got {api_res.status_code}"
    api_data = api_res.json()
    assert "trends" in api_data and len(api_data["trends"]) >= 3, "API returned incomplete trends"
    assert api_data["trends"][0]["id"] == trends_data["trends"][0]["id"], "API trends do not match JSON file"
    print(f"  [PASS] /api/v1/trends/latest returned HTTP 200 with {len(api_data['trends'])} trends")

    # 4. Verify Landing Page DOM Sync
    print("\n--- 4. Verifying Landing Page (static/index.html) Sync ---")
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert 'id="trending-banner"' in html, "Trending banner missing in index.html"
    assert 'id="trending-topic"' in html, "Trending topic span missing in index.html"
    top_title = top3[0]["title"]
    assert top_title in html, f"Top trend title '{top_title}' not rendered in index.html"

    # Meta keywords check
    assert '<meta name="keywords"' in html, "Meta keywords tag missing"
    top_kw = trends_data["top_keywords"][0]
    assert top_kw in html, f"Top keyword '{top_kw}' not found in meta tags"
    print("  [PASS] Landing page contains trending banner, live topic, and updated meta keywords")

    # 5. Check Cloudflare Tunnel or local HTTP 200 status
    print("\n--- 5. Verifying Web Service HTTP 200 Availability ---")
    home_res = requests.get(f"{BASE_URL}/", timeout=5)
    assert home_res.status_code == 200, f"Landing page returned {home_res.status_code}"
    print(f"  [PASS] Local service responding HTTP {home_res.status_code} ({len(home_res.text)} bytes)")

    print("\n==================================================")
    print("🎉 ALL PHASE 4 REQUIREMENTS VERIFIED SUCCESSFULLY (100%)")
    print("==================================================")
    return True

if __name__ == "__main__":
    success = test_phase4_suite()
    sys.exit(0 if success else 1)
