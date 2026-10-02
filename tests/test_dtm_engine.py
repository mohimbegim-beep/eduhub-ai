import unittest
from services.dtm_engine import DTMEngine, DTM_QUESTION_BANK

class TestDTMEngine(unittest.TestCase):

    def test_get_questions(self):
        all_qs = DTMEngine.get_questions()
        self.assertGreaterEqual(len(all_qs), 5)
        math_qs = DTMEngine.get_questions("matematika_mandatory")
        self.assertTrue(all(q["subject"] == "matematika_mandatory" for q in math_qs))

    def test_evaluate_perfect_score(self):
        # All correct answers
        perfect_answers = {q["id"]: q["correct_index"] for q in DTM_QUESTION_BANK}
        res = DTMEngine.evaluate_answers(perfect_answers)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["score_dtm_189"], 189.0)
        self.assertEqual(res["correct_answers"], len(DTM_QUESTION_BANK))
        self.assertIn("Бюджет", res["admission_prediction"])

    def test_evaluate_weak_topics_and_7day_plan(self):
        # Wrong answers to test weak topics and plan generation
        wrong_answers = {q["id"]: (q["correct_index"] + 1) % 4 for q in DTM_QUESTION_BANK}
        res = DTMEngine.evaluate_answers(wrong_answers)
        self.assertEqual(res["score_dtm_189"], 0.0)
        self.assertGreaterEqual(len(res["weak_topics"]), 1)
        self.assertEqual(len(res["revision_plan_7_days"]), 7)

if __name__ == "__main__":
    unittest.main()
