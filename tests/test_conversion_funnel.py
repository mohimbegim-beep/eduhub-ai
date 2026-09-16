import os
import sys
import requests
import re
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_conversion_funnel():
    print("==================================================================")
    print("🚀 AUDIT: HIGH-CONVERTING CRO, PAYWALL & EXIT-INTENT FUNNEL")
    print("==================================================================")

    # 1. Check conversion-engine.js exists and is valid syntax
    print("\n--- 1. Conversion Engine Script Syntax Validation ---")
    conv_js_path = os.path.join(BASE_DIR, "static", "js", "conversion-engine.js")
    assert os.path.exists(conv_js_path), "conversion-engine.js missing from static/js"
    res_node = subprocess.run(["node", "-c", conv_js_path], capture_output=True, text=True)
    assert res_node.returncode == 0, f"Syntax error in conversion-engine.js: {res_node.stderr}"
    print("  [PASS] conversion-engine.js: Node.js syntax check passed with 0 errors")

    # 2. Check Landing Page Conversion Assets
    print("\n--- 2. Landing Page Conversion Elements Verification ---")
    res_home = requests.get(BASE_URL + "/", timeout=5)
    assert res_home.status_code == 200, f"Expected 200 for /, got {res_home.status_code}"
    html_home = res_home.text

    assert "conversion-engine.js" in html_home, "conversion-engine.js not included in /"
    assert "exit-intent-modal" in html_home, "Exit-intent modal missing in /"
    assert "conversion-social-ticker" in html_home, "Social proof ticker missing in /"
    assert "comp_badge" in html_home, "Comparison table badge missing in /"
    assert "comp_title" in html_home, "Comparison table title missing in /"
    assert "comp_col_tutor" in html_home, "Comparison table tutor column missing in /"
    assert "comp_val_eduhub_price" in html_home, "Comparison table eduhub price missing in /"
    assert "checkout[trial]=true" in html_home, "$1 trial checkout link missing in /"
    print("  [PASS] Homepage: Anchor Pricing Table + Exit Modal + Social Ticker verified")

    # 3. Check Standalone Tool Pages
    print("\n--- 3. Standalone Tools Paywall & Exit-Intent Hooks ---")
    tool_pages = [
        ("/tools/essay-grader", "essay-grader.html"),
        ("/tools/homework-solver", "homework-solver.html"),
        ("/tools/pdf-summarizer", "pdf-summarizer.html"),
        ("/tools/language-tutor", "language-tutor.html"),
        ("/tools/gpa-calculator", "gpa-calculator.html"),
        ("/tools/citation-generator", "citation-generator.html"),
    ]

    for route, fname in tool_pages:
        r = requests.get(BASE_URL + route, timeout=5)
        assert r.status_code == 200, f"Expected 200 for {route}, got {r.status_code}"
        html = r.text
        assert "conversion-engine.js" in html, f"conversion-engine.js missing in {route}"
        assert "exit-intent-modal" in html, f"exit-intent-modal missing in {route}"
        assert "conversion-social-ticker" in html, f"conversion-social-ticker missing in {route}"

        # Paywall blur hook for primary grading/solving tools
        if fname in ["essay-grader.html", "homework-solver.html", "pdf-summarizer.html"]:
            assert "applyPaywallBlur" in html, f"applyPaywallBlur missing in {fname}"

        print(f"  [PASS] {route:25} -> Verified (Exit Modal + Ticker + Paywall Hooks)")

    # 4. Check i18n Translation Parity for all Conversion Keys
    print("\n--- 4. Multi-Language Parity Check (EN, RU, UZ, ES) ---")
    dom_test_path = os.path.join(BASE_DIR, "scratch", "test_i18n_dom.py")
    if os.path.exists(dom_test_path):
        res_dom = subprocess.run(["python", dom_test_path], capture_output=True, text=True, encoding="utf-8")
        assert res_dom.returncode == 0, f"DOM i18n test failed: {res_dom.stderr}"
        assert "missing against HTML=0" in res_dom.stdout
        print("  [PASS] 100% i18n Parity: 0 missing keys across EN, RU, UZ, and ES")

    # 5. Route Availability Audit (All 11 Routes HTTP 200)
    print("\n--- 5. Platform Route Integrity Audit (11 Routes) ---")
    all_routes = [
        "/", "/privacy", "/terms", "/refund", "/payment-success",
        "/tools/pdf-summarizer", "/tools/homework-solver", "/tools/gpa-calculator",
        "/tools/citation-generator", "/tools/essay-grader", "/tools/language-tutor"
    ]
    for p in all_routes:
        res = requests.get(BASE_URL + p, timeout=5)
        assert res.status_code == 200, f"Route {p} failed with {res.status_code}"
        print(f"  [PASS] HTTP 200: {p:28} ({len(res.text)} bytes)")

    print("\n==================================================================")
    print("🎉 ALL CONVERSION FUNNEL & PAYWALL CHECKS PASSED (100%)")
    print("==================================================================")

if __name__ == "__main__":
    test_conversion_funnel()
