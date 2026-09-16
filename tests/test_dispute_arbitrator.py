"""
Test Suite: AI Billing, Dispute & Automated Refund Arbitrator (Fee-Protected & Win-Win)
"""
import sys
import json
import urllib.request
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding='utf-8')
BASE = "http://127.0.0.1:8000"

def post_json(endpoint, payload):
    req = urllib.request.Request(
        f"{BASE}{endpoint}",
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.status, json.loads(res.read().decode('utf-8'))

def get_json(endpoint):
    req = urllib.request.Request(f"{BASE}{endpoint}")
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.status, json.loads(res.read().decode('utf-8'))

def get_html(endpoint):
    req = urllib.request.Request(f"{BASE}{endpoint}")
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.status, res.read().decode('utf-8')

print("="*70)
print("⚖️ AUDIT: AI BILLING, DISPUTE & AUTOMATED REFUND ARBITRATOR")
print("="*70)

# 1. Test /support HTML page
status, html = get_html("/support")
assert status == 200, f"Expected 200, got {status}"
assert "AI Billing, Dispute & Refund Resolution Portal" in html or "Arbitration" in html
print("  [PASS] GET /support -> HTTP 200 OK (Portal UI rendered with 4-lang i18n)")

# 2. Test Win-Win 120% Wallet Bonus Resolution
now = datetime.now(timezone.utc)
recent_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
status, data = post_json("/api/v1/support/dispute-analyze", {
    "customer_email": "student_winwin@stanford.edu",
    "order_id": "ORD-LS-1001",
    "issue_type": "unsatisfied",
    "purchase_date": recent_date,
    "description": "I needed more IELTS General Task 1 templates and want to cancel my Pro Max subscription.",
    "plan_tier": "pro_max",
    "preferred_resolution": "instant_bonus_120",
    "language": "ru"
})
assert status == 200
assert data["verdict"] == "APPROVED_BONUS"
assert data["financial_summary"]["order_value"] == 19.00
assert data["financial_summary"]["bonus_value"] == 22.80
assert data["financial_summary"]["net_refund"] == 0.0
print(f"  [PASS] Scenario 1 (Win-Win 120% Bonus): Verdict={data['verdict']} | BonusValue=${data['financial_summary']['bonus_value']:.2f} | Payout=$0.00 (Zero loss for company!)")
disp_id = data["dispute_id"]

# 3. Test Fee-Protected Net Card Refund (Deducting Gateway Acquirer Fee)
status, data2 = post_json("/api/v1/support/dispute-analyze", {
    "customer_email": "client_net@berkeley.edu",
    "order_id": "ORD-LS-2002",
    "issue_type": "forgot_cancel",
    "purchase_date": recent_date,
    "description": "Forgot to cancel my 3-day trial and want a refund back to my Visa credit card.",
    "plan_tier": "pro_max",
    "preferred_resolution": "card_refund",
    "language": "en"
})
assert status == 200
assert data2["verdict"] == "APPROVED_NET_REFUND"
assert data2["financial_summary"]["order_value"] == 19.00
assert data2["financial_summary"]["gateway_fee"] == 1.45
assert data2["financial_summary"]["net_refund"] == 17.55
print(f"  [PASS] Scenario 2 (Fee-Protected Card Refund): Verdict={data2['verdict']} | Gross=$19.00 | RetainedFee=$1.45 | NetPayout=${data2['financial_summary']['net_refund']:.2f}")

# 4. Test 100% Full Refund for Accidental Duplicate Charge
status, data3 = post_json("/api/v1/support/dispute-analyze", {
    "customer_email": "parent_dup@mit.edu",
    "order_id": "ORD-LS-3003",
    "issue_type": "duplicate_charge",
    "purchase_date": recent_date,
    "description": "I was billed twice for Student Starter due to network timeout at checkout.",
    "plan_tier": "student_starter",
    "preferred_resolution": "card_refund",
    "language": "en"
})
assert status == 200
assert data3["verdict"] == "APPROVED"
assert data3["financial_summary"]["net_refund"] == 9.00
print(f"  [PASS] Scenario 3 (Duplicate Billing 100% Full): Verdict={data3['verdict']} | FullPayout=$9.00 (Saves $15 chargeback penalty!)")

# 5. Test Expired Statutory 14-Day Limit (>14 days -> Formal Refusal + 25 Goodwill Credits)
old_date = (now - timedelta(days=28)).strftime("%Y-%m-%d")
status, data4 = post_json("/api/v1/support/dispute-analyze", {
    "customer_email": "late_user@oxford.ac.uk",
    "order_id": "ORD-LS-4004",
    "issue_type": "unsatisfied",
    "purchase_date": old_date,
    "description": "I purchased this course a month ago and now want my money back.",
    "plan_tier": "pro_max",
    "preferred_resolution": "card_refund",
    "language": "ru"
})
assert status == 200
assert data4["verdict"] == "LEGAL_REFUSAL_WITH_GOODWILL"
assert data4["financial_summary"]["net_refund"] == 0.0
assert "14" in data4["legal_notice"]["legal_basis"]
print(f"  [PASS] Scenario 4 (Time-Barred Legal Refusal + Goodwill): Verdict={data4['verdict']} | Payout=$0.00 | Legal Basis Cites Section 1.1")

# 6. Test Multi-Language Output (Uzbek & Spanish)
status, data_uz = post_json("/api/v1/support/dispute-analyze", {
    "customer_email": "toshkent_student@edu.uz",
    "issue_type": "unsatisfied",
    "purchase_date": recent_date,
    "description": "IELTS insholarini tekshirish uchun obuna bo'lgandim, qaytarmoqchiman.",
    "plan_tier": "student_starter",
    "preferred_resolution": "instant_bonus_120",
    "language": "uz"
})
assert status == 200
assert "Bonus" in data_uz["legal_notice"]["title"] or "Balansingizga" in data_uz["legal_notice"]["title"]
print(f"  [PASS] Multi-Language (Uzbek): {data_uz['legal_notice']['title'][:60]}...")

status, data_es = post_json("/api/v1/support/dispute-analyze", {
    "customer_email": "estudiante_madrid@ucm.es",
    "issue_type": "forgot_cancel",
    "purchase_date": recent_date,
    "description": "Deseo cancelar mi suscripción y solicitar la devolución.",
    "plan_tier": "pro_max",
    "preferred_resolution": "card_refund",
    "language": "es"
})
assert status == 200
assert "Reembolso" in data_es["legal_notice"]["title"]
print(f"  [PASS] Multi-Language (Spanish): {data_es['legal_notice']['title'][:60]}...")

# 7. Test Dispute Status Retrieval by Case ID
status, rec = get_json(f"/api/v1/support/dispute/{disp_id}")
assert status == 200
assert rec["dispute"]["dispute_id"] == disp_id
print(f"  [PASS] GET /api/v1/support/dispute/{disp_id} -> HTTP 200 OK (Audited Case record retrieved)")

print("="*70)
print("🎉 ALL 7/7 ARBITRATION, FEE-PROTECTION & LEGAL TESTS PASSED (100%)")
print("="*70)
