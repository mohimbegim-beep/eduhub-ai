import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)

class TestDTMAndSpeakingAPI(unittest.TestCase):

    def test_dtm_questions_api(self):
        resp = client.get("/api/v1/dtm/questions")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "success")
        self.assertGreaterEqual(data.get("total", 0), 5)
        self.assertTrue(len(data.get("questions", [])) > 0)

    def test_dtm_evaluate_api(self):
        answers_payload = {
            "answers": {
                "dtm_math_01": 1,
                "dtm_math_02": 2,
                "dtm_lang_01": 0,
                "dtm_hist_01": 0,
                "dtm_math_spec_01": 0,
                "dtm_phys_spec_02": 1
            }
        }
        resp = client.post("/api/v1/dtm/evaluate", json=answers_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("score_dtm_189"), 189.0)
        self.assertEqual(len(data.get("revision_plan_7_days", [])), 7)

    def test_speaking_evaluate_api(self):
        speaking_payload = {
            "topic": "Describe an important academic milestone in your education.",
            "transcript": "I would like to talk about the time when I successfully passed my university entrance exams. It was a rigorous period requiring intensive preparation in mathematics and analytical problem solving. Moreover, I developed disciplined study habits.",
            "target_band": 7.5
        }
        resp = client.post("/api/v1/language/speaking-evaluate", json=speaking_payload)
        self.assertIn(resp.status_code, [200, 503])
        if resp.status_code == 200:
            data = resp.json()
            self.assertEqual(data.get("status"), "success")
            self.assertIn("overall_band", data)
            self.assertGreaterEqual(data.get("overall_band"), 5.0)
            self.assertIn("fluency_score", data)
            self.assertIn("lexical_score", data)
        else:
            data = resp.json()
            self.assertIn("detail", data)


    def test_dtm_page_served(self):
        resp = client.get("/dtm")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("DTM Imtihon Simulyatori", resp.text)

    def test_security_headers_present(self):
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("content-security-policy", resp.headers)
        self.assertIn("strict-transport-security", resp.headers)
        self.assertIn("x-content-type-options", resp.headers)
        self.assertEqual(resp.headers.get("x-frame-options"), "DENY")
        self.assertNotIn("server", resp.headers)

if __name__ == "__main__":
    unittest.main()
