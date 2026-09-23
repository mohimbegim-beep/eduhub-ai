import os
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def verify_phase1():
    print("==================================================")
    print("🔍 VERIFYING PHASE 1 IMPLEMENTATION")
    print("==================================================")
    
    routes = [
        ("/privacy", "Privacy Policy"),
        ("/terms", "Terms of Service"),
        ("/refund", "Refund Policy"),
        ("/payment-success", "Payment Successful"),
        ("/", "EduHub AI")
    ]
    
    all_ok = True
    for route, expected_text in routes:
        try:
            req = client.get(route)
            html = req.text
            status = req.status_code
            has_expected = expected_text.lower() in html.lower()
            icon = "✅" if (status == 200 and has_expected) else "❌"
            print(f"{icon} Route '{route}': HTTP {status}, Found '{expected_text}': {has_expected} ({len(html)} bytes)")
            if status != 200 or not has_expected:
                all_ok = False
        except Exception as e:
            print(f"❌ Route '{route}': Error {e}")
            all_ok = False
            
    # Verify Catalog $1 Trial offer
    print("\n--- Catalog & Trial Offer Verification ---")
    try:
        cat_req = client.get("/api/v1/catalog/products")
        cat_data = cat_req.json()
        pro_max = cat_data["tiers"]["pro_max"]
        trial = pro_max.get("trial", {})
        trial_ok = trial.get("enabled") is True and trial.get("intro_price_usd") == 1.0 and trial.get("duration_days") == 3
        icon = "✅" if trial_ok else "❌"
        print(f"{icon} Pro Max Trial Config: enabled={trial.get('enabled')}, price=${trial.get('intro_price_usd')}, days={trial.get('duration_days')}")
        print(f"   Checkout URL: {pro_max.get('checkout_url')}")
        if not trial_ok:
            all_ok = False
    except Exception as e:
        print(f"❌ Catalog Error: {e}")
        all_ok = False

    # Verify Landing Page UI triggers
    print("\n--- Landing Page UI Triggers Verification ---")
    try:
        index_req = client.get("/")
        index_html = index_req.text
        has_hero_badge = "3-Day Pro Access" in index_html or "$1" in index_html
        has_clean_checkout = "checkout-trigger-btn" in index_html and "lemon" not in index_html.lower()
        has_trial_button = "checkout" in index_html
        has_footer_links = ('href="/terms"' in index_html and 'href="/privacy"' in index_html and 'href="/refund"' in index_html)
        
        print(f"{'✅' if has_hero_badge else '❌'} Hero $1 Trial Badge: {has_hero_badge}")
        print(f"{'✅' if has_clean_checkout else '❌'} White-Hat SaaS Checkout: {has_clean_checkout}")
        print(f"{'✅' if has_trial_button else '❌'} Trial Checkout Link: {has_trial_button}")
        print(f"{'✅' if has_footer_links else '❌'} Direct Footer Anchor Links (/terms, /privacy, /refund): {has_footer_links}")
        
        if not (has_hero_badge and has_clean_checkout and has_trial_button and has_footer_links):
            all_ok = False
    except Exception as e:
        print(f"❌ Index Check Error: {e}")
        all_ok = False

    print("\n==================================================")
    if all_ok:
        print("🎉 ALL PHASE 1 REQUIREMENTS VERIFIED SUCCESSFULLY (100%)")
    else:
        print("⚠️ SOME PHASE 1 CHECKS FAILED")
    print("==================================================")
    return all_ok

if __name__ == "__main__":
    success = verify_phase1()
    sys.exit(0 if success else 1)
