"""
Test Suite: Trust & Legal Micro-Consent Layer (Cookie & Legal Bar, Checkout Micro-Consent, i18n Parity)
"""
import unittest
import subprocess
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

class TestLegalConsentLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.base_dir = Path(__file__).resolve().parent.parent

    def test_01_legal_consent_js_syntax_and_keys(self):
        js_file = self.base_dir / "static" / "js" / "legal-consent.js"
        self.assertTrue(js_file.exists(), "legal-consent.js does not exist!")

        content = js_file.read_text(encoding="utf-8")
        self.assertIn("cookie_consent", content, "Missing localStorage key 'cookie_consent'")
        self.assertIn("Accept & Continue", content, "Missing English button")
        self.assertIn("Принять и продолжить", content, "Missing Russian button")
        self.assertIn("Qabul qilish va davom etish", content, "Missing Uzbek button")
        self.assertIn("Aceptar y continuar", content, "Missing Spanish button")
        self.assertTrue("/terms" in content and "/privacy" in content and "/refund" in content)
        self.assertIn("checkout-micro-consent", content)

    def test_02_i18n_translation_keys(self):
        i18n_content = (self.base_dir / "static" / "js" / "i18n.js").read_text(encoding="utf-8")
        self.assertIn("checkout_micro_consent", i18n_content)
        self.assertIn("cookie_consent_text", i18n_content)
        self.assertIn("cookie_consent_btn", i18n_content)

    def test_03_index_markup(self):
        index_content = (self.base_dir / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("legal-consent.js", index_content, "legal-consent.js missing from index.html")
        micro_count = index_content.count("checkout-micro-consent")
        self.assertGreaterEqual(micro_count, 5, f"Expected at least 5 checkout micro-consent captions, found {micro_count}")

    def test_04_tools_markup(self):
        tool_names = [
            "essay-grader.html",
            "homework-solver.html",
            "pdf-summarizer.html",
            "language-tutor.html",
            "gpa-calculator.html",
            "citation-generator.html"
        ]
        for tool in tool_names:
            t_path = self.base_dir / "static" / "tools" / tool
            t_content = t_path.read_text(encoding="utf-8")
            self.assertIn("legal-consent.js", t_content, f"legal-consent.js missing in {tool}")
            self.assertIn("checkout-micro-consent", t_content, f"checkout-micro-consent missing in {tool}")

    def test_05_legal_pages_inclusion(self):
        for p in ["support.html", "refund.html", "terms.html", "privacy.html"]:
            lp = self.base_dir / "static" / p
            self.assertIn("legal-consent.js", lp.read_text(encoding="utf-8"))

    def test_06_http_routes_availability(self):
        urls = [
            "/",
            "/static/js/legal-consent.js",
            "/support",
            "/refund",
            "/terms",
            "/privacy",
            "/tools/essay-grader",
            "/tools/homework-solver"
        ]
        for u in urls:
            resp = self.client.get(u)
            self.assertEqual(resp.status_code, 200, f"Route {u} returned status {resp.status_code}")

if __name__ == "__main__":
    unittest.main()
