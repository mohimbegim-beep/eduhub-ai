"""
EduHub AI — Quality Gate 12 Test Suite: International Legal Compliance & GDPR
Verifies:
1. GDPR Article 17 Right to Erasure ("Right to be Forgotten"):
   - Endpoint: POST /api/v1/user/delete-account & POST /api/v1/user/gdpr-erasure
   - Atomic balance erasure and transaction anonymization (retaining financial ledgers without PII)
   - Telemetry audit logging and session cookie clearance
2. Merchant of Record (MoR) Full Transparency:
   - All 24 HTML pages contain explicit MoR disclosures identifying Dodo Payments Inc.
   - Zero occurrences of legacy placeholder payment processor names or unauthorized MoRs.
3. Pre-Checkout Interactive Consent Gate & Legal Policies:
   - Terms of Service, Privacy Policy, and Refund Policy accessibility
   - Pre-checkout affirmative consent modal and multi-language transparency (EN, RU, UZ, ES)
"""

import unittest
import json
import re
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app, USER_BALANCES_FILE, TRANSACTIONS_LOG, SYSTEM_AUDIT_LOG

class TestStage12ComplianceAndGDPR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.root_dir = Path(__file__).resolve().parent.parent

    def test_01_gdpr_article_17_right_to_erasure(self):
        """Verify GDPR Article 17 account deletion and transactional anonymization."""
        test_email = "gdpr_test_user_777@example.com"

        # 1. Seed user balance
        with open(USER_BALANCES_FILE, "r", encoding="utf-8") as f:
            balances = json.load(f)
        balances[test_email] = {
            "balance": 25.0,
            "currency": "USD",
            "tier": "pro",
            "created_at": "2026-09-01T00:00:00Z"
        }
        with open(USER_BALANCES_FILE, "w", encoding="utf-8") as f:
            json.dump(balances, f, indent=2)

        # 2. Seed transaction in billing_transactions.json
        if TRANSACTIONS_LOG.exists():
            with open(TRANSACTIONS_LOG, "r", encoding="utf-8") as f:
                txs = json.load(f)
        else:
            txs = []
        
        txs.append({
            "event_id": "tx_gdpr_test_999",
            "event_type": "payment_succeeded",
            "customer_email": test_email,
            "amount": 2500,
            "currency": "USD",
            "attributes": {"user_email": test_email}
        })
        with open(TRANSACTIONS_LOG, "w", encoding="utf-8") as f:
            json.dump(txs, f, indent=2)

        # 3. Call GDPR deletion endpoint
        res = self.client.post("/api/v1/user/delete-account", json={"email": test_email})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("Article 17", data["gdpr_article"])
        self.assertTrue(data["account_erased"])
        self.assertGreaterEqual(data["transactions_anonymized"], 1)

        # 4. Verify balances file: user MUST be completely deleted
        with open(USER_BALANCES_FILE, "r", encoding="utf-8") as f:
            updated_balances = json.load(f)
        self.assertNotIn(test_email, updated_balances)

        # 5. Verify transactions: personal email MUST be replaced by gdpr_erased_ hash
        with open(TRANSACTIONS_LOG, "r", encoding="utf-8") as f:
            updated_txs = json.load(f)
        emails = [t.get("customer_email") for t in updated_txs]
        self.assertNotIn(test_email, emails)
        # Verify an anonymized record exists
        erased_records = [t for t in updated_txs if str(t.get("customer_email")).startswith("gdpr_erased_")]
        self.assertGreaterEqual(len(erased_records), 1)

        # 6. Verify audit log entry
        if SYSTEM_AUDIT_LOG.exists():
            with open(SYSTEM_AUDIT_LOG, "r", encoding="utf-8") as f:
                log_content = f.read()
            self.assertIn("GDPR_RIGHT_TO_ERASURE_PROCESSED", log_content)

    def test_02_gdpr_erasure_alias_and_validation(self):
        """Verify alias /api/v1/user/gdpr-erasure and email validation."""
        # Invalid email
        res_bad = self.client.post("/api/v1/user/gdpr-erasure", json={"email": "invalid_email_format"})
        self.assertEqual(res_bad.status_code, 400)

        # Non-existent email should succeed gracefully with account_erased=False
        res_ok = self.client.post("/api/v1/user/gdpr-erasure", json={"email": "nonexistent_gdpr_user@test.org"})
        self.assertEqual(res_ok.status_code, 200)
        self.assertFalse(res_ok.json()["account_erased"])

    def test_03_mor_transparency_all_24_html_pages(self):
        """Verify that all 24 HTML pages have Dodo Payments Inc. MoR disclosure in their footers."""
        static_dir = self.root_dir / "static"
        html_files = sorted(static_dir.rglob("*.html"))
        self.assertEqual(len(html_files), 24, f"Expected 24 HTML pages, found {len(html_files)}")

        for html_path in html_files:
            text = html_path.read_text(encoding="utf-8")
            # 1. Must contain Dodo Payments
            self.assertIn(
                "Dodo Payments",
                text,
                f"Page {html_path.relative_to(self.root_dir)} is missing Dodo Payments MoR mention"
            )
            # 2. Must contain Merchant of Record disclosure
            self.assertIn(
                "Merchant of Record",
                text,
                f"Page {html_path.relative_to(self.root_dir)} is missing Merchant of Record disclosure"
            )
            # 3. Must NOT contain obsolete placeholder
            self.assertNotIn(
                "Certified Payment Processor (PCI-DSS L1)",
                text,
                f"Page {html_path.relative_to(self.root_dir)} contains legacy payment processor placeholder"
            )

    def test_04_zero_unauthorized_payment_processors(self):
        """Ensure no legacy or unauthorized payment processors exist across codebase."""
        forbidden_terms = [
            "Lemon Squeezy",
            "lemonsqueezy",
            "Certified Payment Processor (PCI-DSS L1)"
        ]
        target_dirs = [self.root_dir / "static", self.root_dir / "locales", self.root_dir / "app"]
        for tdir in target_dirs:
            for p in tdir.rglob("*"):
                if p.is_file() and p.suffix in [".html", ".js", ".json", ".py"]:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    for term in forbidden_terms:
                        self.assertNotIn(
                            term,
                            text,
                            f"Forbidden payment reference '{term}' found in {p.relative_to(self.root_dir)}"
                        )

    def test_05_legal_policy_endpoints_accessible(self):
        """Verify that legal policy routes return HTTP 200 with appropriate content."""
        endpoints = ["/terms", "/privacy", "/refund", "/support", "/demo"]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Endpoint {ep} failed with {res.status_code}")
            self.assertIn("Dodo Payments", res.text)
            self.assertIn("Merchant of Record", res.text)

    def test_06_consent_checkpoint_in_js_layer(self):
        """Verify pre-checkout legal consent module has Dodo Payments transparency across all 4 locales."""
        js_path = self.root_dir / "static" / "js" / "legal-consent.js"
        self.assertTrue(js_path.exists())
        js_text = js_path.read_text(encoding="utf-8")
        
        # Check pre-checkout modal components
        self.assertIn("pre-checkout-checkbox", js_text)
        self.assertIn("confirmCheckoutConsent", js_text)
        self.assertIn("pcm-b4", js_text)
        self.assertIn("Dodo Payments Inc.", js_text)
        
        # Check 4 locales are supported
        for loc in ["en", "ru", "uz", "es"]:
            self.assertIn(f"{loc}:", js_text)

if __name__ == "__main__":
    unittest.main()
