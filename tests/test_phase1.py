import urllib.request
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
        url = f"http://127.0.0.1:8000{route}"
        try:
            req = urllib.request.urlopen(url, timeout=5)
            html = req.read().decode("utf-8")
            status = req.status
            has_expected = expected_text in html
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
        cat_req = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/catalog/products", timeout=5)
        cat_data = json.loads(cat_req.read().decode("utf-8"))
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
        index_req = urllib.request.urlopen("http://127.0.0.1:8000/", timeout=5)
        index_html = index_req.read().decode("utf-8")
        has_hero_badge = "Start 3-Day Pro Access for Just $1" in index_html
        has_lemon_js = "checkout-trigger-btn" in index_html and "lemonsqueezy" not in index_html.lower()
        has_trial_button = "checkout[trial]=true" in index_html
        has_footer_links = ('href="/terms"' in index_html and 'href="/privacy"' in index_html and 'href="/refund"' in index_html)
        
        print(f"{'✅' if has_hero_badge else '❌'} Hero $1 Trial Badge: {has_hero_badge}")
        print(f"{'✅' if has_lemon_js else '❌'} White-Hat SaaS Checkout: {has_lemon_js}")
        print(f"{'✅' if has_trial_button else '❌'} Trial Checkout Link with query params: {has_trial_button}")
        print(f"{'✅' if has_footer_links else '❌'} Direct Footer Anchor Links (/terms, /privacy, /refund): {has_footer_links}")
        
        if not (has_hero_badge and has_lemon_js and has_trial_button and has_footer_links):
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
