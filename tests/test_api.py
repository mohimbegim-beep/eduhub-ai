import os
import time
import base64
import hmac
import hashlib
import unittest
from unittest.mock import MagicMock, patch

# Устанавливаем тестовые переменные окружения
os.environ["DODO_WEBHOOK_SECRET"] = "test_secret_key"
os.environ["RATE_LIMIT_MAX_REQUESTS"] = "5"
os.environ["RATE_LIMIT_WINDOW_SECONDS"] = "2"
os.environ["GEMINI_API_KEY"] = "fake_test_key_123"
os.environ["GEMINI_MODEL"] = "gemini-2.5-flash"

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app, rate_limiter, InMemoryRateLimiter

client = TestClient(app)

class TestEduHubAPI(unittest.TestCase):

    def setUp(self):
        rate_limiter._history.clear()

    def test_health_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["model"], "gemini-2.5-flash")
        self.assertIn("content_filtering", data)
        self.assertIn("rate_limiter", data)

    def test_landing_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)

    # ----------------------------------------------------------------------
    # Тесты фильтрации контента 18+ (Safe Content Filter)
    # ----------------------------------------------------------------------
    def test_ask_question_adult_content_blocked(self):
        # Запрос с темой 18+ должен немедленно блокироваться
        bad_queries = [
            "Где бесплатно смотреть порно?",
            "Напиши эротический рассказ",
            "Show me nsfw porn videos",
            "Как работает Onlyfans секс видео"
        ]
        for query in bad_queries:
            response = client.post("/api/v1/assistant/ask", json={"question": query})
            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertEqual(data["detail"]["error"], "ContentPolicyViolation")
            self.assertEqual(data["detail"]["policy"], "no_adult_content_18_plus")

    def test_summarize_adult_content_blocked(self):
        response = client.post("/api/v1/student/summarize", json={
            "text": "Длинный текст содержащий откровенное порно описание интимных сцен 18+ для проверки защитного фильтра платформы."
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["error"], "ContentPolicyViolation")

    def test_check_homework_adult_content_blocked(self):
        response = client.post("/api/v1/parent/check-homework", json={
            "assignment": "Задание с эротика и порнография описанием"
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["error"], "ContentPolicyViolation")

    # ----------------------------------------------------------------------
    # Тесты Input Validation (Валидация входных данных)
    # ----------------------------------------------------------------------
    def test_ask_question_validation_empty(self):
        response = client.post("/api/v1/assistant/ask", json={"question": " "})
        self.assertEqual(response.status_code, 422)

    def test_summarize_validation_too_short(self):
        response = client.post("/api/v1/student/summarize", json={"text": "Short"})
        self.assertEqual(response.status_code, 422)

    def test_summarize_validation_invalid_format(self):
        response = client.post("/api/v1/student/summarize", json={
            "text": "This is a sufficiently long lecture text describing fundamental algorithms and data structures.",
            "format": "invalid_format_type"
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Недопустимый формат", str(response.json()))

    def test_check_homework_validation_too_short(self):
        response = client.post("/api/v1/parent/check-homework", json={"assignment": "x"})
        self.assertEqual(response.status_code, 422)

    def test_check_homework_validation_corrupted_base64(self):
        response = client.post("/api/v1/parent/check-homework", json={
            "assignment": "Solve equation 2x + 4 = 10",
            "image_base64": "this-is-not-valid-base64-content!!!"
        })
        self.assertEqual(response.status_code, 422)
        self.assertIn("Некорректные данные base64", str(response.json()))

    # ----------------------------------------------------------------------
    # Тесты In-Memory Rate Limiting
    # ----------------------------------------------------------------------
    def test_rate_limiting_triggers_429(self):
        limiter = InMemoryRateLimiter(max_requests=3, window_seconds=2)
        key = "test_client_standalone"

        for _ in range(3):
            allowed, remaining, retry_after = limiter.check_and_record(key)
            self.assertTrue(allowed)

        allowed, remaining, retry_after = limiter.check_and_record(key)
        self.assertFalse(allowed)
        self.assertGreaterEqual(retry_after, 1)

        time.sleep(2.1)
        allowed, remaining, retry_after = limiter.check_and_record(key)
        self.assertTrue(allowed)

    def test_rate_limiting_via_api(self):
        test_key = f"client_api_test_{time.time()}"
        headers = {"X-API-Key": test_key}

        for _ in range(5):
            resp = client.post(
                "/api/v1/student/summarize",
                json={"text": "Short"},
                headers=headers
            )
            self.assertEqual(resp.status_code, 422)

        resp = client.post(
            "/api/v1/student/summarize",
            json={"text": "Short"},
            headers=headers
        )
        self.assertEqual(resp.status_code, 429)
        self.assertEqual(resp.json()["detail"]["error"], "Rate limit exceeded")
        self.assertIn("Retry-After", resp.headers)

    # ----------------------------------------------------------------------
    # Тесты Google GenAI SDK интеграции (gemini-2.5-flash)
    # ----------------------------------------------------------------------
    @patch("app.main.get_genai_client")
    def test_ask_question_gemini_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Квантовая запутанность — это физическое явление, при котором квантовые состояния двух или более объектов оказываются взаимосвязанными."
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/v1/assistant/ask",
            json={
                "question": "Объясни простыми словами квантовую запутанность",
                "detail_level": "standard"
            },
            headers={"X-API-Key": "unit-test-ask-key"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["model"], "gemini-2.5-flash")
        self.assertTrue(data["safety_checked"])
        self.assertIn("Квантовая запутанность", data["answer"])

        mock_client.models.generate_content.assert_called_once()
        call_args = mock_client.models.generate_content.call_args
        self.assertEqual(call_args.kwargs["model"], "gemini-2.5-flash")
        # Проверяем, что переданы настройки безопасности (safety_settings)
        self.assertIn("safety_settings", call_args.kwargs["config"].__dict__)

    @patch("app.main.get_genai_client")
    def test_summarize_gemini_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "## Executive Summary\nCalculus is the mathematical study of continuous change."
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        response = client.post(
            "/api/v1/student/summarize",
            json={
                "text": "Calculus is the mathematical study of continuous change, in the same way that geometry is the study of shape.",
                "format": "structured"
            },
            headers={"X-API-Key": "unit-test-summarize-key"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["model"], "gemini-2.5-flash")
        self.assertIn("Calculus", data["summary"])

    @patch("app.main.get_genai_client")
    def test_check_homework_gemini_with_image_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "### 🎯 Step-by-Step Diagnostic\nGood start on the quadratic formula."
        mock_client.models.generate_content.return_value = mock_response
        mock_get_client.return_value = mock_client

        sample_b64 = base64.b64encode(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82").decode("utf-8")

        response = client.post(
            "/api/v1/parent/check-homework",
            json={
                "assignment": "Find roots for 2x^2 + 4x - 6 = 0",
                "student_solution": "x = (-4 +- 8) / 4",
                "image_base64": f"data:image/png;base64,{sample_b64}",
                "subject": "Mathematics",
                "grade_level": "Grade 9"
            },
            headers={"X-API-Key": "unit-test-homework-key"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["model"], "gemini-2.5-flash")
        self.assertIn("Diagnostic", data["guidance"])

    # ----------------------------------------------------------------------
    # Тесты Dodo Payments Webhook
    # ----------------------------------------------------------------------
    def test_dodo_payments_webhook_signature_valid(self):
        secret = "test_secret_key"
        payload_body = b'{"meta":{"event_name":"order_created"},"data":{"attributes":{"user_email":"student@eduhub.ai"}}}'
        signature = hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()

        response = client.post(
            "/api/v1/billing/dodo-webhook",
            content=payload_body,
            headers={"x-signature": signature, "Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "verified")
        self.assertEqual(response.json()["event"], "order_created")

    def test_dodo_payments_webhook_signature_invalid(self):
        response = client.post(
            "/api/v1/billing/dodo-webhook",
            content=b'{"meta":{"event_name":"order_created"}}',
            headers={"x-signature": "wrong_signature_12345", "Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Invalid cryptographic signature", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
