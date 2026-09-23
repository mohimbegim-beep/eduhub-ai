import os
import sys
import time
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app, generate_session_token, verify_session_token, ALLOWED_ORIGINS
from services.backup_engine import backup_engine, atomic_write_json

client = TestClient(app)

class TestStage7SecurityAndData(unittest.TestCase):

    # --------------------------------------------------------------------------
    # 7.1: HTTP Security Headers
    # --------------------------------------------------------------------------
    def test_7_1_security_headers_present(self):
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)

        headers = resp.headers
        self.assertIn("strict-transport-security", headers)
        self.assertEqual(headers["strict-transport-security"], "max-age=31536000; includeSubDomains; preload")

        self.assertIn("content-security-policy", headers)
        csp = headers["content-security-policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("https://checkout.dodopayments.com", csp)
        self.assertIn("https://cdn.tailwindcss.com", csp)
        self.assertIn("frame-src 'self' https://checkout.dodopayments.com", csp)

        self.assertEqual(headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(headers.get("x-frame-options"), "SAMEORIGIN")
        self.assertEqual(headers.get("x-xss-protection"), "1; mode=block")
        self.assertEqual(headers.get("referrer-policy"), "strict-origin-when-cross-origin")
        self.assertIn("payment=*", headers.get("permissions-policy", ""))

    # --------------------------------------------------------------------------
    # 7.2: Production CORS Whitelist
    # --------------------------------------------------------------------------
    def test_7_2_cors_allowed_origin(self):
        resp = client.options(
            "/api/v1/catalog/products",
            headers={
                "Origin": "https://eduhub-ai.onrender.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("access-control-allow-origin"), "https://eduhub-ai.onrender.com")
        self.assertEqual(resp.headers.get("access-control-allow-credentials"), "true")

    def test_7_2_cors_unauthorized_origin_rejected(self):
        resp = client.options(
            "/api/v1/catalog/products",
            headers={
                "Origin": "https://malicious-phishing-attacker.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        # Should NOT echo back the malicious origin
        self.assertNotEqual(resp.headers.get("access-control-allow-origin"), "https://malicious-phishing-attacker.com")

    # --------------------------------------------------------------------------
    # 7.3: Auth & Session Lifecycle
    # --------------------------------------------------------------------------
    def test_7_3_unauthenticated_session(self):
        resp = client.get("/api/v1/auth/session")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["authenticated"])
        self.assertEqual(data["role"], "free_tier")

    def test_7_3_login_and_authenticated_session(self):
        email = f"user_{int(time.time())}@eduhub.ai"
        login_resp = client.post("/api/v1/auth/login", json={"email": email})
        self.assertEqual(login_resp.status_code, 200)
        data = login_resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["email"], email)
        self.assertIn("session_token", data)

        token = data["session_token"]
        self.assertEqual(verify_session_token(token), email)

        # Проверка cookie
        session_resp = client.get("/api/v1/auth/session")
        self.assertEqual(session_resp.status_code, 200)
        sess_data = session_resp.json()
        self.assertTrue(sess_data["authenticated"])
        self.assertEqual(sess_data["email"], email)

        # Проверка передачи токена через заголовок
        client_clean = TestClient(app)
        header_resp = client_clean.get("/api/v1/auth/session", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(header_resp.status_code, 200)
        self.assertTrue(header_resp.json()["authenticated"])
        self.assertEqual(header_resp.json()["email"], email)

    def test_7_3_logout_clears_session(self):
        email = "logout_test@eduhub.ai"
        client.post("/api/v1/auth/login", json={"email": email})
        logout_resp = client.post("/api/v1/auth/logout")
        self.assertEqual(logout_resp.status_code, 200)

        # После logout сессия не аутентифицирована
        check_resp = client.get("/api/v1/auth/session")
        self.assertFalse(check_resp.json()["authenticated"])

    def test_7_3_invalid_corrupted_token(self):
        client_test = TestClient(app)
        bad_resp = client_test.get("/api/v1/auth/session", headers={"Authorization": "Bearer corrupted_fake_token_123"})
        self.assertEqual(bad_resp.status_code, 200)
        self.assertFalse(bad_resp.json()["authenticated"])

    # --------------------------------------------------------------------------
    # 7.4: Backup Engine & Data Shield
    # --------------------------------------------------------------------------
    def test_7_4_create_and_list_backups(self):
        # Триггер снимка через API
        backup_resp = client.post("/api/v1/system/backup")
        self.assertEqual(backup_resp.status_code, 200)
        data = backup_resp.json()
        self.assertEqual(data["status"], "success")
        self.assertGreater(len(data["files_backed_up"]), 0)

        # Запрос списка снимков
        list_resp = client.get("/api/v1/system/backups")
        self.assertEqual(list_resp.status_code, 200)
        list_data = list_resp.json()
        self.assertEqual(list_data["status"], "active")
        self.assertGreater(list_data["total_snapshots"], 0)

    def test_7_4_atomic_write_json_safety(self):
        test_file = BASE_DIR / "data" / "test_atomic_safety.json"
        payload = {"safety_verified": True, "timestamp": time.time()}
        success = atomic_write_json(test_file, payload)
        self.assertTrue(success)
        self.assertTrue(test_file.exists())
        self.assertFalse(test_file.with_suffix(".tmp").exists())

        # Очистка тестового файла
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    unittest.main()
