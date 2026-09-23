import os
import sys
import json
import time
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import (
    app,
    record_system_audit_event,
    SYSTEM_AUDIT_LOG
)
from services.keepalive_sentinel import save_sentinel_telemetry

client = TestClient(app, raise_server_exceptions=False)

class TestStage11ObservabilityAndSentinel(unittest.TestCase):

    # --------------------------------------------------------------------------
    # 11.1: Deep Healthcheck Diagnostic Engine
    # --------------------------------------------------------------------------
    def test_11_1_deep_healthcheck_diagnostics_on_health_and_alias(self):
        for route in ["/health", "/api/v1/health"]:
            resp = client.get(route)
            self.assertEqual(resp.status_code, 200, f"Route {route} must return HTTP 200")
            data = resp.json()

            self.assertEqual(data.get("status"), "healthy")
            self.assertEqual(data.get("version"), "1.2.0")
            self.assertIn("uptime_seconds", data)

            # Deep diagnostics structure
            diag = data.get("diagnostics", {})
            self.assertIn("latency_ms", diag)

            # Database / Storage
            db = diag.get("database", {})
            self.assertEqual(db.get("status"), "healthy")
            self.assertGreaterEqual(db.get("users_registered", 0), 0)
            self.assertGreaterEqual(db.get("transactions_recorded", 0), 0)

            # GenAI Engine
            genai_diag = diag.get("genai", {})
            self.assertEqual(genai_diag.get("model"), "gemini-2.5-flash")
            self.assertTrue(genai_diag.get("configured"))
            self.assertIn("Strict 18+", genai_diag.get("safety_filter", ""))

            # MoR Billing Gateway
            billing = diag.get("billing", {})
            self.assertEqual(billing.get("provider"), "Dodo Payments Inc.")
            self.assertEqual(billing.get("role"), "Authorized Merchant of Record (MoR)")

            # Backup Engine
            bkp = diag.get("backup", {})
            self.assertGreaterEqual(bkp.get("total_snapshots", 0), 1)

            # Legacy compatibility fields
            self.assertEqual(data.get("model"), "gemini-2.5-flash")
            self.assertIn("Strict 18+", data.get("content_filtering", ""))
            self.assertIn("rate_limiter", data)

    # --------------------------------------------------------------------------
    # 11.2: Structured System Audit Logging & Sanitized Error Responses
    # --------------------------------------------------------------------------
    def test_11_2_record_system_audit_event_functionality(self):
        test_event = f"TEST_AUDIT_EVENT_{int(time.time() * 1000)}"
        record_system_audit_event(
            level="INFO",
            event=test_event,
            details={"metric": "test_latency", "value": 42.5},
            duration_ms=42.5
        )

        self.assertTrue(SYSTEM_AUDIT_LOG.exists(), "logs/system_audit.log must exist")
        with open(SYSTEM_AUDIT_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()

        matched = None
        for line in reversed(lines):
            try:
                entry = json.loads(line.strip())
                if entry.get("event") == test_event:
                    matched = entry
                    break
            except Exception:
                continue

        self.assertIsNotNone(matched, f"Event {test_event} should be logged in system_audit.log")
        self.assertEqual(matched["level"], "INFO")
        self.assertEqual(matched["details"]["value"], 42.5)
        self.assertEqual(matched["duration_ms"], 42.5)

    def test_11_2_sanitized_500_error_response_no_path_leak(self):
        # Добавляем временный эндпоинт, намеренно вызывающий crash
        @app.get("/api/v1/test/trigger-crash")
        async def trigger_crash():
            raise RuntimeError("Confidential Internal Database Failure in C:\\EDU HUB\\secrets\\keys.pem")

        resp = client.get("/api/v1/test/trigger-crash")
        self.assertEqual(resp.status_code, 500)
        body = resp.json()

        # Проверяем, что клиенту возвращается безопасный, стандартизированный ответ
        self.assertEqual(body.get("status"), "error")
        self.assertEqual(body.get("error_code"), "INTERNAL_SERVER_ERROR")
        self.assertIn("An unexpected error occurred", body.get("message", ""))

        # Проверяем, что секретные серверные пути НЕ утекли клиенту в JSON ответе
        raw_body_text = resp.text
        self.assertNotIn("C:\\EDU HUB", raw_body_text)
        self.assertNotIn("keys.pem", raw_body_text)
        self.assertNotIn("RuntimeError", raw_body_text)

    # --------------------------------------------------------------------------
    # 11.3: Sentinel Keepalive Monitoring & Daemon Telemetry
    # --------------------------------------------------------------------------
    def test_11_3_sentinel_status_endpoint(self):
        # 1. Симулируем запись телеметрии сторожа
        save_sentinel_telemetry(success=True, status_code=200, latency_ms=450.2)

        resp = client.get("/api/v1/system/sentinel/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data.get("status"), "success")
        sentinel = data.get("sentinel", {})
        self.assertEqual(sentinel.get("status"), "active")
        self.assertTrue(sentinel.get("is_daemon_alive"))
        self.assertEqual(sentinel.get("interval_seconds"), 540)
        self.assertEqual(sentinel.get("target_url"), "https://eduhub-ai.onrender.com/health")
        self.assertEqual(sentinel.get("last_status_code"), 200)
        self.assertEqual(sentinel.get("latency_ms"), 450.2)
        self.assertTrue(sentinel.get("success"))


if __name__ == "__main__":
    unittest.main()
