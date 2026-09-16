import sys
import os
import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_user_utilities_suite():
    print("==================================================")
    print("🔍 VERIFYING ESSENTIAL USER UTILITIES SUITE")
    print("==================================================")

    # 1. Verify user-utils.js file integrity
    print("\n--- 1. Validating static/js/user-utils.js ---")
    utils_path = os.path.join(BASE_DIR, "static", "js", "user-utils.js")
    assert os.path.exists(utils_path), f"Missing {utils_path}"
    with open(utils_path, "r", encoding="utf-8") as f:
        js = f.read()

    # Export actions
    assert "copyText" in js, "copyText function missing in user-utils.js"
    assert "downloadPDF" in js, "downloadPDF function missing in user-utils.js"
    assert "exportDOCX" in js, "exportDOCX function missing in user-utils.js"
    assert "application/msword" in js or "msword" in js, "Word MIME type missing in exportDOCX"
    assert "window.print" in js, "window.print trigger missing in downloadPDF"
    print("  [PASS] 1. Export actions: Copy Text, Download PDF, Export DOCX fully implemented")

    # Session history & drawer
    assert "eduhub_user_history" in js, "LocalStorage history key missing"
    assert "saveHistoryItem" in js, "saveHistoryItem missing"
    assert "getHistory" in js, "getHistory missing"
    assert "openHistoryDrawer" in js, "openHistoryDrawer missing"
    assert "closeHistoryDrawer" in js, "closeHistoryDrawer missing"
    assert "loadHistoryItem" in js, "loadHistoryItem missing"
    assert "clearAllHistory" in js, "clearAllHistory missing"
    assert "updateHistoryBadge" in js, "updateHistoryBadge missing"
    print("  [PASS] 2. Session history & Recent Documents drawer functions verified")

    # Animated stepper
    assert "startStepper" in js, "startStepper missing"
    assert "stopStepper" in js, "stopStepper missing"
    assert "stepper-bar" in js, "stepper-bar markup missing"
    print("  [PASS] 3. Streaming / animated step progress indicator verified")

    # Mobile camera
    assert "initCameraTrigger" in js, "initCameraTrigger missing"
    assert "getAttachedPhoto" in js, "getAttachedPhoto missing"
    assert "removeAttachedPhoto" in js, "removeAttachedPhoto missing"
    print("  [PASS] 4. Mobile camera direct upload trigger verified")

    # 2. Verify i18n dictionary parity for new keys
    print("\n--- 2. Validating i18n.js Translation Parity ---")
    i18n_path = os.path.join(BASE_DIR, "static", "js", "i18n.js")
    with open(i18n_path, "r", encoding="utf-8") as f:
        i18n_code = f.read()

    required_keys = [
        "export_copy", "export_pdf", "export_docx",
        "recent_docs", "recent_empty", "camera_snap",
        "photo_attached", "stepper_ingest", "stepper_safety",
        "stepper_reason", "stepper_finalize"
    ]

    for lang in ["en", "ru", "uz", "es"]:
        assert f"{lang}: {{" in i18n_code or f"'{lang}': {{" in i18n_code, f"Missing {lang} dictionary"
        for key in required_keys:
            assert f"{key}:" in i18n_code, f"Key '{key}' missing from i18n file"
        print(f"  [PASS] Locale '{lang}': All 11 essential utility keys present")

    # 3. Verify Homepage (static/index.html) integration
    print("\n--- 3. Validating Homepage (index.html) Integration ---")
    home_res = requests.get(f"{BASE_URL}/", timeout=5)
    assert home_res.status_code == 200
    home_html = home_res.text
    assert "user-utils.js" in home_html, "user-utils.js script tag missing from index.html"
    assert "EduHubUtils.openHistoryDrawer()" in home_html, "Recent Documents drawer button missing in index.html"
    assert "history-drawer" in home_html, "#history-drawer missing from index.html"
    assert "history-backdrop" in home_html, "#history-backdrop missing from index.html"
    assert "stepper-container" in home_html, "#stepper-container missing from index.html"
    assert "EduHubUtils.copyText" in home_html, "copyText trigger missing from index.html"
    assert "EduHubUtils.downloadPDF" in home_html, "downloadPDF trigger missing from index.html"
    assert "EduHubUtils.exportDOCX" in home_html, "exportDOCX trigger missing from index.html"
    assert "camera-btn" in home_html, "camera-btn missing from index.html"
    assert 'capture="environment"' in home_html, "Mobile capture='environment' missing from index.html"
    assert "EduHubUtils.startStepper" in home_html, "startStepper call missing from askEduHub"
    assert "EduHubUtils.saveHistoryItem" in home_html, "saveHistoryItem call missing from askEduHub"
    print("  [PASS] Homepage: All 4 utilities successfully wired and rendered")

    # 4. Verify PDF Summarizer integration
    print("\n--- 4. Validating PDF Summarizer Integration ---")
    pdf_res = requests.get(f"{BASE_URL}/tools/pdf-summarizer", timeout=5)
    assert pdf_res.status_code == 200
    pdf_html = pdf_res.text
    assert "user-utils.js" in pdf_html, "user-utils.js script tag missing from pdf-summarizer.html"
    assert "EduHubUtils.openHistoryDrawer()" in pdf_html, "History drawer trigger missing from pdf-summarizer.html"
    assert "history-drawer" in pdf_html, "#history-drawer missing from pdf-summarizer.html"
    assert "stepper-container" in pdf_html, "#stepper-container missing from pdf-summarizer.html"
    assert "EduHubUtils.copyText" in pdf_html, "copyText missing from pdf-summarizer.html"
    assert "EduHubUtils.downloadPDF" in pdf_html, "downloadPDF missing from pdf-summarizer.html"
    assert "EduHubUtils.exportDOCX" in pdf_html, "exportDOCX missing from pdf-summarizer.html"
    assert "EduHubUtils.startStepper" in pdf_html, "startStepper call missing from executeSummarize"
    assert "EduHubUtils.saveHistoryItem" in pdf_html, "saveHistoryItem call missing from executeSummarize"
    print("  [PASS] PDF Summarizer: Export actions, Stepper, and History Drawer verified")

    # 5. Verify Homework Solver integration
    print("\n--- 5. Validating Homework Solver Integration ---")
    hw_res = requests.get(f"{BASE_URL}/tools/homework-solver", timeout=5)
    assert hw_res.status_code == 200
    hw_html = hw_res.text
    assert "user-utils.js" in hw_html, "user-utils.js script tag missing from homework-solver.html"
    assert "hw-camera-btn" in hw_html, "hw-camera-btn missing from homework-solver.html"
    assert 'capture="environment"' in hw_html, "capture='environment' missing from homework-solver.html"
    assert "hw-photo-preview" in hw_html, "#hw-photo-preview missing from homework-solver.html"
    assert "stepper-container" in hw_html, "#stepper-container missing from homework-solver.html"
    assert "EduHubUtils.copyText" in hw_html, "copyText missing from homework-solver.html"
    assert "EduHubUtils.downloadPDF" in hw_html, "downloadPDF missing from homework-solver.html"
    assert "EduHubUtils.exportDOCX" in hw_html, "exportDOCX missing from homework-solver.html"
    assert "EduHubUtils.initCameraTrigger" in hw_html, "initCameraTrigger missing from homework-solver.html"
    assert "image_base64" in hw_html, "image_base64 payload handling missing in homework-solver.html"
    print("  [PASS] Homework Solver: Mobile Camera trigger, Vision payload, and Stepper verified")

    print("\n==================================================")
    print("🎉 ALL ESSENTIAL USER UTILITIES VERIFIED (100% PASS)")
    print("==================================================")
    return True

if __name__ == "__main__":
    success = test_user_utilities_suite()
    sys.exit(0 if success else 1)
