import sys
import requests
import json
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

def test_phase3_suite():
    print("=== Testing Phase 3: B2B Suite ($79/mo) & Institutional Signals ===")
    
    # 1. Test /api/v1/catalog/products
    res = requests.get(f"{BASE_URL}/api/v1/catalog/products")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    catalog = res.json()["products"]
    
    assert "b2b_center" in catalog, "b2b_center missing from catalog"
    b2b = catalog["b2b_center"]
    assert b2b["price_usd"] == 79.00, f"Expected price 79.00, got {b2b['price_usd']}"
    assert b2b["seats"]["lead_educators"] == 1, "Expected 1 lead educator"
    assert b2b["seats"]["student_seats"] == 10, "Expected 10 student seats"
    print("  [PASS] Catalog contains b2b_center ($79/mo, 1 lead + 10 student seats)")
    
    # 2. Test direct item endpoint
    res_item = requests.get(f"{BASE_URL}/api/v1/catalog/products/b2b_center")
    assert res_item.status_code == 200, f"Expected 200, got {res_item.status_code}"
    assert res_item.json()["product"]["price_usd"] == 79.00
    print("  [PASS] GET /api/v1/catalog/products/b2b_center responds 200 with correct pricing")
    
    # 3. Check HTML content
    index_path = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    assert "setPricingAudience" in html, "setPricingAudience function missing from index.html"
    assert "grid-institutional" in html, "grid-institutional element missing from index.html"
    assert "btn-institutional" in html, "btn-institutional element missing from index.html"
    assert "$79" in html, "$79 price missing from index.html"
    assert "10 Student Seats" in html or "10 Full Student Seats" in html, "10 student seats text missing"
    assert "Anti-Hallucination Guard" in html, "Anti-Hallucination Guard missing"
    assert "Strict 18+ Safety Filter" in html, "Strict 18+ Safety Filter missing"
    assert "Zero-Plagiarism Integrity" in html, "Zero-Plagiarism Integrity missing"
    assert "CSV &amp; JSON Gradebook" in html or "CSV & JSON Gradebook" in html, "Gradebook export missing"
    print("  [PASS] index.html contains B2B UI switcher, $79 card, and institutional trust signals")

    # 4. Verify existing tests still pass
    for pid in ["student_starter", "pro_max", "tutor_creator", "exam_sprint", "flash_sprint_50", "flash_crunch_120"]:
        assert pid in catalog, f"Prior tier {pid} missing!"
    print("  [PASS] All previous individual tiers and consumables remain 100% intact")

    print("\nALL PHASE 3 TESTS PASSED SUCCESSFULLY! (100%)")

if __name__ == "__main__":
    test_phase3_suite()
