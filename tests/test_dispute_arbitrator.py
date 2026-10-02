"""
Test Suite: AI Billing, Dispute & Automated Refund Arbitrator (Fee-Protected & Win-Win)
"""
import unittest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app

class TestDisputeArbitrator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_support_html_page(self):
        res = self.client.get("/support")
        self.assertEqual(res.status_code, 200)
        self.assertTrue("AI Billing, Dispute & Refund Resolution Portal" in res.text or "Arbitration" in res.text)

    def test_02_winwin_bonus_resolution(self):
        now = datetime.now(timezone.utc)
        recent_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
        res = self.client.post("/api/v1/support/dispute-analyze", json={
            "customer_email": "student_winwin@stanford.edu",
            "order_id": "ORD-LS-1001",
            "issue_type": "unsatisfied",
            "purchase_date": recent_date,
            "description": "I needed more IELTS General Task 1 templates and want to cancel my Pro Max subscription.",
            "plan_tier": "pro_max",
            "preferred_resolution": "instant_bonus_120",
            "language": "ru"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["verdict"], "APPROVED_BONUS")
        self.assertEqual(data["financial_summary"]["order_value"], 19.00)
        self.assertEqual(data["financial_summary"]["bonus_value"], 22.80)
        self.assertEqual(data["financial_summary"]["net_refund"], 0.0)

    def test_03_fee_protected_net_card_refund(self):
        now = datetime.now(timezone.utc)
        recent_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
        res = self.client.post("/api/v1/support/dispute-analyze", json={
            "customer_email": "client_net@berkeley.edu",
            "order_id": "ORD-LS-2002",
            "issue_type": "forgot_cancel",
            "purchase_date": recent_date,
            "description": "Forgot to cancel my 3-day trial and want a refund back to my Visa credit card.",
            "plan_tier": "pro_max",
            "preferred_resolution": "card_refund",
            "language": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["verdict"], "APPROVED_NET_REFUND")
        self.assertEqual(data["financial_summary"]["order_value"], 19.00)
        self.assertEqual(data["financial_summary"]["gateway_fee"], 1.45)
        self.assertEqual(data["financial_summary"]["net_refund"], 17.55)

    def test_04_duplicate_charge_full_refund(self):
        now = datetime.now(timezone.utc)
        recent_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
        res = self.client.post("/api/v1/support/dispute-analyze", json={
            "customer_email": "parent_dup@mit.edu",
            "order_id": "ORD-LS-3003",
            "issue_type": "duplicate_charge",
            "purchase_date": recent_date,
            "description": "I was billed twice for Student Starter due to network timeout at checkout.",
            "plan_tier": "student_starter",
            "preferred_resolution": "card_refund",
            "language": "en"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["verdict"], "APPROVED")
        self.assertEqual(data["financial_summary"]["net_refund"], 9.00)

    def test_05_expired_statutory_14day_limit(self):
        now = datetime.now(timezone.utc)
        old_date = (now - timedelta(days=28)).strftime("%Y-%m-%d")
        res = self.client.post("/api/v1/support/dispute-analyze", json={
            "customer_email": "late_user@oxford.ac.uk",
            "order_id": "ORD-LS-4004",
            "issue_type": "unsatisfied",
            "purchase_date": old_date,
            "description": "I purchased this course a month ago and now want my money back.",
            "plan_tier": "pro_max",
            "preferred_resolution": "card_refund",
            "language": "ru"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["verdict"], "LEGAL_REFUSAL_WITH_GOODWILL")
        self.assertEqual(data["financial_summary"]["net_refund"], 0.0)
        self.assertIn("14", data["legal_notice"]["legal_basis"])

    def test_06_multilanguage_support(self):
        now = datetime.now(timezone.utc)
        recent_date = (now - timedelta(days=3)).strftime("%Y-%m-%d")
        res_uz = self.client.post("/api/v1/support/dispute-analyze", json={
            "customer_email": "toshkent_student@edu.uz",
            "issue_type": "unsatisfied",
            "purchase_date": recent_date,
            "description": "IELTS insholarini tekshirish uchun obuna bo'lgandim, qaytarmoqchiman.",
            "plan_tier": "student_starter",
            "preferred_resolution": "instant_bonus_120",
            "language": "uz"
        })
        self.assertEqual(res_uz.status_code, 200)
        data_uz = res_uz.json()
        self.assertTrue("Bonus" in data_uz["legal_notice"]["title"] or "Balansingizga" in data_uz["legal_notice"]["title"])

        res_es = self.client.post("/api/v1/support/dispute-analyze", json={
            "customer_email": "estudiante_madrid@ucm.es",
            "issue_type": "forgot_cancel",
            "purchase_date": recent_date,
            "description": "Deseo cancelar mi suscripción y solicitar la devolución.",
            "plan_tier": "pro_max",
            "preferred_resolution": "card_refund",
            "language": "es"
        })
        self.assertEqual(res_es.status_code, 200)
        data_es = res_es.json()
        self.assertIn("Reembolso", data_es["legal_notice"]["title"])

    def test_07_dispute_status_retrieval(self):
        now = datetime.now(timezone.utc)
        recent_date = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        create_res = self.client.post("/api/v1/support/dispute-analyze", json={
            "customer_email": "retrieve_test@mit.edu",
            "order_id": "ORD-RET-999",
            "issue_type": "duplicate_charge",
            "purchase_date": recent_date,
            "description": "Checking dispute retrieval.",
            "plan_tier": "student_starter",
            "preferred_resolution": "card_refund",
            "language": "en"
        })
        self.assertEqual(create_res.status_code, 200)
        disp_id = create_res.json()["dispute_id"]

        res = self.client.get(f"/api/v1/support/dispute/{disp_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["dispute"]["dispute_id"], disp_id)

if __name__ == "__main__":
    unittest.main()
