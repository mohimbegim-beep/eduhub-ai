import os
import sys
import time
import json
import hmac
import hashlib
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import (
    app,
    apply_dunning_grace_period,
    apply_refund_or_dispute,
    provision_subscription,
    get_or_create_user,
    load_user_balances,
    save_user_balances,
    is_transaction_already_processed,
    record_billing_transaction
)

client = TestClient(app)

def send_signed_webhook(payload: dict):
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "webhook-id": f"msg_{int(time.time() * 1000)}",
        "webhook-timestamp": str(int(time.time()))
    }
    sec = os.getenv("DODO_WEBHOOK_SECRET", "").strip()
    if sec:
        headers["x-signature"] = hmac.new(sec.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return client.post("/api/v1/billing/dodo-webhook", content=body, headers=headers)

class TestStage9BillingDunningReceipts(unittest.TestCase):

    # --------------------------------------------------------------------------
    # 9.1: Dunning Management & Grace Period Engine
    # --------------------------------------------------------------------------
    def test_9_1_apply_dunning_grace_period_function(self):
        email = f"dunning_test_{int(time.time() * 1000)}@eduhub.ai"
        user = apply_dunning_grace_period(email, order_id="sub_grace_100", grace_days=3)
        self.assertEqual(user["role"], "pro_max")
        self.assertTrue(user["is_subscribed"])
        self.assertEqual(user["subscription"]["status"], "grace_period")
        self.assertEqual(user["subscription"]["role"], "pro_max")
        self.assertTrue(user["subscription"]["dunning"]["active"])
        self.assertEqual(user["subscription"]["dunning"]["grace_days"], 3)
        self.assertGreater(user["subscription"]["dunning"]["grace_period_until"], time.time())

    def test_9_1_subscription_status_endpoint_reports_grace_period(self):
        email = f"grace_status_{int(time.time() * 1000)}@eduhub.ai"
        apply_dunning_grace_period(email, order_id="sub_grace_200", grace_days=3)

        resp = client.get(f"/api/v1/subscription/status?email={email}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["role"], "pro_max")
        self.assertTrue(data["is_subscribed"])
        self.assertTrue(data["workspace_unlocked"])
        self.assertTrue(data["in_grace_period"])
        self.assertEqual(data["subscription"]["status"], "grace_period")

    def test_9_1_webhook_payment_failed_activates_grace_period(self):
        email = f"wh_failed_{int(time.time() * 1000)}@eduhub.ai"
        order_id = f"fail_{int(time.time() * 1000)}"
        payload = {
            "type": "payment.failed",
            "data": {
                "id": order_id,
                "customer": {"email": email},
                "attributes": {"status": "failed", "user_email": email}
            }
        }
        resp = send_signed_webhook(payload)
        self.assertEqual(resp.status_code, 200)
        res_data = resp.json()
        self.assertEqual(res_data["status"], "verified")
        self.assertEqual(res_data["role_provisioned"], "pro_max")

        # Проверяем, что пользователю действительно включен grace period
        status_resp = client.get(f"/api/v1/subscription/status?email={email}")
        self.assertEqual(status_resp.status_code, 200)
        self.assertTrue(status_resp.json()["in_grace_period"])

    # --------------------------------------------------------------------------
    # 9.2: Webhook Idempotency Validation
    # --------------------------------------------------------------------------
    def test_9_2_webhook_idempotency_prevents_duplicate_processing(self):
        order_id = f"dodo_idemp_{int(time.time() * 1000)}"
        email = f"idemp_{int(time.time() * 1000)}@eduhub.ai"
        payload = {
            "type": "subscription.active",
            "data": {
                "id": order_id,
                "subscription_id": order_id,
                "customer": {"email": email},
                "attributes": {"status": "active", "user_email": email}
            }
        }

        # 1-й вызов: обработка и персистенция
        resp1 = send_signed_webhook(payload)
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()
        self.assertEqual(data1["status"], "verified")
        self.assertFalse(data1.get("idempotent", False))

        # 2-й вызов с тем же order_id и event_type: должен распознать дубликат
        resp2 = send_signed_webhook(payload)
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertEqual(data2["status"], "verified")
        self.assertTrue(data2.get("idempotent"))

    # --------------------------------------------------------------------------
    # 9.3: Refund and Dispute Immediate Revocation Engine
    # --------------------------------------------------------------------------
    def test_9_3_apply_refund_or_dispute_revocation(self):
        email = f"refund_target_{int(time.time() * 1000)}@eduhub.ai"
        # Сначала выдаем Pro Max и токены
        provision_subscription(email, "pro_max", order_id="ord_initial_300")
        balances = load_user_balances()
        balances[email]["flash_credits"] = 150
        save_user_balances(balances)

        # Вызываем отзыв по возврату средств
        user = apply_refund_or_dispute(email, order_id="ord_refund_300", reason="refund.processed")
        self.assertEqual(user["role"], "free_tier")
        self.assertEqual(user["tier"], "free_tier")
        self.assertFalse(user["is_subscribed"])
        self.assertEqual(user["subscription"]["status"], "refunded")
        self.assertEqual(user["flash_credits"], 0)

    def test_9_3_webhook_dispute_opened_revokes_access(self):
        email = f"dispute_wh_{int(time.time() * 1000)}@eduhub.ai"
        provision_subscription(email, "pro_max", order_id="ord_disp_orig")

        payload = {
            "type": "dispute.opened",
            "data": {
                "id": f"disp_{int(time.time() * 1000)}",
                "customer": {"email": email},
                "attributes": {"status": "disputed", "user_email": email}
            }
        }
        resp = send_signed_webhook(payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["role_provisioned"], "free_tier")

        # Проверяем итоговый статус пользователя
        status_resp = client.get(f"/api/v1/subscription/status?email={email}")
        self.assertEqual(status_resp.status_code, 200)
        self.assertEqual(status_resp.json()["role"], "free_tier")
        self.assertFalse(status_resp.json()["is_subscribed"])

    # --------------------------------------------------------------------------
    # 9.4: Electronic Receipts & MoR Transparency
    # --------------------------------------------------------------------------
    def test_9_4_get_billing_receipt_endpoint(self):
        test_order_id = f"rcpt_ord_{int(time.time() * 1000)}"
        test_email = f"receipt_buyer_{int(time.time() * 1000)}@eduhub.ai"
        
        # Регистрируем событие в логе транзакций
        record_billing_transaction(
            "subscription.active",
            {"data": {"id": test_order_id, "attributes": {"status": "paid", "user_email": test_email}}},
            explicit_order_id=test_order_id,
            explicit_email=test_email
        )

        resp = client.get(f"/api/v1/billing/receipt/{test_order_id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(data["receipt_id"], f"rcpt_{test_order_id}")
        self.assertEqual(data["order_id"], test_order_id)
        self.assertEqual(data["customer_email"], test_email)

        # Проверка реквизитов Merchant of Record
        mor = data["merchant_of_record"]
        self.assertEqual(mor["name"], "Dodo Payments Inc.")
        self.assertEqual(mor["role"], "Authorized Merchant of Record (MoR)")
        self.assertIn("VAT, Sales Tax", mor["tax_compliance"])
        self.assertEqual(mor["support_email"], "support@dodopayments.com")

        # Проверка тарифа и гарантий
        self.assertEqual(data["item"]["tier"], "pro_max")
        self.assertEqual(data["item"]["amount_usd"], 19.00)
        self.assertEqual(data["customer_portal_url"], "https://customer.dodopayments.com")
        self.assertIn("14-day", data["refund_guarantee"])


if __name__ == "__main__":
    unittest.main()
