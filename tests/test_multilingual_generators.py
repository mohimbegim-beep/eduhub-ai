import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

LANGUAGES = ["uz", "en", "es", "ru"]
FORBIDDEN_UZ_WORDS = ["asbob", "instrument"]
FORBIDDEN_PRIVACY_TERMS = [
    "водное право",
    "водного законодательства",
    "кодекс республики узбекистан об охране и использовании вод",
    "эколого-правового подхода к исследуемому институту",
    "water law",
    "suv huquqi"
]

def assert_quality_and_privacy_gates(text: str, lang: str):
    if lang == "uz":
        text_lower = text.lower()
        for forbidden in FORBIDDEN_UZ_WORDS:
            assert forbidden not in text_lower, f"Quality Gate 2 violation: found forbidden word '{forbidden}' in Uzbek output:\n{text[:300]}"
    
    text_lower = text.lower()
    for forbidden in FORBIDDEN_PRIVACY_TERMS:
        assert forbidden not in text_lower, f"Privacy Gate violation: found sensitive term '{forbidden}' in output:\n{text[:300]}"

def test_marketplace_lab_multilingual():
    for lang in LANGUAGES:
        payload = {
            "product_name": "Ergonomic Office Chair",
            "category": "Furniture",
            "marketplace": "uzum",
            "cost_price": 50.0,
            "selling_price": 120.0,
            "key_features": "Mesh back, lumbar support, 360 swivel",
            "language": lang
        }
        res = client.post("/api/v1/tools/marketplace-lab", json=payload)
        assert res.status_code == 200, f"Failed for lang {lang}: {res.text}"
        data = res.json()
        assert "seo_title" in data
        assert "selling_bullets" in data
        assert len(data["selling_bullets"]) >= 3
        
        full_content = " ".join([data["seo_title"]] + data["selling_bullets"] + [data.get("description", "")])
        assert_quality_and_privacy_gates(full_content, lang)

def test_sop_builder_multilingual():
    for lang in LANGUAGES:
        payload = {
            "degree_level": "masters",
            "target_major": "Computer Science",
            "target_country": "Germany",
            "target_university": "TU Munich",
            "grant_program": "DAAD",
            "background_experience": "Software engineering honors graduate with ML publications",
            "career_vision": "Architect scalable AI systems for global education accessibility",
            "language": lang
        }
        res = client.post("/api/v1/tools/sop-builder", json=payload)
        assert res.status_code == 200, f"Failed for lang {lang}: {res.text}"
        data = res.json()
        assert "statement_of_purpose" in data
        assert len(data["statement_of_purpose"]) > 50
        assert_quality_and_privacy_gates(data["statement_of_purpose"], lang)

def test_excel_wizard_multilingual():
    for lang in LANGUAGES:
        payload = {
            "query": "Find the average revenue for sales above 1000",
            "app_type": "excel",
            "language": lang
        }
        res = client.post("/api/v1/tools/excel-wizard", json=payload)
        assert res.status_code == 200, f"Failed for lang {lang}: {res.text}"
        data = res.json()
        assert "formula" in data
        assert "explanation" in data
        full_expl = " ".join(data["explanation"])
        assert_quality_and_privacy_gates(full_expl, lang)

def test_teacher_lab_multilingual():
    for lang in LANGUAGES:
        payload = {
            "subject": "Physics",
            "grade_level": "10",
            "topic": "Newton's Laws of Motion",
            "language": lang
        }
        res = client.post("/api/v1/tools/teacher-lab", json=payload)
        assert res.status_code == 200, f"Failed for lang {lang}: {res.text}"
        data = res.json()
        assert "lesson_objectives" in data
        assert len(data["lesson_objectives"]) >= 2
        full_text = " ".join(data["lesson_objectives"])
        if "diagnostic_preview_tests" in data:
            for q in data["diagnostic_preview_tests"]:
                full_text += " " + q.get("question", "") + " " + q.get("explanation", "")
        assert_quality_and_privacy_gates(full_text, lang)

def test_career_orientate_multilingual():
    for lang in LANGUAGES:
        payload = {
            "stage": "student",
            "energy_type": "logic",
            "problem_solving": "analytical",
            "dream_lifestyle": "flexible",
            "income_priority": "high",
            "favourite_subjects": "Mathematics and Computer Science",
            "language": lang
        }
        res = client.post("/api/v1/career/orientate", json=payload)
        assert res.status_code == 200, f"Failed for lang {lang}: {res.text}"
        data = res.json()
        assert data.get("status") == "success"
        # Support both schemas
        assert "archetype" in data or ("result" in data and "archetype" in data["result"])
        profile = data.get("result", data)
        assert len(profile.get("top_careers", profile.get("top_professions", []))) >= 1
        full_text = profile.get("personality_summary", "") + " " + profile.get("superpower", "")
        assert_quality_and_privacy_gates(full_text, lang)

def test_parent_check_homework_multilingual():
    for lang in LANGUAGES:
        payload = {
            "assignment": "Solve the quadratic equation: x^2 - 5x + 6 = 0",
            "student_solution": "x = 2 and x = 3",
            "subject": "Algebra",
            "grade_level": "8",
            "guidance_style": "pedagogical",
            "language": lang
        }
        res = client.post("/api/v1/parent/check-homework", json=payload)
        assert res.status_code == 200, f"Failed for lang {lang}: {res.text}"
        data = res.json()
        assert "guidance" in data
        assert len(data["guidance"]) > 30
        assert_quality_and_privacy_gates(data["guidance"], lang)

def test_academic_research_compose_multilingual():
    modes = ["outline", "apparatus", "article_vak", "chapter", "defense_speech"]
    for lang in LANGUAGES:
        for mode in modes:
            payload = {
                "topic": "Machine Learning in Algorithmic Trading",
                "level": "masters_dissertation",
                "mode": mode,
                "discipline": "Computer Science & Quantitative Finance",
                "language": lang
            }
            res = client.post("/api/v1/academic/research-compose", json=payload)
            assert res.status_code == 200, f"Failed for {mode} in {lang}: {res.text}"
            data = res.json()
            assert "content" in data
            assert len(data["content"]) > 50
            assert_quality_and_privacy_gates(data["content"], lang)

def test_ats_tailor_multilingual():
    for lang in LANGUAGES:
        payload = {
            "job_description": "We are seeking a Senior Full-Stack Engineer with strong Python, FastAPI, and Docker experience.",
            "resume_text": "Experienced Software Engineer skilled in Python, FastAPI, Docker, and REST APIs with 5 years experience.",
            "target_role": "Senior Full-Stack Engineer",
            "language": lang
        }
        res = client.post("/api/v1/career/ats-tailor", json=payload)
        assert res.status_code == 200, f"Failed for ats-tailor in {lang}: {res.text}"
        data = res.json()
        assert "ats_score" in data
        assert "match_verdict" in data
        assert "tailored_summary" in data
        full_text = data.get("match_verdict", "") + " " + data.get("key_findings", "") + " " + data.get("tailored_summary", "")
        assert_quality_and_privacy_gates(full_text, lang)

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("Running Multilingual Generators Test Suite...")
    test_marketplace_lab_multilingual()
    print("[PASS] test_marketplace_lab_multilingual")
    test_sop_builder_multilingual()
    print("[PASS] test_sop_builder_multilingual")
    test_excel_wizard_multilingual()
    print("[PASS] test_excel_wizard_multilingual")
    test_teacher_lab_multilingual()
    print("[PASS] test_teacher_lab_multilingual")
    test_career_orientate_multilingual()
    print("[PASS] test_career_orientate_multilingual")
    test_parent_check_homework_multilingual()
    print("[PASS] test_parent_check_homework_multilingual")
    test_academic_research_compose_multilingual()
    print("[PASS] test_academic_research_compose_multilingual")
    test_ats_tailor_multilingual()
    print("[PASS] test_ats_tailor_multilingual")
    print("\n[SUCCESS] ALL MULTILINGUAL GENERATOR TESTS PASSED WITH 100% SUCCESS!")



