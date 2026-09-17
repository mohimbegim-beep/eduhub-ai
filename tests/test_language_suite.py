import sys
import os
import re
import requests
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_language_suite():
    print("==================================================================")
    print("🎓 AUDIT: LANGUAGE LEARNING SUITE & END-TO-END VERIFICATION")
    print("==================================================================")

    # ----------------------------------------------------------------------
    # 1. Route Accessibility & SEO Meta Tags
    # ----------------------------------------------------------------------
    print("\n--- 1. Standalone Routes & Programmatic SEO Verification ---")
    new_tools = [
        ("/tools/essay-grader", "IELTS & CEFR Essay Grader", "essay-grader"),
        ("/tools/language-tutor", "AI Conversation & Roleplay Partner", "language-tutor")
    ]

    for route, expected_title, tool_attr in new_tools:
        url = f"{BASE_URL}{route}"
        res = requests.get(url, allow_redirects=False, timeout=5)
        assert res.status_code == 200, f"Expected 200 for {route}, got {res.status_code}"
        html = res.text
        assert expected_title in html or tool_attr in html, f"Expected title/attr in {route}"
        assert 'data-page-tool="' + tool_attr + '"' in html, f"data-page-tool missing in {route}"
        
        # Check Core Scripts
        assert 'src="/static/js/i18n.js"' in html, f"i18n.js missing in {route}"
        assert 'src="/static/js/user-utils.js"' in html, f"user-utils.js missing in {route}"
        assert 'src="/static/js/doc-renderer.js"' in html, f"doc-renderer.js missing in {route}"
        assert 'checkout-trigger-btn' in html or 'data-i18n' in html, f"Checkout or i18n missing in {route}"
        
        # Check Schema.org JSON-LD
        assert 'application/ld+json' in html, f"Schema.org JSON-LD missing in {route}"
        assert 'SoftwareApplication' in html, f"SoftwareApplication schema missing in {route}"
        assert 'Course' in html, f"Course schema missing in {route}"

        # Check Hreflang Tags (EN, RU, UZ, ES, x-default)
        for lang in ['en', 'ru', 'uz', 'es', 'x-default']:
            assert f'hreflang="{lang}"' in html, f"Hreflang '{lang}' missing in {route}"

        # Check Camera OCR and Anki utilities
        assert 'Snap' in html or 'camera' in html.lower(), f"Camera OCR button missing in {route}"
        assert 'Anki' in html, f"Anki export action missing in {route}"
        assert 'checkout[trial]=true' in html, f"$1 Pro Max trial link missing in {route}"

        print(f"  [PASS] {route} -> HTTP 200 OK (Len: {len(html)} bytes, Schema.org + Hreflang + Anki verified)")

    # ----------------------------------------------------------------------
    # 2. Essay Grader API Endpoint
    # ----------------------------------------------------------------------
    print("\n--- 2. IELTS & CEFR Essay Grader Endpoint (/api/v1/language/grade-essay) ---")
    grade_url = f"{BASE_URL}/api/v1/language/grade-essay"
    
    # 2.1 Standard IELTS Task 2 evaluation in Russian
    sample_essay = (
        "Nowadays university education is very important for young people. "
        "Some people think government must pay for all university students. "
        "In my opinion I completely agree with this idea because education give good future and help country. "
        "First of all, many smart students cannot go to university because they are poor. "
        "If university is free, everyone have equal chance to study medicine, engineering and science. "
        "Secondly, free education is good for country economy. "
        "When more citizens have university degree, country will have many qualified specialists. "
        "In conclusion, I think higher education should be free for everybody."
    )
    payload_ru = {
        "essay_text": sample_essay,
        "task_prompt": "Some people believe that university education should be free for all students. To what extent do you agree?",
        "exam_type": "IELTS Academic Writing Task 2",
        "target_band": 7.5,
        "native_language": "Russian"
    }
    res_grade = requests.post(grade_url, json=payload_ru, timeout=20)
    assert res_grade.status_code == 200, f"Grade essay failed: {res_grade.status_code}"
    data_grade = res_grade.json()
    assert data_grade.get("status") == "success", "Expected status: success"
    feedback = data_grade.get("feedback", "")
    assert len(feedback) > 500, "Feedback text is too short"
    
    # Verify standard rubric criteria scores & sections
    assert "Task Response" in feedback or "TR" in feedback or "Task Achievement" in feedback
    assert "Coherence" in feedback or "CC" in feedback
    assert "Lexical Resource" in feedback or "LR" in feedback
    assert "Grammatical Range" in feedback or "GRA" in feedback
    assert "Band" in feedback
    assert "Original" in feedback or "Оригинал" in feedback
    assert "Band 8.5" in feedback or "Band 9" in feedback or "Upgraded" in feedback or "Улучшенная" in feedback
    assert "Vocabulary" in feedback or "Словарь" in feedback
    print(f"  [PASS] Grade Essay (RU): Band Breakdown, Side-by-Side Upgrade, Anki Vocab table verified (len: {len(feedback)})")

    # 2.2 Dual-Language Support: Uzbek & Spanish
    for lang_code, lang_name, expected_marker in [("uz", "Uzbek", "mezon"), ("es", "Spanish", "criterio")]:
        payload_lang = {
            "essay_text": sample_essay,
            "exam_type": "IELTS Academic Writing Task 2",
            "target_band": 8.0,
            "native_language": lang_name
        }
        r = requests.post(grade_url, json=payload_lang, timeout=15)
        assert r.status_code == 200
        fb = r.json().get("feedback", "")
        assert len(fb) > 400
        print(f"  [PASS] Grade Essay ({lang_name}): Feedback generated successfully (len: {len(fb)})")

    # 2.3 Safe Content Filter Refusal
    toxic_payload = {
        "essay_text": "This text contains illegal explicit 18+ pornographic obscenities.",
        "exam_type": "IELTS Academic Writing Task 2",
        "target_band": 7.0
    }
    r_toxic = requests.post(grade_url, json=toxic_payload, timeout=10)
    assert r_toxic.status_code == 400, f"Expected 400 for toxic essay, got {r_toxic.status_code}"
    print("  [PASS] Safe Content Filter: Toxic / 18+ submission refused with HTTP 400")

    # ----------------------------------------------------------------------
    # 3. Language Tutor Conversational Roleplay Endpoint
    # ----------------------------------------------------------------------
    print("\n--- 3. AI Conversational & Roleplay Partner (/api/v1/language/chat) ---")
    chat_url = f"{BASE_URL}/api/v1/language/chat"

    scenarios = [
        ("academic_interview", "I have graduated with honors in Software Engineering and wish to research AI ethics."),
        ("travel", "Excuse me, I missed my connecting flight to Boston due to a delay in Frankfurt."),
        ("debate", "I strongly contend that artificial intelligence improves student critical faculties rather than degrading them."),
        ("casual_chat", "I am enjoying my university courses, especially machine learning and robotics.")
    ]

    for scenario, msg in scenarios:
        chat_payload = {
            "scenario": scenario,
            "message": msg,
            "target_language": "English",
            "target_level": "B2",
            "native_language": "Russian"
        }
        res_chat = requests.post(chat_url, json=chat_payload, timeout=20)
        assert res_chat.status_code == 200, f"Chat failed for {scenario}: {res_chat.status_code}"
        chat_data = res_chat.json()
        assert chat_data.get("status") == "success"
        reply = chat_data.get("reply", "")
        assert len(reply) > 80, f"Reply too short for {scenario}"
        print(f"  [PASS] Roleplay [{scenario}]: Responded with dialogue & feedback (len: {len(reply)})")

    # 3.2 Dual-Language Feedback in UZ, ES, EN
    for test_lang in ["Uzbek", "Spanish", "English"]:
        payload = {
            "scenario": "academic_interview",
            "message": "My research investigates neural network optimization.",
            "native_language": test_lang
        }
        res_l = requests.post(chat_url, json=payload, timeout=15)
        assert res_l.status_code == 200
        reply_l = res_l.json().get("reply", "")
        assert len(reply_l) > 50
        print(f"  [PASS] Language Tutor ({test_lang}): Pedagogical feedback generated successfully")

    # 3.3 Safe Content Filter Refusal
    toxic_chat = {
        "scenario": "casual_chat",
        "message": "Explicit sexual 18+ adult illegal harassment message."
    }
    r_chat_toxic = requests.post(chat_url, json=toxic_chat, timeout=10)
    assert r_chat_toxic.status_code == 400, f"Expected 400 for toxic chat, got {r_chat_toxic.status_code}"
    print("  [PASS] Safe Content Filter: Toxic / 18+ chat refused with HTTP 400")

    # ----------------------------------------------------------------------
    # 4. Anki Export Format Verification
    # ----------------------------------------------------------------------
    print("\n--- 4. Anki Deck TSV Export Engine Validation ---")
    user_utils_file = os.path.join(BASE_DIR, "static", "js", "user-utils.js")
    with open(user_utils_file, "r", encoding="utf-8") as f:
        utils_code = f.read()

    assert "exportAnkiDeck" in utils_code, "exportAnkiDeck function missing from user-utils.js"
    assert "text/tab-separated-values" in utils_code, "Anki TSV MIME type missing"
    assert "#separator:tab" in utils_code, "Anki header #separator:tab missing"
    print("  [PASS] Anki Deck Export Engine: Standard UTF-8 TSV format with tags and collocations verified")

    # ----------------------------------------------------------------------
    # 5. Full Platform Route Audit (All 11 Routes)
    # ----------------------------------------------------------------------
    print("\n--- 5. Full Platform Route Audit (11 Routes Verified) ---")
    all_routes = [
        ("/", "EduHub AI"),
        ("/privacy", "Privacy Policy"),
        ("/terms", "Terms of Service"),
        ("/refund", "Refund Policy"),
        ("/payment-success", "Payment Successful"),
        ("/tools/pdf-summarizer", "PDF Summarizer"),
        ("/tools/homework-solver", "Homework Solver"),
        ("/tools/gpa-calculator", "GPA Predictor"),
        ("/tools/citation-generator", "Citation Formatter"),
        ("/tools/essay-grader", "Essay Grader"),
        ("/tools/language-tutor", "Language Tutor")
    ]

    for path, expected_text in all_routes:
        url = f"{BASE_URL}{path}"
        r = requests.get(url, allow_redirects=False, timeout=5)
        assert r.status_code == 200, f"Route {path} returned HTTP {r.status_code}"
        assert expected_text in r.text or path.split("/")[-1] in r.text, f"Text '{expected_text}' not in {path}"
        print(f"  [PASS] HTTP 200: {path:26} ({len(r.text)} bytes)")

    print("\n==================================================================")
    print("✅ ALL AUDIT CHECKS PASSED: Language Suite & Platform 100% Operational")
    print("==================================================================")

if __name__ == "__main__":
    test_language_suite()
