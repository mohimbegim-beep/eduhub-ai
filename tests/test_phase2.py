import os
import sys
import json
import time
import hmac
import hashlib
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app, load_user_balances, add_flash_credits, record_daily_ai_call, FAIR_USAGE_DAILY_LIMIT

client = TestClient(app)

def run_phase2_tests():
    print("==================================================")
    print("🔍 VERIFYING PHASE 2: FLASH CREDITS & FAIR USAGE")
    print("==================================================")
    all_ok = True

    # 1. Product Catalog Consumable Packages Check
    res_cat = client.get("/api/v1/catalog/products")
    cat_data = res_cat.json() if res_cat.status_code == 200 else {}
    tiers = cat_data.get("tiers", {})

    has_sprint_50 = "flash_sprint_50" in tiers and tiers["flash_sprint_50"]["price_usd"] == 5.0 and tiers["flash_sprint_50"]["credits"] == 50
    has_crunch_120 = "flash_crunch_120" in tiers and tiers["flash_crunch_120"]["price_usd"] == 10.0 and tiers["flash_crunch_120"]["credits"] == 120

    print(f"{'✅' if has_sprint_50 else '❌'} Catalog: 'Sprint Pack (50 Credits)' ($5.00): {has_sprint_50}")
    print(f"{'✅' if has_crunch_120 else '❌'} Catalog: 'Exam Crunch Pack (120 Credits)' ($10.00): {has_crunch_120}")
    if not (has_sprint_50 and has_crunch_120):
        all_ok = False

    # 2. Credits Endpoint Check
    test_email = f"student_test_{int(time.time())}@eduhub.ai"
    res_credits = client.get(f"/api/v1/user/credits?email={test_email}")
    data_credits = res_credits.json() if res_credits.status_code == 200 else {}
    initial_credits_ok = res_credits.status_code == 200 and data_credits.get("flash_credits") == 0 and data_credits.get("daily_fair_usage_limit") == 60
    print(f"{'✅' if initial_credits_ok else '❌'} User Credits API: Initial state (0 credits, limit 60): {initial_credits_ok}")
    if not initial_credits_ok:
        all_ok = False

    # 3. Webhook Fulfillment: Sprint Pack (50 Credits)
    secret = os.getenv("LEMON_WEBHOOK_SECRET", "default_secret_key_change_me")
    payload_50 = json.dumps({
        "meta": {"event_name": "order_created"},
        "data": {
            "type": "orders",
            "id": f"ord_50_{int(time.time())}",
            "attributes": {
                "user_email": test_email,
                "status": "paid",
                "first_order_item": {
                    "product_name": "Sprint Pack (50 Credits)",
                    "variant_name": "50 Credits"
                }
            }
        }
    }).encode("utf-8")
    sig_50 = hmac.new(secret.encode("utf-8"), payload_50, hashlib.sha256).hexdigest()
    res_wh_50 = client.post(
        "/api/v1/billing/lemon-webhook",
        content=payload_50,
        headers={"X-Signature": sig_50, "Content-Type": "application/json"}
    )
    data_wh_50 = res_wh_50.json() if res_wh_50.status_code == 200 else {}
    wh_50_ok = res_wh_50.status_code == 200 and data_wh_50.get("credits_added") == 50 and data_wh_50.get("new_balance") == 50
    print(f"{'✅' if wh_50_ok else '❌'} Webhook Fulfillment (Sprint 50): status={res_wh_50.status_code}, added={data_wh_50.get('credits_added')}, balance={data_wh_50.get('new_balance')}")
    if not wh_50_ok:
        all_ok = False

    # 4. Webhook Fulfillment: Exam Crunch (120 Credits)
    payload_120 = json.dumps({
        "meta": {"event_name": "order_created"},
        "data": {
            "type": "orders",
            "id": f"ord_120_{int(time.time())}",
            "attributes": {
                "user_email": test_email,
                "status": "paid",
                "first_order_item": {
                    "product_name": "Exam Crunch Pack (120 Credits)",
                    "variant_name": "120 Credits"
                }
            }
        }
    }).encode("utf-8")
    sig_120 = hmac.new(secret.encode("utf-8"), payload_120, hashlib.sha256).hexdigest()
    res_wh_120 = client.post(
        "/api/v1/billing/lemon-webhook",
        content=payload_120,
        headers={"X-Signature": sig_120, "Content-Type": "application/json"}
    )
    data_wh_120 = res_wh_120.json() if res_wh_120.status_code == 200 else {}
    wh_120_ok = res_wh_120.status_code == 200 and data_wh_120.get("credits_added") == 120 and data_wh_120.get("new_balance") == 170
    print(f"{'✅' if wh_120_ok else '❌'} Webhook Fulfillment (Crunch 120): status={res_wh_120.status_code}, added={data_wh_120.get('credits_added')}, balance={data_wh_120.get('new_balance')}")
    if not wh_120_ok:
        all_ok = False

    # 5. Verify User Balance Persistence
    res_check = client.get(f"/api/v1/user/credits?email={test_email}")
    final_balance = res_check.json().get("flash_credits") if res_check.status_code == 200 else 0
    balance_persisted = final_balance == 170
    print(f"{'✅' if balance_persisted else '❌'} Balance Persistence: Stored balance = {final_balance} (Expected 170)")
    if not balance_persisted:
        all_ok = False

    # 6. Fair Usage Policy Guardrail Logic
    fu_email = f"fu_test_{int(time.time())}@eduhub.ai"
    # Call 60 times
    for i in range(FAIR_USAGE_DAILY_LIMIT):
        allowed, remaining = record_daily_ai_call(fu_email)
        assert allowed is True

    # 61st call without credits: should be False
    allowed_61, remaining_61 = record_daily_ai_call(fu_email)
    quota_blocked = (allowed_61 is False and remaining_61 == 0)
    print(f"{'✅' if quota_blocked else '❌'} Fair Usage Guardrail: 61st call blocked at daily limit: {quota_blocked}")
    if not quota_blocked:
        all_ok = False

    # Top-up 5 credits, now 62nd call should consume 1 credit and allow!
    add_flash_credits(fu_email, 5)
    allowed_with_credit, _ = record_daily_ai_call(fu_email)
    balances_after = load_user_balances()
    credits_left = balances_after.get(fu_email, {}).get("flash_credits")
    credit_consumed_ok = allowed_with_credit is True and credits_left == 4
    print(f"{'✅' if credit_consumed_ok else '❌'} Flash Credit Consumption: Allowed after quota exhaustion, remaining credits = {credits_left} (Expected 4)")
    if not credit_consumed_ok:
        all_ok = False

    # 7. Landing Page UI Modal Verification
    res_index = client.get("/")
    html = res_index.text
    has_modal = "topup-modal" in html and "Sprint Pack (50 Credits)" in html and "Exam Crunch" in html and "checkCreditsBalance" in html
    print(f"{'✅' if has_modal else '❌'} Landing Page: 'Instant Top-Up / Exam Sprint' modal & balance tool: {has_modal}")
    if not has_modal:
        all_ok = False

    print("==================================================")
    if all_ok:
        print("🎉 ALL PHASE 2 REQUIREMENTS VERIFIED SUCCESSFULLY (100%)")
    else:
        print("⚠️ SOME PHASE 2 CHECKS FAILED")
    print("==================================================")
    return all_ok

if __name__ == "__main__":
    success = run_phase2_tests()
    sys.exit(0 if success else 1)
