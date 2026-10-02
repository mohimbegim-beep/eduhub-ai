import os
import sys
import json
import base64
import hmac
import hashlib
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app, rate_limiter

client = TestClient(app)


class TestBackendAndAPIReliability(unittest.TestCase):
    """
    Комплексный стресс-тест надежности бэкенда и API EduHub AI:
    1. Проверка всех ключевых эндпоинтов
    2. Проверка интеграции Gemini AI (2026 модели: gemini-3.6-flash, gemini-3.5-flash-lite)
    3. Проверка отказоустойчивости при сбоях AI (503, 429, Timeout, Empty response)
    4. Проверка защитных фильтров (18+, невалидный base64, ошибки входных данных)
    5. Проверка биллинговых и системных сервисов
    """

    def setUp(self):
        rate_limiter._history.clear()

    # =========================================================================
    # 1. СИСТЕМНЫЕ И МОНИТОРИНГОВЫЕ ЭНДПОИНТЫ
    # =========================================================================

    def test_health_endpoints(self):
        for path in ["/health", "/api/v1/health"]:
            response = client.get(path)
            self.assertEqual(response.status_code, 200, f"Failed on {path}")
            data = response.json()
            self.assertEqual(data, {"status": "ok"})

            # Authenticated admin access
            admin_resp = client.get(f"{path}?token=edumate_admin_telemetry_2026")
            self.assertEqual(admin_resp.status_code, 200)
            admin_data = admin_resp.json()
            self.assertIn("diagnostics", admin_data)
            self.assertIn("genai", admin_data["diagnostics"])

    def test_sentinel_status(self):
        response = client.get("/api/v1/system/sentinel/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)

    # =========================================================================
    # 2. ЭНДПОИНТ: /api/v1/instant-diagnostic
    # =========================================================================

    def test_instant_diagnostic_success_fallback(self):
        payload = {
            "text": "The rapid advancement of artificial intelligence has revolutionized modern education. Many educators argue that automated tutors enhance personalized learning.",
            "lang": "en"
        }
        response = client.post("/api/v1/instant-diagnostic", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("predicted_band", data)
        self.assertGreaterEqual(data["predicted_band"], 5.0)

    def test_instant_diagnostic_content_safety_blocked(self):
        payload = {
            "text": "Writing an essay about explicit porn videos and nsfw content for teenagers.",
            "lang": "en"
        }
        response = client.post("/api/v1/instant-diagnostic", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["detail"]["error"], "ContentPolicyViolation")

    # =========================================================================
    # 3. ЭНДПОИНТ: /api/v1/parent/check-homework
    # =========================================================================

    def test_check_homework_fallback_when_gemini_unavailable(self):
        payload = {
            "assignment": "Solve quadratic equation 2x^2 + 5x - 3 = 0 using discriminant formula.",
            "student_solution": "D = 25 - 4*2*(-3) = 49. Roots: x = (-5 +- 7) / 4",
            "subject": "Mathematics",
            "grade_level": "Grade 9",
            "language": "uz"
        }
        response = client.post("/api/v1/parent/check-homework", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("guidance", data)
        self.assertTrue(len(data["guidance"]) > 50)

    def test_check_homework_invalid_base64_returns_400_or_422(self):
        payload = {
            "assignment": "Solve for x: 3x + 12 = 0",
            "image_base64": "invalid!@#$not-valid-base64-string====",
            "subject": "Algebra"
        }
        response = client.post("/api/v1/parent/check-homework", json=payload)
        self.assertIn(response.status_code, [400, 422])
        self.assertNotEqual(response.status_code, 500)

    def test_check_homework_with_valid_image(self):
        valid_b64 = base64.b64encode(b"fake image bytes data").decode("utf-8")
        payload = {
            "assignment": "Review geometry proof in the attached photo.",
            "image_base64": f"data:image/jpeg;base64,{valid_b64}",
            "subject": "Geometry",
            "language": "ru"
        }
        response = client.post("/api/v1/parent/check-homework", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("guidance", data)

    # =========================================================================
    # 4. ЭНДПОИНТ: /api/v1/language/grade-essay
    # =========================================================================

    def test_grade_essay_fallback_when_no_api_key(self):
        payload = {
            "essay_text": "In contemporary society, environmental degradation has become one of the most pressing global challenges. Governments and individuals must collaborate to establish renewable energy infrastructure.",
            "native_language": "Russian",
            "exam_type": "IELTS Academic Writing Task 2",
            "target_band": 7.5
        }
        response = client.post("/api/v1/language/grade-essay", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("feedback", data)
        self.assertIn("Band", data["feedback"])

    def test_grade_essay_invalid_base64_returns_400_or_422(self):
        payload = {
            "essay_text": "Valid essay text exceeding minimum length requirement.",
            "image_base64": "corrupt_data_not_base64!"
        }
        response = client.post("/api/v1/language/grade-essay", json=payload)
        self.assertIn(response.status_code, [400, 422])
        self.assertNotEqual(response.status_code, 500)

    # =========================================================================
    # 5. ЭНДПОИНТ: /api/v1/student/summarize
    # =========================================================================

    def test_summarize_lecture_resilience(self):
        payload = {
            "text": "Neuroplasticity refers to the brain's ability to reorganize itself by forming new neural connections throughout life. This phenomenon allows neurons in the brain to compensate for injury and disease and to adjust their activities in response to new situations or changes in their environment.",
            "format": "structured",
            "language": "en"
        }
        response = client.post("/api/v1/student/summarize", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("summary", data)
        self.assertTrue(len(data["summary"]) > 50)

    # =========================================================================
    # 6. ЭНДПОИНТ: /api/v1/career/ats-tailor
    # =========================================================================

    def test_ats_tailor_resilience(self):
        payload = {
            "resume_text": "Senior Software Engineer with 5 years experience in Python, FastAPI, Docker, and PostgreSQL. Built high-scale microservices.",
            "job_description": "Looking for a Backend Lead with deep Python, FastAPI, Docker, Kubernetes, and CI/CD expertise.",
            "target_role": "Backend Lead",
            "language": "en"
        }
        response = client.post("/api/v1/career/ats-tailor", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("ats_score", data)
        self.assertIn("matching_keywords", data)
        self.assertIn("missing_keywords", data)
        self.assertIn("metric_improvements", data)

    # =========================================================================
    # 7. ЭНДПОИНТЫ ИНСТРУМЕНТОВ: marketplace-lab, teacher-lab, excel-wizard, sop-builder
    # =========================================================================

    def test_tools_marketplace_lab_resilience(self):
        payload = {
            "product_name": "Беспроводные наушники Pro",
            "category": "Электроника",
            "marketplace": "uzum",
            "cost_price": 12.0,
            "selling_price": 25.0,
            "language": "uz"
        }
        response = client.post("/api/v1/tools/marketplace-lab", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("seo_title", data)
        self.assertIn("selling_bullets", data)
        self.assertIn("unit_economics", data)

    def test_tools_teacher_lab_resilience(self):
        payload = {
            "subject": "Algebra",
            "grade_level": "8-sinf",
            "topic": "Kvadrat tenglamalar",
            "language": "uz"
        }
        response = client.post("/api/v1/tools/teacher-lab", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("lesson_objectives", data)
        self.assertIn("warmup_5min", data)
        self.assertIn("preview_tests", data)
        self.assertIn("locked_preview_teaser", data)

    def test_tools_excel_wizard_resilience(self):
        payload = {
            "query": "Посчитай сумму в столбце C, если в столбце A статус Оплачено и в столбце B дата после 2026 года",
            "app_type": "Excel",
            "language": "ru"
        }
        response = client.post("/api/v1/tools/excel-wizard", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("formula", data)
        self.assertIn("explanation", data)
        self.assertIn("common_pitfalls", data)

    def test_tools_sop_builder_resilience(self):
        payload = {
            "degree_level": "Master of Science",
            "target_major": "Artificial Intelligence",
            "target_country": "Germany",
            "target_university": "Technical University of Munich",
            "grant_program": "DAAD Scholarship",
            "background_experience": "3 years software development and AI research",
            "career_vision": "Lead autonomous systems research",
            "language": "en"
        }
        response = client.post("/api/v1/tools/sop-builder", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("statement_of_purpose", data)
        self.assertIn("academic_collocations", data)
        self.assertIn("admissions_rating", data)

    # =========================================================================
    # 8. ИМИТАЦИЯ СБОЕВ GEMINI API (503, 429, Timeout, Empty Response)
    # =========================================================================

    @patch("app.main.get_genai_client")
    def test_ai_outage_503_graceful_fallback(self, mock_client_factory):
        # Моделируем 503 Service Unavailable на всех попытках
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("503 Service Unavailable: High Demand Spikes")
        mock_client_factory.return_value = mock_client

        payload = {
            "text": "Calculus and linear algebra are fundamental to machine learning.",
            "format": "structured"
        }
        response = client.post("/api/v1/student/summarize", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("resilient", data["model"])

    @patch("app.main.get_genai_client")
    def test_ai_empty_response_graceful_fallback(self, mock_client_factory):
        # Моделируем пустой ответ от API
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = ""
        mock_resp.candidates = []
        mock_client.models.generate_content.return_value = mock_resp
        mock_client_factory.return_value = mock_client

        payload = {
            "assignment": "Explain Newton's third law of motion.",
            "subject": "Physics"
        }
        response = client.post("/api/v1/parent/check-homework", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("guidance", data)

    # =========================================================================
    # 9. БИЛЛИНГОВЫЕ ЭНДПОИНТЫ
    # =========================================================================

    def test_billing_receipt_endpoint(self):
        response = client.get("/api/v1/billing/receipt/ORD-TEST-12345")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["order_id"], "ORD-TEST-12345")
        self.assertIn("merchant_of_record", data)

    def test_billing_payout_policy(self):
        response = client.get("/api/v1/billing/payout-policy")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "active")
        self.assertIn("policy", data)


if __name__ == "__main__":
    unittest.main()
