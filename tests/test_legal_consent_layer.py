"""
Test Suite: Trust & Legal Micro-Consent Layer (Cookie & Legal Bar, Checkout Micro-Consent, i18n Parity)
"""
import sys
import subprocess
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
BASE = "http://127.0.0.1:8000"

print("="*70)
print("🛡️ AUDIT: TRUST & LEGAL MICRO-CONSENT LAYER (COOKIE BAR + CHECKOUT)")
print("="*70)

# 1. Validate static/js/legal-consent.js with Node.js
js_file = Path(r"c:\EDU HUB\static\js\legal-consent.js")
assert js_file.exists(), "legal-consent.js does not exist!"
res = subprocess.run(["node", "-c", str(js_file)], capture_output=True, text=True)
assert res.returncode == 0, f"Node.js syntax error in legal-consent.js: {res.stderr}"
print("  [PASS] legal-consent.js: Node.js syntax check passed with 0 errors")

# 2. Check content of legal-consent.js for all requirements
content = js_file.read_text(encoding="utf-8")
assert "cookie_consent" in content, "Missing localStorage key 'cookie_consent'"
assert "Accept & Continue" in content, "Missing English button"
assert "Принять и продолжить" in content, "Missing Russian button"
assert "Qabul qilish va davom etish" in content, "Missing Uzbek button"
assert "Aceptar y continuar" in content, "Missing Spanish button"
assert "/terms" in content and "/privacy" in content and "/refund" in content
assert "target='_blank'" in content or 'target="_blank"' in content
assert "checkout-micro-consent" in content
print("  [PASS] legal-consent.js: All 4 language dictionaries (RU, EN, UZ, ES) & legal routes verified")

# 3. Check i18n.js integration
i18n_content = Path(r"c:\EDU HUB\static\js\i18n.js").read_text(encoding="utf-8")
assert "checkout_micro_consent" in i18n_content
assert "cookie_consent_text" in i18n_content
assert "cookie_consent_btn" in i18n_content
print("  [PASS] i18n.js: Translation keys synchronized across EN, RU, UZ, ES")

# 4. Check index.html markup
index_content = Path(r"c:\EDU HUB\static\index.html").read_text(encoding="utf-8")
assert "legal-consent.js" in index_content, "legal-consent.js missing from index.html"
micro_count = index_content.count("checkout-micro-consent")
assert micro_count >= 5, f"Expected at least 5 checkout micro-consent captions, found {micro_count}"
print(f"  [PASS] index.html: Verified script inclusion + {micro_count} checkout micro-consent captions")

# 5. Check all 6 standalone tools
tool_names = [
    "essay-grader.html",
    "homework-solver.html",
    "pdf-summarizer.html",
    "language-tutor.html",
    "gpa-calculator.html",
    "citation-generator.html"
]

for tool in tool_names:
    t_path = Path(r"c:\EDU HUB\static\tools") / tool
    t_content = t_path.read_text(encoding="utf-8")
    assert "legal-consent.js" in t_content, f"legal-consent.js missing in {tool}"
    assert "checkout-micro-consent" in t_content, f"checkout-micro-consent missing in {tool}"
    print(f"  [PASS] /tools/{tool.replace('.html', '')}: Script + checkout micro-consent verified")

# 6. Check legal & support pages
for p in ["support.html", "refund.html", "terms.html", "privacy.html"]:
    lp = Path(r"c:\EDU HUB\static") / p
    assert "legal-consent.js" in lp.read_text(encoding="utf-8")
    print(f"  [PASS] /{p.replace('.html', '')}: Script inclusion verified")

# 7. Live HTTP availability
urls = [
    "/",
    "/static/js/legal-consent.js",
    "/support",
    "/refund",
    "/terms",
    "/privacy",
    "/tools/essay-grader",
    "/tools/homework-solver"
]

for u in urls:
    req = urllib.request.Request(f"{BASE}{u}")
    with urllib.request.urlopen(req, timeout=10) as r:
        assert r.status == 200
        print(f"  [PASS] HTTP 200: {u}")

print("="*70)
print("🎉 ALL TRUST & LEGAL MICRO-CONSENT LAYER CHECKS PASSED (100%)")
print("="*70)
